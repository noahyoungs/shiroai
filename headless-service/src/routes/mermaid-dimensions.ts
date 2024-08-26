import { Router, Request, Response } from 'express';
import { launchCluster } from '../utils/cluster';
import logger from '../utils/logger';

const router = Router();

router.post('/', async (req: Request, res: Response) => {
  const { code } = req.body;
  if (!code) {
    logger.warn('Mermaid code is required');
    return res.status(400).send('Mermaid code is required');
  }

  try {
    const cluster = await launchCluster();

    const getDimensions = async ({ page, data: { code } }: any) => {
      await page.setContent(`
        <!DOCTYPE html>
        <html>
        <body>
        <div class="mermaid">${code}</div>
        <script type="module">
          import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@9/dist/mermaid.esm.min.mjs';
          mermaid.initialize({ startOnLoad: true });
        </script>
        </body>
        </html>
      `);

      await page.waitForSelector('.mermaid > svg', { timeout: 3000 });
      const dimensions = await page.evaluate(() => {
        const svg = document.querySelector('.mermaid > svg');
        const { width, height } = svg?.getBoundingClientRect() || { width: 0, height: 0 };
        return { width, height };
      });

      return dimensions;
    };

    const dimensions = await cluster.execute({ code }, getDimensions);
    logger.info('Dimensions retrieved successfully');
    res.json(dimensions);
  } catch (error: any) {
    logger.error(`Failed to get dimensions: ${error.message}`);
    res.status(500).send(`Failed to get dimensions: ${error.message}`);
  }
});

export default router;
