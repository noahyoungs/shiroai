import { Request, Response, NextFunction } from 'express';
import logger from './logger';

const requestLogger = (req: Request, res: Response, next: NextFunction) => {
  const start = Date.now();
  res.on('finish', () => {
    const duration = Date.now() - start;
    const logMessage = `${req.method} ${req.originalUrl} ${res.statusCode} ${duration}ms`;
    logger.info(logMessage);
  });
  next();
};

export default requestLogger;
