import pino from 'pino';

const logger = pino({
  level: 'info',
  timestamp: pino.stdTimeFunctions.isoTime,
  transport: {
    targets: [
      { target: 'pino-pretty', options: { destination: 1 } },
    ]
  }
});

export default logger;
