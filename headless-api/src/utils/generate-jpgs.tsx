// headless-api/src/utils/generate-jpgs.tsx
import { Request, Response } from "express";
import React from "react";
import ReactDOMServer from "react-dom/server";
import { SlideComponent } from "../components/slide-component";
import logger from "./logger";
import { sanitizeFileName } from "./sanitize-file-name";
import archiver from "archiver";
import streamBuffers from "stream-buffers";
import {
  fetchAndSortSlides,
  setupBrowser,
  readStaticFiles,
  uploadBufferToS3,
  generateSignedUrlSuffix,
  DEBUG,
} from "./generate-utils";

export async function generateJPGs(req: Request, res: Response) {
  const { presentationId } = req.params;
  const { theme, footnotes, resolution } = req.body;
  const themeClass = theme === "print" ? "nobg" : theme === "dark" ? "dark" : "";

  if (!["dark", "light", "print"].includes(theme)) {
    logger.info(`Received invalid theme: ${theme}`);
    res.status(400).send("Invalid theme, please use 'dark', 'light' or 'print'");
    return;
  }

  if (!["1920x1080", "1280x720"].includes(resolution)) {
    logger.info(`Received invalid resolution: ${resolution}`);
    res.status(400).send("Invalid resolution, please use '1920x1080' or '1280x720'");
    return;
  }

  const [viewportWidth, viewportHeight] = [1280, 720];
  const [screenshotWidth, screenshotHeight] = resolution === "1920x1080" ? [1920, 1080] : [1280, 720];

  logger.info(`Received theme: ${theme}, resolution: ${resolution}, footnotes: ${footnotes}`);

  try {
    const { presentation, sortedSlidesArray } = await fetchAndSortSlides(presentationId);
    const signedUrlSuffix = generateSignedUrlSuffix(presentationId);

    const { tailwindCssContent, iconifyIconContent, fontCSS } = readStaticFiles();

    const { browser, page } = await setupBrowser();

    await page.setViewport({
      width: viewportWidth,
      height: viewportHeight,
      deviceScaleFactor: 1,
    });

    const jpegBuffers = [];

    for (const slide of sortedSlidesArray) {
      const slideHtml = ReactDOMServer.renderToString(
        <div className="slide text-black dark:text-white bg-neutral-100 dark:bg-neutral-900 nobg:bg-white" style={{ width: `${viewportWidth}px`, height: `${viewportHeight}px` }}>
          <SlideComponent slide={slide} signedUrlSuffix={signedUrlSuffix} dark={theme === "dark"} />
        </div>
      );

      const html = `
        <html>
          <head>
            <style>${fontCSS}</style>
            <style>${tailwindCssContent}</style>
            <style>
              .slide {
                width: ${viewportWidth}px;
                height: ${viewportHeight}px;
              }
            </style>
            <script>${iconifyIconContent}</script>
          </head>
          <body class="${themeClass}">
            ${slideHtml}
          </body>
        </html>
      `;

      await page.setContent(html, {
        waitUntil: ["load", "networkidle0"],
        timeout: 60000,
      });

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

      // Take screenshot with the desired settings (choose either fullPage or clip, not both)
      const jpegBuffer = await page.screenshot({
        type: 'jpeg',
        quality: 80,
        // Remove 'clip' option to use fullPage
        fullPage: true, 
        omitBackground: true
      });

      const scaledBuffer = resolution === "1920x1080"
        ? await scaleImage(jpegBuffer, screenshotWidth, screenshotHeight)
        : jpegBuffer;

      jpegBuffers.push({ buffer: scaledBuffer, slide });
    }

    if (!DEBUG) {
      await browser.close();
    }

    // Use a stream buffer to handle zip file creation in memory
    const zipStream = new streamBuffers.WritableStreamBuffer({
      initialSize: (100 * 1024),   // start at 100 kilobytes
      incrementAmount: (10 * 1024) // grow by 10 kilobytes each time buffer overflows
    });

    const archive = archiver('zip', { zlib: { level: 9 } });

    archive.on('error', (err) => {
      throw err;
    });

    archive.pipe(zipStream);

    jpegBuffers.forEach(({ buffer, slide }, index) => {
      const slideFileName = sanitizeFileName(slide.title || `Slide_${index + 1}`) + '.jpg';
      archive.append(buffer, { name: slideFileName });
    });

    await archive.finalize();

    // When the zip is finalized, convert the stream buffer to a Buffer
    const zipBuffer = zipStream.getContents() as Buffer;

    const zipFileName = `${presentationId}/slides.zip`;

    // Upload the zip buffer to S3
    await uploadBufferToS3(zipBuffer, zipFileName, 'application/zip');

    res.json({ s3Key: zipFileName });

  } catch (error: any) {
    logger.error(`Failed to generate JPEGs: ${error.message}\n${error.stack}`);
    res.status(500).send(`Failed to generate JPEGs: ${error.message}`);
  }
}

async function scaleImage(buffer: Buffer, width: number, height: number): Promise<Buffer> {
  const sharp = require('sharp');
  return sharp(buffer)
    .resize(width, height)
    .toBuffer();
}