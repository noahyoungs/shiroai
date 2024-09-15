import 'dotenv/config';
import express, { Request, Response, NextFunction } from 'express';
import https from 'https';
import fs from 'fs';
import path from 'path';
import cors from 'cors';
import globalLogger, { getChildLogger } from './utils/logger.js';
import mermaidRoutes from './routes/mermaid.js';
import proseClassRoutes from './routes/prose-class.js';
import validateMermaidRoutes from './routes/validate-mermaid.js';
import mermaidDimensionsRoutes from './routes/mermaid-dimensions.js';
import generatePDFRouter from './routes/generate-pdf-router.js';
import markdownSplitRouter from './routes/markdown-split.js';
import generateJPGsRouter from './routes/generate-jpgs-router.js';
import generateVideoRouter from './routes/generate-video-router.js';
import pinoHttp from 'pino-http';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

process.on('uncaughtException', (error) => {
  console.error('Uncaught Exception:', error);
  process.exit(1);
});

process.on('unhandledRejection', (reason, promise) => {
  console.error('Unhandled Rejection at:', promise, 'reason:', reason);
  process.exit(1);
});

const app = express();
app.use(express.json());

const logger = getChildLogger(import.meta.url);

// Initialize pino-http logger
const httpLogger = pinoHttp({
  logger: globalLogger,
  customProps: (req, res) => ({
    userId: req.headers['x-user-id'] || 'unknown'
  }),
  // Customize logging levels based on status code
  customLogLevel: (req, res, err) => {
    if (res.statusCode >= 400 && res.statusCode < 500) {
      return 'warn';
    } else if (res.statusCode >= 500 || err) {
      return 'error';
    }
    return 'info';
  },
});
app.use(httpLogger);

// Middleware to check for the API key and user ID
const apiKeyAndUserMiddleware = (req: Request, res: Response, next: NextFunction) => {
  const apiKey = req.header('x-api-key');
  const userId = req.header('x-user-id');
  const validApiKey = process.env.HEADLESS_API_INTERNAL_KEY;

  if (apiKey !== validApiKey) {
    return res.status(401).json({ error: 'Unauthorized' });
  }

  if (!userId) {
    return res.status(400).json({ error: 'User ID is required' });
  }

  // Set userId on the request object
  (req as any).userId = userId;

  next();
};

// Use the middleware
app.use(apiKeyAndUserMiddleware);

// Serve static files from the 'public' directory
const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
app.use(express.static(join(__dirname, '..', 'public')));

// Enable CORS with specified origin if needed
app.use(cors({
  origin: process.env.NEXT_PUBLIC_BASE_URL,
}));

// Use the routes
app.use('/mermaid', mermaidRoutes);
app.use('/prose-class', proseClassRoutes);
app.use('/validate-mermaid', validateMermaidRoutes);
app.use('/mermaid-dimensions', mermaidDimensionsRoutes);
app.use('/generate-pdf', generatePDFRouter);
app.use('/markdown-split', markdownSplitRouter);
app.use('/generate-jpg', generateJPGsRouter);
app.use('/generate-mp4', generateVideoRouter);

// Test connection route
app.get('/test-connection', (req, res) => {
  res.status(200).send('Server is running properly');
});

const PORT = process.env.PORT || 3003;
const httpsOptions = {
  key: fs.readFileSync(join(__dirname, '..', 'localhost+2-key.pem')),
  cert: fs.readFileSync(join(__dirname, '..', 'localhost+2.pem')),
};

https.createServer(httpsOptions, app).listen(PORT, async () => {
  logger.info(`Server is running on port ${PORT} with HTTPS`);
});

process.on('exit', async () => {
  // Clean up resources if necessary
  logger.info('Server is shutting down');
});
