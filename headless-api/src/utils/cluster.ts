import { Cluster } from 'puppeteer-cluster';
import logger from './logger';

let cluster: Cluster;

export async function launchCluster(): Promise<Cluster> {
  if (!cluster) {
    cluster = await Cluster.launch({
      concurrency: Cluster.CONCURRENCY_CONTEXT,
      maxConcurrency: 4,
      puppeteerOptions: { headless: true },
    });
    logger.info('Cluster launched');
  }
  return cluster;
}
