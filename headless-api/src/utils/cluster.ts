import { Cluster } from 'puppeteer-cluster';
import globalLogger from './logger';

let cluster: Cluster;

export async function launchCluster(): Promise<Cluster> {
  if (!cluster) {
    cluster = await Cluster.launch({
      concurrency: Cluster.CONCURRENCY_CONTEXT,
      maxConcurrency: 4,
      puppeteerOptions: { headless: true },
    });
    globalLogger.info('Cluster launched');
  }
  return cluster;
}
