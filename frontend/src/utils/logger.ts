import pino, { Logger } from "pino";
import { fileURLToPath } from 'url';
import path from 'path';

export const globalLogger: Logger =
  process.env["NODE_ENV"] === "production"
    ? // JSON in production
    pino({ level: "warn" })
    : // Pretty print in development
    pino({
      transport: {
        target: 'pino-pretty',
        options: {
          colorize: true
        },
        level: "info"
      }
    });

/**
 * Creates a child logger with the relative file path as metadata.
 * 
 * This function is designed to be used in ES modules to create a logger
 * specific to the current file. It adds the relative file path as metadata
 * to help identify the source of log messages.
 * 
 * @param {string} url - The URL of the current module (use import.meta.url)
 * @returns {Object} A child logger instance
 * 
 * @example
 * // In your ES module file (e.g., myModule.js):
 * import { getChildLogger } from './logger.js';
 * 
 * const logger = getChildLogger(import.meta.url);
 * 
 * // Now you can use the logger in your file
 * logger.info('This is a log message from myModule.js');
 */
export const getChildLogger = (url: string) => {
  const __filename = fileURLToPath(url);
  const filePath = path.relative(process.cwd(), __filename);
  return globalLogger.child({ file: filePath });
};