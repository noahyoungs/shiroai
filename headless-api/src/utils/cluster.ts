import { Cluster } from 'puppeteer-cluster';
import globalLogger from './logger';

let cluster: Cluster;

export async function launchCluster(): Promise<Cluster> {
  if (!cluster) {
    cluster = await Cluster.launch({
      concurrency: Cluster.CONCURRENCY_CONTEXT,
      maxConcurrency: 6,
      timeout: 30000,
      puppeteerOptions: { headless: true },
    });
    globalLogger.info('Cluster launched');
  }
  return cluster;
}
