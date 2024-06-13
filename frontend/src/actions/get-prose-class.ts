import puppeteer from "puppeteer";
import { marked } from "marked";
import fs from "fs";
import path from "path";

export async function getProseClass(markdown: string): Promise<string> {
  try {
    const browser = await puppeteer.launch();
    const page = await browser.newPage();

    // Set the viewport size to match the slide dimensions
    await page.setViewport({ width: 960, height: 540 });

    // Convert the markdown to HTML using marked
    const html = marked(markdown);

    // Set the page content to the HTML with the generated styles
    await page.setContent(`
      <html>
        <head>
        <script src="https://cdn.tailwindcss.com?plugins=typography"></script>
        </head>
        <body>
          <div class="p-12 pb-0 flex flex-col relative text-foreground dark:bg-foreground/10 bg-foreground/5 box-border bg-content1 outline-none shadow-medium rounded-large w-full flex-none aspect-video overflow-scroll">
            <div class="flex-none">
              <div class="border-b-medium border-transparent rounded-none">
                <div class="pb-[8px] box-border text-4xl font-bold [overflow-wrap:anywhere]">
                  Slide Title
                </div>
              </div>
            </div>
            <div class="flex-auto"></div>
            <div class="slide-content flex flex-col justify-center w-full max-w-none prose">
              ${html}
            </div>
            <div class="flex-auto"></div>
          </div>
        </body>
      </html>
    `);

    // Get the height of the slide content
    const contentHeight = await page.evaluate(() => {
      const content = document.querySelector(".slide-content");
      // @ts-ignore
      return content.offsetHeight;
    });

    console.log("Content height:", contentHeight);

    // Save the rendered page as an image
    const outputDir = "./public/rendered-pages";
    if (!fs.existsSync(outputDir)) {
      fs.mkdirSync(outputDir, { recursive: true });
    }
    const imagePath = path.join(outputDir, "rendered-page.png");
    await page.screenshot({ path: imagePath, fullPage: true });

    await browser.close();

    // Determine the prose class based on the content height
    let proseClass = "prose-2xl";
    if (contentHeight >= 570) {
      proseClass = "overheight";
    } else if (contentHeight >= 500) {
      proseClass = "prose-xs";
    } else if (contentHeight >= 400) {
      proseClass = "prose-sm";
    } else if (contentHeight >= 375) {
      proseClass = "prose-base";
    } else if (contentHeight >= 300) {
      proseClass = "prose-lg";
    } else if (contentHeight > 190) {
      proseClass = "prose-xl";
    }

    console.log("Prose class:", proseClass);
    return proseClass;
  } catch (error) {
    console.error(error);
    throw new Error("Failed to determine prose class");
  }
}
