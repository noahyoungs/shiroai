import 'dotenv/config'; // Load environment variables from .env file
import express, { Request, Response, NextFunction } from 'express';
import https from 'https';
import fs from 'fs';
import path from 'path';
import cors from 'cors'; // Import the CORS package
import logger from './utils/logger';
import requestLogger from './utils/request-logger';
import mermaidRoutes from './routes/mermaid';
import proseClassRoutes from './routes/prose-class';
import validateMermaidRoutes from './routes/validate-mermaid';
import mermaidDimensionsRoutes from './routes/mermaid-dimensions';
import generatePDFRouter from './routes/generate-pdf-router';
import markdownSplitRouter from './routes/markdown-split';
import generateJPGsRouter from './routes/generate-jpgs-router';
import generateVideoRouter from './routes/generate-video-router';

const app = express();
app.use(express.json());

// Middleware to check for the API key
const apiKeyMiddleware = (req: Request, res: Response, next: NextFunction) => {
  const apiKey = req.header('x-api-key');
  const validApiKey = process.env.HEADLESS_API_INTERNAL_KEY;

  if (apiKey === validApiKey) {
    next(); // Proceed if the API key matches
  } else {
    res.status(401).json({ error: 'Unauthorized' }); // Unauthorized if the API key does not match
  }
};

// Apply the request logger middleware
app.use(requestLogger);

// Serve static files from the 'public' directory
app.use(express.static(path.join(__dirname, 'public')));

// Enable CORS with specified origin if needed
app.use(cors({
  origin: process.env.NEXT_PUBLIC_BASE_URL,
}));

// Protect all routes with the API key middleware
app.use(apiKeyMiddleware);

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
  key: fs.readFileSync(path.join(__dirname, '../localhost+2-key.pem')),
  cert: fs.readFileSync(path.join(__dirname, '../localhost+2.pem')),
};

https.createServer(httpsOptions, app).listen(PORT, async () => {
  logger.info(`Server is running on port ${PORT} with HTTPS`);
});

process.on('exit', async () => {
  // Clean up resources if necessary
  logger.info('Server is shutting down');
});