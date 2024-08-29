// headless-service/src/utils/generate-pdf.tsx

import fs from "fs";
import path from "path";
import puppeteer from "puppeteer";
import { S3Client, PutObjectCommand } from "@aws-sdk/client-s3";
import React from "react";
import ReactDOMServer from "react-dom/server";
import { Request, Response } from "express";
import { getPresentationByID, getAllSlides } from "./dynamodb";
import { SlideComponent } from "../components/slide-component";
import { Slide } from "../../../frontend/src/utils/slide-types";
import logger from "./logger";
import { sanitizeFileName } from "./sanitize-file-name";
import { createSignedUrlSuffix } from "./create-signed-url-suffix";

const SAVE_TO_FILE = false;
const DEBUG = false;

export async function generatePDF(req: Request, res: Response) {
  const { presentationId } = req.params;
  const { theme, footnotes } = req.body;
  const themeClass = theme === "print" ? "nobg" : theme === "dark" ? "dark" : "";

  // error if theme is not "dark", "light" or "print"
  if (!["dark", "light", "print"].includes(theme)) {
    logger.info(`Received invalid theme: ${theme}`);
    res.status(400).send("Invalid theme, please use 'dark', 'light' or 'print'");
    return;
  }

  logger.info(`Received theme: ${theme}, footnotes: ${footnotes}`);

  try {
    const presentation = await getPresentationByID(presentationId, [
      "head_slide_id",
      "topic",
    ]);
    logger.info(`Fetched presentation`);

    if (!presentation.topic) {
      res
        .status(404)
        .send("Presentation not found, please check the presentation id");
      return;
    }

    if (!presentation.head_slide_id) {
      res.status(500).send("No head slide found for the presentation");
      return;
    }

    const unsortedSlidesArray = await getAllSlides(presentationId);
    logger.info(`Fetched unsorted slides`);

    if (!unsortedSlidesArray.length) {
      res
        .status(500)
        .send(
          "No slides found for the presentation though the presentation exists"
        );
      return;
    }

    let slidesMap: { [key: string]: Slide } = {};
    try {
      unsortedSlidesArray.forEach((slide: Slide) => {
        slidesMap[slide.id] = slide;
      });
      logger.info(`Converted slides to map`);
    } catch (error: any) {
      logger.error(
        `Failed to convert slides to linked list map: ${error.message}`
      );
      res
        .status(500)
        .send(`Failed to convert slides to linked list map: ${error.message}`);
      return;
    }

    let sortedSlidesArray = [];
    try {
      let currentId = presentation.head_slide_id;
      while (currentId) {
        const slide = slidesMap[currentId];
        if (!slide) {
          break;
        }
        if (!slide.hidden) {
          sortedSlidesArray.push(slide);
        }
        currentId = slide.next!;
      }
      logger.info(`Sorted slides`);
    } catch (error: any) {
      logger.error(`Failed to sort slides: ${error.message}`);
      res.status(500).send(`Failed to sort slides: ${error.message}`);
      return;
    }

    const privateKey = process.env.CLOUDFRONT_PRIVATE_KEY!;
    const keyPairId = process.env.CLOUDFRONT_KEY_PAIR_ID!;
    const expires = Math.floor(Date.now() / 1000) + 5 * 60;

    const policy = {
      Statement: [
        {
          Resource: `https://${process.env.CLOUDFRONT_DOMAIN}/${presentationId}/*`,
          Condition: {
            DateLessThan: {
              "AWS:EpochTime": expires,
            },
          },
        },
      ],
    };

    const signedUrlSuffix = createSignedUrlSuffix(
      policy,
      privateKey,
      keyPairId
    );

    // Read the Tailwind CSS content
    const tailwindCssPath = path.join(__dirname, "../../dist/tailwind.css");
    const tailwindCssContent = fs.readFileSync(tailwindCssPath, "utf-8");

    // Read the iconify-icon script
    const iconifyIconPath = path.join(__dirname, "../../src/iconify-icon.min.js");
    const iconifyIconContent = fs.readFileSync(iconifyIconPath, "utf-8");


    const fontCSS = `@font-face {
    font-family: 'Inter';
    font-style: normal;
    font-weight: 100 900;
    font-display: swap;
    src: url('${process.env.INTER_TTF_URL}') format('truetype');
  }`;

    const browser = await puppeteer.launch({
      headless: !DEBUG,
      args: ["--no-sandbox", "--disable-setuid-sandbox"],
    });

    const slidesHtml = sortedSlidesArray
      .map(
        (slide) =>
          ReactDOMServer.renderToString(
            <div className="slide text-black dark:text-white bg-neutral-100 dark:bg-neutral-900 nobg:bg-white" style={{ pageBreakAfter: "always", width: "1281px", height: "720px"}}>
              <SlideComponent slide={slide} signedUrlSuffix={signedUrlSuffix} dark={theme === "dark"}/>
            </div>
          )
      )
      .join("");

    const html = `
      <html>
        <head>
          <style>${fontCSS}</style>
          <style>${tailwindCssContent}</style>
          <style>
            .slide {
              width: 1280px;
              height: 720px;
              page-break-after: always;
            }
          </style>
          <script>${iconifyIconContent}</script>
        </head>
        <body class="${themeClass}">
          ${slidesHtml}
        </body>
      </html>
    `;

    const page = await browser.newPage();

    await page.setViewport({
      width: 1280,
      height: 720,
      deviceScaleFactor: 1,
    });

    // Log network activity
    page.on("request", (request) => {
      logger.debug(`Request: ${request.url()}`);
    });

    page.on("response", async (response) => {
      const status = response.status();
      const url = response.url();
      logger.debug(`Response: ${url} - ${status}`);

      if (status === 403) {
        try {
          const text = await response.text();
          logger.error(`403 Error Details for ${url}:\n${text}`);
        } catch (error) {
          logger.error(`Failed to get 403 error details for ${url}: ${error}`);
        }
      }
    });

    await page.setContent(html, {
      waitUntil: ["load", "networkidle0"],
      timeout: 60000, // Increased timeout
    });

    logger.info(`Page content set`);

    // Wait for images to load
    await page.evaluate(() => {
      return Promise.all(
        Array.from(document.images)
          .filter((img) => !img.complete)
          .map(
            (img) =>
              new Promise((resolve) => {
                img.onload = img.onerror = resolve;
              })
          )
      );
    });

    const pdfBuffer = await page.pdf({
      width: "1280px",
      height: "720px",
      landscape: false,
      printBackground: true,
    });

    if (!DEBUG) {
      await browser.close();
    }

    if (SAVE_TO_FILE) {
      const filePath = path.join(
        __dirname,
        `../../output/${sanitizeFileName(presentation.topic)}.pdf`
      );
      fs.writeFileSync(filePath, pdfBuffer);
      res.json({ filePath });
      logger.info(`PDF generated and saved to file: ${filePath}`);
    } else {
      const s3Client = new S3Client({ region: process.env.AWS_REGION });
      const s3Key = `${presentationId}/${sanitizeFileName(
        presentation.topic
      )}.pdf`;
      const command = new PutObjectCommand({
        Bucket: process.env.SOURCES_BUCKET_NAME,
        Key: s3Key,
        Body: pdfBuffer,
        ContentType: "application/pdf",
      });
      await s3Client.send(command);

      res.json({ s3Key });
      logger.info(`PDF generated and uploaded to S3: ${s3Key}`);
    }
  } catch (error: any) {
    logger.error(`Failed to generate PDF: ${error.message}\n${error.stack}`);
    res.status(500).send(`Failed to generate PDF: ${error.message}`);
  }
}
