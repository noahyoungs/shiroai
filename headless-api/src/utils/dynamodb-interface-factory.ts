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
 * Fetch one or multiple items from DynamoDB based on the provided item type and identifiers.
 *
 * This function supports fetching a single item or multiple items at once.
 * It generates the keys based on the item type and identifiers, and optionally allows specifying which
 * attributes to fetch (projection). It handles both single and batch item fetches, ensuring proper sorting
 * of results and logging.
 *
 * @template T - The valid item type, which can be 'user', 'presentation', 'slide', 'topic', or 'source'.
 * @param {T} itemType - The type of item being fetched. Determines the structure of the keys and results.
 * @param {Identifiers<T> | Identifiers<T>[]} identifiers - The identifiers used to generate the primary key (PK) and sort key (SK).
 *        Can be a single identifier object for fetching a single item or an array of identifier objects for batch fetching.
 * @param {string[]} [attributes] - An optional array of attribute names to project (i.e., retrieve specific attributes only).
 * @returns {Promise<Partial<DBItemMap<T>> | DBItemMap<T> | null | (Partial<DBItemMap<T>> | null)[] | (DBItemMap<T> | null)[]>} 
 *          - A promise that resolves with the fetched item(s). Returns `null` if the item does not exist.
 *            When fetching a single item, it returns a single object (or null). When fetching multiple items, 
 *            it returns an array of objects (or null values for missing items).
 *
 * @throws Will throw an error if there is an issue fetching the item(s) from DynamoDB.
 *
 * Example usage:
 * ```typescript
 * const user = await getItems('user', { user_id: '12345' });
 * const slides = await getItems('slide', [
 *   { user_id: '12345', presentation_id: '67890', slide_id: '11111' },
 *   { user_id: '12345', presentation_id: '67890', slide_id: '22222' }
 * ]);
 * ```
 */
export const getItems = dynamoDBInterface.getItems.bind(dynamoDBInterface);

/**
 * Update one or multiple items in DynamoDB.
 *
 * This function allows updating a single item or performing a transactional update of multiple items.
 * It validates the identifiers of each item, builds the appropriate DynamoDB key, and generates the update expression.
 * The function handles single item updates as well as multiple item updates using DynamoDB's `TransactWriteItemsCommand`.
 *
 * @template T - The valid item type, which can be 'user', 'presentation', 'slide', 'topic', or 'source'.
 * @param {T} itemType - The type of item being updated. Determines the structure of the keys and update logic.
 * @param {ItemWithIdentifiers<T>[]} items - An array of items to update. Each item must include the necessary identifiers.
 *        The update expressions are generated based on the remaining properties of each item.
 *
 * @returns {Promise<void>} - A promise that resolves when the update operation is complete.
 *            If there is an error during the update, the function will throw an error.
 *
 * @throws Will throw an error if the update operation fails or if any item is missing required identifiers.
 *
 * Example usage:
 * ```typescript
 * await updateItems('slide', [
 *   { user_id: '12345', presentation_id: '67890', slide_id: '11111', title: 'New Slide Title' },
 *   { user_id: '12345', presentation_id: '67890', slide_id: '22222', content: 'Updated slide content' }
 * ]);
 * ```
 */
export const updateItems = dynamoDBInterface.updateItems.bind(dynamoDBInterface);

/**
 * Delete one or multiple items from DynamoDB.
 *
 * This function allows deleting a single item or multiple items based on the provided item type and identifiers.
 * It builds the keys for each item using the identifiers and performs either a single delete or a transaction delete for multiple items.
 *
 * @template T - The valid item type, which can be 'user', 'presentation', 'slide', 'topic', or 'source'.
 * @param {T} itemType - The type of item being deleted. Determines the structure of the keys.
 * @param {Identifiers<T>[]} identifiers - An array of identifier objects for the items to delete. Each object should contain the required keys.
 * @returns {Promise<void>} - A promise that resolves when the delete operation is complete. If there is an error, the function will throw an error.
 *
 * @throws Will throw an error if the delete operation fails.
 *
 * Example usage:
 * ```typescript
 * await deleteItems('slide', [
 *   { user_id: '12345', presentation_id: '67890', slide_id: '11111' },
 *   { user_id: '12345', presentation_id: '67890', slide_id: '22222' }
 * ]);
 * ```
 */
export const deleteItems = dynamoDBInterface.deleteItems.bind(dynamoDBInterface);

/**
 * Get all items of a specific type (slide, topic, or source) for a specific presentation from DynamoDB.
 *
 * This function fetches all items of a specific type for a given presentation using the user ID and 
 * presentation ID to build the partition key. It scans for items with a matching sort key prefix.
 * 
 * @param {'slide' | 'topic' | 'source'} itemType - The type of items to fetch (slide, topic, or source).
 * @param {string} userID - The user ID associated with the presentation.
 * @param {string} presentationID - The presentation ID for which to fetch items.
 * @param {string[]} [attributes] - An optional array of attribute names to fetch. If provided, only these attributes will be fetched.
 * @returns {Promise<Slide[] | Topic[] | Source[]>} - A promise that resolves with an array of items depending on the item type.
 *
 * @throws Will throw an error if the fetch operation fails.
 */
export const getAllItemsForPresentation = dynamoDBInterface.getAllItemsForPresentation.bind(dynamoDBInterface);

/**
 * Delete all items for a specific presentation from DynamoDB.
 *
 * This function deletes all items of a specific type (slide, topic, or source) for a given presentation.
 * It first queries the items by their partition and sort keys, then deletes them in batches.
 *
 * @param {'slide' | 'topic' | 'source'} itemType - The type of items to delete (slide, topic, or source).
 * @param {string} userID - The user ID associated with the presentation.
 * @param {string} presentationID - The presentation ID for which to delete items.
 * @returns {Promise<void>} - A promise that resolves when all items are deleted. If there are no items, the function completes without error.
 *
 * @throws Will throw an error if the delete operation fails.
 *
 * Example usage:
 * ```typescript
 * await deleteAllItemsForPresentation('12345', '67890', 'slide');
 * ```
 */
export const deleteAllItemsForPresentation = dynamoDBInterface.deleteAllItemsForPresentation.bind(dynamoDBInterface);