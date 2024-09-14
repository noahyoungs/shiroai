// headless-api/src/utils/generate-pdf.tsx

import { Request, Response } from "express";
import React from "react";
import ReactDOMServer from "react-dom/server";
import { SlideComponent } from "../components/slide-component";
import globalLogger from "./logger";
import {
  fetchAndSortSlides,
  setupBrowser,
  readStaticFiles,
  uploadBufferToS3,
  generateSignedUrlSuffix,
  DEBUG,
} from "./generate-utils";
import { sanitizeFileName } from "./sanitize-file-name";


export async function generatePDF(req: Request, res: Response) {
  const { presentationId } = req.params;
  const { theme, footnotes } = req.body;
  const themeClass = theme === "print" ? "nobg" : theme === "dark" ? "dark" : "";

  if (!["dark", "light", "print"].includes(theme)) {
    globalLogger.info(`Received invalid theme: ${theme}`);
    res.status(400).send("Invalid theme, please use 'dark', 'light' or 'print'");
    return;
  }

  globalLogger.info(`Received theme: ${theme}, footnotes: ${footnotes}`);

  try {
    const { presentation, sortedSlidesArray } = await fetchAndSortSlides(presentationId);
    const signedUrlSuffix = generateSignedUrlSuffix(presentationId);

    const { tailwindCssContent, iconifyIconContent, fontCSS } = readStaticFiles();

    const { browser, page } = await setupBrowser();

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

    await page.setViewport({
      width: 1280,
      height: 720,
      deviceScaleFactor: 1,
    });

    page.on("request", (request) => {
      globalLogger.debug(`Request: ${request.url()}`);
    });

    page.on("response", async (response) => {
      const status = response.status();
      const url = response.url();
      globalLogger.debug(`Response: ${url} - ${status}`);

      if (status === 403) {
        try {
          const text = await response.text();
          globalLogger.error(`403 Error Details for ${url}:\n${text}`);
        } catch (error) {
          globalLogger.error(`Failed to get 403 error details for ${url}: ${error}`);
        }
      }
    });

    await page.setContent(html, {
      waitUntil: ["load", "networkidle0"],
      timeout: 60000,
    });

    globalLogger.info(`Page content set`);

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

    const s3Key = `${presentationId}/export/pdf/${sanitizeFileName(
      presentation.topic
    )}.pdf`;
    
    await uploadBufferToS3(pdfBuffer, s3Key, 'application/pdf');

    res.json({ s3Key });
    globalLogger.info(`PDF generated and uploaded to S3: ${s3Key}`);
  } catch (error: any) {
    globalLogger.error(`Failed to generate PDF: ${error.message}\n${error.stack}`);
    res.status(500).send(`Failed to generate PDF: ${error.message}`);
  }
}