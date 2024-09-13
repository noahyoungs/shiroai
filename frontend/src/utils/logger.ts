import pino, { Logger } from "pino";
import { fileURLToPath } from 'url';
import path from 'path';

export const globalLogger: Logger =
  process.env["NODE_ENV"] === "production"
    ? // JSON in production
    pino({ level: "warn" })
    : // Pretty print in development
    pino({
      // transport: {
      //   target: 'pino-pretty',
      //   options: {
      //     colorize: true
      //   }
      // }
    });

export const getChildLogger = (url: string) => {
  const __filename = fileURLToPath(url);
  const filePath = path.relative(process.cwd(), __filename);
  return globalLogger.child({ file: filePath });
};