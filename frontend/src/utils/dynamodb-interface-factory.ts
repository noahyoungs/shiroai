// frontend/src/utils/dynamodb-interface-factory.ts

import { DynamoDBInterface } from '@shared-utils/dynamodb-interface';
import { getChildLogger } from './logger';
import { DynamoDBClient } from '@aws-sdk/client-dynamodb';

const logger = getChildLogger(import.meta.url);

const client = new DynamoDBClient({});
const tableName = process.env.DYNAMODB_TABLE_NAME as string;

if (!tableName) {
  const errorMessage = "DYNAMODB_TABLE_NAME environment variable is not set";
  logger.fatal(errorMessage);
  throw new Error(errorMessage);
}

logger.info("DynamoDB client initialized");

const dynamoDBInterface = new DynamoDBInterface(logger, client, tableName);

/**
 * Fetch items from DynamoDB.
 * @param key - The key of the item to fetch.
 */
export const getItems = dynamoDBInterface.getItems.bind(dynamoDBInterface);

/**
 * Update items in DynamoDB.
 * @param key - The key of the item to update.
 * @param data - The data to update.
 */
export const updateItems = dynamoDBInterface.updateItems.bind(dynamoDBInterface);

/**
 * Delete items from DynamoDB.
 * @param key - The key of the item to delete.
 */
export const deleteItems = dynamoDBInterface.deleteItems.bind(dynamoDBInterface);

/**
 * Get all items for a presentation.
 * @param presentationId - The ID of the presentation.
 */
export const getAllItemsForPresentation = dynamoDBInterface.getAllItemsForPresentation.bind(dynamoDBInterface);

/**
 * Delete all items for a presentation.
 * @param presentationId - The ID of the presentation.
 */
export const deleteAllItemsForPresentation = dynamoDBInterface.deleteAllItemsForPresentation.bind(dynamoDBInterface);