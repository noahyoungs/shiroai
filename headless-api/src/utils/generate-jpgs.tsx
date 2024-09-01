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

/**
 * Function to generate JPGs for a presentation.
 *
 * @param presentationID - The ID of the presentation.
 * @param theme - The theme for the slides (dark, light, print).
 * @param footnotes - Whether to include footnotes for the slides.
 * @param resolution - The desired resolution ('1920x1080', '1280x720', '2560x1440', '3840x2160').
 * @param sortedSlidesArray - An array of sorted slides.
 * @param zipFileName - The name to use for the zip file (replaces 'slides' in 'slides.zip').
 * @param s3Subdirectory - The subdirectory within the S3 bucket under the presentationId where slides.zip will be stored (defaults to '').
 */
export async function generateJPGs(
  presentationID: string,
  theme: string,
  footnotes: boolean,
  resolution: string,
  sortedSlidesArray: any[],
  zipFileName: string,
  s3Subdirectory: string = ''
): Promise<{ s3Key: string; manifest: { slide_id: string; image_filename: string }[] } | Error> {
  const themeClass = theme === "print" ? "nobg" : theme === "dark" ? "dark" : "";

  // Ensure s3Subdirectory is in the format '/subdir/' or '/'
  if (s3Subdirectory === '' || !s3Subdirectory) {
    s3Subdirectory = '/';
  } 

  if (s3Subdirectory[0] !== '/') {
    s3Subdirectory = '/' + s3Subdirectory;
  }

  if (s3Subdirectory[s3Subdirectory.length - 1] !== '/') {
    s3Subdirectory = s3Subdirectory + '/';
  }

  if (!["dark", "light", "print"].includes(theme)) {
    const errorMsg = `Invalid theme: ${theme}. Please use 'dark', 'light' or 'print'`;
    logger.info(errorMsg);
    return new Error(errorMsg);
  }

  if (!["1920x1080", "1280x720", "2560x1440", "3840x2160"].includes(resolution)) {
    const errorMsg = `Invalid resolution: ${resolution}. Please use '1920x1080', '1280x720', '2560x1440', or '3840x2160'`;
    logger.info(errorMsg);
    return new Error(errorMsg);
  }

  const [viewportWidth, viewportHeight] = [1280, 720];
  const deviceScaleFactor = resolution === "1920x1080" ? 1.5 :
                            resolution === "2560x1440" ? 2 :
                            resolution === "3840x2160" ? 3 : 1;

  logger.info(`Received theme: ${theme}, resolution: ${resolution}, footnotes: ${footnotes}`);

  try {
    logger.info(`Generating signed URL suffix for presentation ID: ${presentationID}`);
    const signedUrlSuffix = generateSignedUrlSuffix(presentationID);

    logger.info(`Reading static files for presentation rendering`);
    const { tailwindCssContent, iconifyIconContent, fontCSS } = readStaticFiles();

    logger.info(`Setting up the Puppeteer browser`);
    const { browser, page } = await setupBrowser();

    await page.setViewport({
      width: viewportWidth,
      height: viewportHeight,
      deviceScaleFactor: deviceScaleFactor,
    });

    const jpegBuffers = [];
    const manifest: { slide_id: string; image_filename: string }[] = [];

    for (const [index, slide] of sortedSlidesArray.entries()) {
      try {
        logger.info(`Rendering slide: ${slide.slide_title || `Slide_${index + 1}`}`);
        const slideHtml = ReactDOMServer.renderToString(
          <div
            className="slide text-black dark:text-white bg-neutral-100 dark:bg-neutral-900 nobg:bg-white"
            style={{ width: `${viewportWidth}px`, height: `${viewportHeight}px` }}
          >
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

        logger.info(`Waiting for all images to load for slide ${index + 1} of ${sortedSlidesArray.length}`);
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

        logger.info(`Taking screenshot of slide ${index + 1} of ${sortedSlidesArray.length}`);
        const jpegBuffer = await page.screenshot({
          type: 'jpeg',
          quality: 80,
          fullPage: true,
          omitBackground: false,
        });

        jpegBuffers.push({ buffer: jpegBuffer, slide });

        // Generate consistent filename and update the manifest
        const sanitizedTitle = sanitizeFileName(slide.slide_title ? `${index + 1} ${slide.slide_title}` : `Slide_${index + 1}`)
        const slideFileName = `${sanitizedTitle}.jpg`;
        manifest.push({ slide_id: slide.id, image_filename: slideFileName });

      } catch (error: any) {
        logger.warn(`Error rendering slide ${index + 1}, omitted from manifest: ${error.message}\n${error.stack}`);
      }
    }

    if (!DEBUG) {
      logger.info(`Closing the Puppeteer browser`);
      await browser.close();
    }

    logger.info(`Creating zip archive for presentation ID: ${presentationID}`);
    const zipStream = new streamBuffers.WritableStreamBuffer({
      initialSize: 100 * 1024,
      incrementAmount: 10 * 1024,
    });

    const archive = archiver('zip', { zlib: { level: 9 } });

    archive.on('error', (err) => {
      throw err;
    });

    archive.pipe(zipStream);

    jpegBuffers.forEach(({ buffer, slide }, index) => {
      const sanitizedTitle = sanitizeFileName(slide.slide_title ? `${index + 1} ${slide.slide_title}` : `Slide_${index + 1}`);
      const slideFileName = `${sanitizedTitle}.jpg`;
      archive.append(buffer, { name: slideFileName });
    });

    await archive.finalize();

    const zipBuffer = zipStream.getContents() as Buffer;
    const finalZipFileName = `${presentationID}${s3Subdirectory}${zipFileName}.zip`;

    logger.info(`Uploading zip archive to S3: ${finalZipFileName}`);
    await uploadBufferToS3(zipBuffer, finalZipFileName, 'application/zip');

    logger.info(`Buffer uploaded to S3 successfully: ${finalZipFileName}`);
    return { s3Key: finalZipFileName, manifest }; // Return both s3Key and manifest

  } catch (error: any) {
    logger.error(`Failed to generate JPEGs: ${error.message}\n${error.stack}`);
    return new Error(`Failed to generate JPEGs: ${error.message}`);
  }
}


/**
 * Express handler to generate JPGs for a presentation via HTTP request.
 *
 * @param req - The Express request object.
 * @param res - The Express response object.
 */
export async function generateJPGsHandler(req: Request, res: Response) {
  const { presentationId } = req.params;
  const { theme, footnotes, resolution } = req.body;

  try {
    logger.info(`Fetching and sorting slides for presentation ID: ${presentationId}`);
    const { presentation, sortedSlidesArray } = await fetchAndSortSlides(presentationId);

    // Generate sanitized zip file name based on presentation topic
    const zipFileName = sanitizeFileName(presentation.topic);

    const result = await generateJPGs(
      presentationId,
      theme,
      footnotes,
      resolution,
      sortedSlidesArray,
      zipFileName,
      'export/jpg/'
    );

    if (result instanceof Error) {
      res.status(400).send(result.message);
    } else {
      res.json({ s3Key: result.s3Key, manifest: result.manifest }); // Send both s3Key and manifest in the response
    }
  } catch (error: any) {
    logger.error(`Failed to process generateJPGsHandler: ${error.message}\n${error.stack}`);
    res.status(500).send(`Internal Server Error: ${error.message}`);
  }
}
