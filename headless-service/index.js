const express = require('express');
const { Cluster } = require('puppeteer-cluster');
const { marked } = require('marked');
const fs = require('fs');
const path = require('path');
const winston = require('winston');

// Configure winston logger
const logger = winston.createLogger({
  level: 'info',
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.printf(({ timestamp, level, message }) => {
      return `${timestamp} [${level.toUpperCase()}]: ${message}`;
    })
  ),
  transports: [
    new winston.transports.Console(),
    new winston.transports.File({ filename: 'app.log' })
  ],
});

const app = express();
app.use(express.json());

let cluster;

async function launchCluster() {
  if (!cluster) {
    cluster = await Cluster.launch({
      concurrency: Cluster.CONCURRENCY_CONTEXT,
      maxConcurrency: 4, // Adjust based on your server's capacity
      puppeteerOptions: { headless: true },
    });
    logger.info('Cluster launched');
  }
  return cluster;
}

// Generate SVG from Mermaid code
app.post('/mermaid', async (req, res) => {
  const { code } = req.body;
  if (!code) {
    logger.warn('Mermaid code is required');
    return res.status(400).send('Mermaid code is required');
  }

  try {
    const cluster = await launchCluster();

    const generateSvg = async ({ page, data: { theme, code } }) => {
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
      return await page.$eval('.mermaid', el => el.innerHTML);
    };

    const lightSvg = await cluster.execute({ theme: 'default', code }, generateSvg);
    const darkSvg = await cluster.execute({ theme: 'dark', code }, generateSvg);

    logger.info('SVG generated successfully');
    res.json({ lightSvg, darkSvg });
  } catch (error) {
    logger.error(`Failed to generate SVG: ${error.message}`);
    res.status(500).send(`Failed to generate SVG: ${error.message}`);
  }
});

// Determine prose class
app.post('/prose-class', async (req, res) => {
    const { markdown, title } = req.body;
    if (!markdown) {
      logger.warn('Markdown is required');
      return res.status(400).send('Markdown is required');
    }
  
    if (!title) {
      logger.warn('Title is required');
      return res.status(400).send('Title is required');
    }
  
    try {
      const cluster = await launchCluster();
  
      const determineProseClass = async ({ page, data: { markdown, title } }) => {
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
          return content.offsetHeight;
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
  
        const screenshotPath = path.join(__dirname, 'screenshots', `screenshot-${Date.now()}.png`);
        await page.screenshot({ path: screenshotPath });
  
        return { proseClass, screenshotPath };
      };
  
      const { proseClass, screenshotPath } = await cluster.execute({ markdown, title }, determineProseClass);
      logger.info('Prose class determined and screenshot taken');
      res.json({ proseClass, screenshotPath });
    } catch (error) {
      logger.error(`Failed to determine prose class: ${error.message}`);
      res.status(500).send(`Failed to determine prose class: ${error.message}`);
    }
  });
  

// Validate Mermaid diagram
app.post('/validate-mermaid', async (req, res) => {
  const { diagram } = req.body;
  if (!diagram) {
    logger.warn('Mermaid diagram is required');
    return res.status(400).send('Mermaid diagram is required');
  }

  function removeStacktrace(error_message) {
    const lines = error_message.split('\n');
    const new_lines = lines.filter(line => !line.includes('w1.parseError'));
    return new_lines.join('\n');
  }

  try {
    const cluster = await launchCluster();

    const validateMermaid = async ({ page, data: { diagram } }) => {
      await page.setContent(`
        <!DOCTYPE html>
        <html>
        <head>
        <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
        </head>
        <body>
        <script>
        const diagram = \`${diagram}\`;
        let isValid = false;
        let errorMessage = '';
        try {
            isValid = mermaid.parse(diagram);
        } catch (err) {
            errorMessage = err.message;
        }
        </script>
        </body>
        </html>
      `);

      const parsingResult = await page.evaluate('isValid');
      let errorMessage = '';
      if (!parsingResult) {
        errorMessage = await page.evaluate('errorMessage');
      }

      return { parsingResult, errorMessage: removeStacktrace(errorMessage) };
    };

    const { parsingResult, errorMessage } = await cluster.execute({ diagram }, validateMermaid);
    if (parsingResult) {
      logger.info('Valid Mermaid diagram');
      res.json({ valid: true, message: 'Valid Mermaid diagram' });
    } else {
      logger.warn(`Invalid Mermaid diagram: ${errorMessage}`);
      res.json({ valid: false, message: errorMessage || 'Invalid Mermaid diagram' });
    }
  } catch (error) {
    logger.error(`Failed to validate Mermaid diagram: ${removeStacktrace(error.message)}`);
    res.json({ valid: false, message: removeStacktrace(error.message) || 'Invalid Mermaid diagram' });
  }
});

// Get dimensions of Mermaid diagram
app.post('/mermaid-dimensions', async (req, res) => {
  const { code } = req.body;
  if (!code) {
    logger.warn('Mermaid code is required');
    return res.status(400).send('Mermaid code is required');
  }

  try {
    const cluster = await launchCluster();

    const getDimensions = async ({ page, data: { code } }) => {
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
        const { width, height } = svg.getBoundingClientRect();
        return { width, height };
      });

      return dimensions;
    };

    const dimensions = await cluster.execute({ code }, getDimensions);
    logger.info('Dimensions retrieved successfully');
    res.json(dimensions);
  } catch (error) {
    logger.error(`Failed to get dimensions: ${error.message}`);
    res.status(500).send(`Failed to get dimensions: ${error.message}`);
  }
});

const PORT = process.env.PORT || 3003;
app.listen(PORT, async () => {
  await launchCluster();
  logger.info(`Server is running on port ${PORT}`);
});

process.on('exit', async () => {
  if (cluster) {
    await cluster.idle();
    await cluster.close();
    logger.info('Cluster closed');
  }
});
