// headless-service/src/routes/prose-class.ts
import { Router, Request, Response } from 'express';
import { launchCluster } from '../utils/cluster';
import { marked } from 'marked';
import path from 'path';

const router = Router();

const ENABLE_SCREENSHOT = false; // Flag to enable or disable screenshot taking

router.post('/', async (req: Request, res: Response) => {
  const { markdown, title } = req.body;
  if (!markdown) {
    req.log.warn('Markdown is required');
    return res.status(400).send('Markdown is required');
  }

  if (!title) {
    req.log.warn('Title is required');
    return res.status(400).send('Title is required');
  }

  try {
    const cluster = await launchCluster();

    const determineProseClass = async ({ page, data: { markdown, title } }: any) => {
      const html = marked.parse(markdown);

      await page.setViewport({ width: 960, height: 540 });
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
                ${title}
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

      const contentHeight = await page.evaluate(() => {
        const content = document.querySelector('.slide-content');
        return content ? content.clientHeight : 0;
      });

      let proseClass = 'prose-2xl';
      if (contentHeight >= 570) {
        proseClass = 'overheight';
      } else if (contentHeight >= 500) {
        proseClass = 'prose-xs';
      } else if (contentHeight >= 400) {
        proseClass = 'prose-sm';
      } else if (contentHeight >= 375) {
        proseClass = 'prose-base';
      } else if (contentHeight >= 300) {
        proseClass = 'prose-lg';
      } else if (contentHeight > 190) {
        proseClass = 'prose-xl';
      }

      let screenshotPath = '';
      if (ENABLE_SCREENSHOT) {
        screenshotPath = path.join(__dirname, '..', '..', 'screenshots', `screenshot-${Date.now()}.png`);
        await page.screenshot({ path: screenshotPath });
      }

      return { proseClass };
    };

    const { proseClass, screenshotPath } = await cluster.execute({ markdown, title }, determineProseClass);
    req.log.info('Prose class determined');
    res.json({ proseClass });
  } catch (error: any) {
    req.log.error({
      error: {
        message: error.message,
        stack: error.stack,
        name: error.name
      }
    }, 'Failed to determine prose class');
    res.status(500).send('Failed to determine prose class');
  }
});

export default router;
