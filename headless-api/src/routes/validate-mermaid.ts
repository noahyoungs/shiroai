import { Router, Request, Response } from 'express';
import { launchCluster } from '../utils/cluster';
import globalLogger from '../utils/logger';

const router = Router();

router.post('/', async (req: Request, res: Response) => {
  const { diagram } = req.body;
  if (!diagram) {
    globalLogger.warn('Mermaid diagram is required');
    return res.status(400).send('Mermaid diagram is required');
  }

  function removeStacktrace(errorMessage: string): string {
    if (!errorMessage) return '';
    const lines = errorMessage.split('\n');
    const newLines = lines.filter(line => !line.includes('w1.parseError'));
    return newLines.join('\n');
  }

  try {
    const cluster = await launchCluster();

    const validateMermaid = async ({ page, data: { diagram } }: any) => {
      await page.setContent(`
        <!DOCTYPE html>
        <html>
        <head>
        <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
        </head>
        <body>
        <script>
        const diagram = \`${diagram.trim()}\`;
        window.isValid = false;
        window.errorMessage = '';
        try {
            window.isValid = mermaid.parse(diagram);
        } catch (err) {
            window.errorMessage = err.message;
        }
        </script>
        </body>
        </html>
      `);

      const parsingResult = await page.evaluate(() => (window as any).isValid);
      let errorMessage = '';
      if (!parsingResult) {
        errorMessage = await page.evaluate(() => (window as any).errorMessage);
      }

      return { parsingResult, errorMessage: removeStacktrace(errorMessage) };
    };

    const { parsingResult, errorMessage } = await cluster.execute({ diagram }, validateMermaid);
    if (parsingResult) {
      globalLogger.info('Valid Mermaid diagram');
      res.json({ valid: true, message: 'Valid Mermaid diagram' });
    } else {
      globalLogger.warn(`Invalid Mermaid diagram: ${errorMessage}`);
      res.json({ valid: false, message: errorMessage || 'Invalid Mermaid diagram' });
    }
  } catch (error: any) {
    globalLogger.error(`Failed to validate Mermaid diagram: ${removeStacktrace(error.message)}`);
    res.json({ valid: false, message: removeStacktrace(error.message) || 'Invalid Mermaid diagram' });
  }
});

export default router;
