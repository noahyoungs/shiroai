// headless-api/src/utils/generate-utils.tsx

import path from "path";
import puppeteer, { Browser, Page } from "puppeteer";
import { S3Client, PutObjectCommand } from "@aws-sdk/client-s3";
import fs from "fs";
import { Presentation, Slide } from "@shared-utils/database-types";
import globalLogger from "./logger";
import { getItems, getAllItemsForPresentation } from "./dynamodb-interface-factory";
import { createSignedUrlSuffix } from "./create-signed-url-suffix";

export const DEBUG = false;

export async function fetchAndSortSlides(userId: string, presentationId: string, slide_attrs?: string[]): Promise<{ presentation: any, sortedSlidesArray: Slide[] }> {
  // const presentation = await getPresentationByID(presentationId, ["head_slide_id", "topic"]);
  const presentation = await getItems('presentation', { user_id: userId, presentation_id: presentationId }, ["head_slide_id", "topic"]) as Presentation;
  globalLogger.info(`Fetched presentation`);

  if (!presentation) {
    throw new Error("Presentation not found, please check the presentation id");
  }

  if (!presentation.head_slide_id) {
    throw new Error("No head slide found for the presentation");
  }

  const unsortedSlidesArray = await getAllItemsForPresentation("slide", userId, presentationId, slide_attrs) as Slide[];
  globalLogger.info(`Fetched unsorted slides`);

  if (!unsortedSlidesArray.length) {
    throw new Error("No slides found for the presentation though the presentation exists");
  }

  let slidesMap: { [key: string]: Slide } = {};
  unsortedSlidesArray.forEach((slide: Slide | undefined) => {
    if (slide) {
      slidesMap[slide.id] = slide;
    }
  });

  globalLogger.info(`Converted slides to map`);

  let sortedSlidesArray: Slide[] = [];
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
  globalLogger.info(`Sorted slides`);

  return { presentation, sortedSlidesArray };
}

export async function setupBrowser(): Promise<{ browser: Browser, page: Page }> {
  const browser = await puppeteer.launch({
    headless: !DEBUG,
    args: ["--no-sandbox", "--disable-setuid-sandbox"],
  });
  const page = await browser.newPage();
  return { browser, page };
}

export function readStaticFiles() {
  const tailwindCssPath = path.join(__dirname, "../../dist/tailwind.css");
  const tailwindCssContent = fs.readFileSync(tailwindCssPath, "utf-8");

  const iconifyIconPath = path.join(__dirname, "../../src/iconify-icon.min.js");
  const iconifyIconContent = fs.readFileSync(iconifyIconPath, "utf-8");

  const fontCSS = `@font-face {
    font-family: 'Inter';
    font-style: normal;
    font-weight: 100 900;
    font-display: swap;
    src: url('${process.env.INTER_TTF_URL}') format('truetype');
  }`;

  return { tailwindCssContent, iconifyIconContent, fontCSS };
}

export async function uploadBufferToS3(buffer: Buffer, key: string, contentType: string): Promise<void> {
  const s3Client = new S3Client();
  const uploadCommand = new PutObjectCommand({
    Bucket: process.env.SOURCES_BUCKET_NAME,
    Key: key,
    Body: buffer,
    ContentType: contentType,
  });

  await s3Client.send(uploadCommand);
  globalLogger.info(`Buffer uploaded to S3: ${key}`);
}

export function generateSignedUrlSuffix(presentationId: string): string {
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

  return createSignedUrlSuffix(policy, privateKey, keyPairId);
}