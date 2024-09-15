import { Router, Request, Response } from 'express';
import { launchCluster } from '../utils/cluster';

const router = Router();

router.post('/', async (req: Request, res: Response) => {
  const { code } = req.body;
  if (!code) {
    // No need for additional logging here, as pino-http will log the 400 status
    return res.status(400).send('Mermaid code is required');
  }

  try {
    const cluster = await launchCluster();

    const generateSvg = async ({ page, data: { theme, code } }: any) => {
      await page.setContent(`
        <!DOCTYPE html>
        <html>
        <body>
        <div class="mermaid">${code}</div>
        <script type="module">
          import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@9/dist/mermaid.esm.min.mjs';
          mermaid.initialize({ startOnLoad: true, theme: '${theme}' });
        </script>
        </body>
        </html>
      `);

      await page.waitForSelector('.mermaid > svg', { timeout: 3000 });
      return await page.$eval('.mermaid', (el: HTMLElement) => el.innerHTML);
    };

    const lightSvg = await cluster.execute({ theme: 'default', code }, generateSvg);
    const darkSvg = await cluster.execute({ theme: 'dark', code }, generateSvg);

    // No need for additional success logging, as pino-http will log the 200 status
    res.json({ lightSvg, darkSvg });
  } catch (error: any) {
    // Log additional error details that pino-http wouldn't capture
    req.log.error({ error }, 'SVG generation failed');
    res.status(500).send('Failed to generate SVG');
  }
});

export default router;
