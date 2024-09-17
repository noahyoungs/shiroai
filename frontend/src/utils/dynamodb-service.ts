"use server"
// import path is "@/utils/dynamodb-service"
import * as dynamoDBInterface from "@/utils/dynamodb-interface-factory";
import { Identifiers, ItemWithIdentifiers, ValidItemTypes } from "@shared-utils/database-types";
import { Slide, Topic, Source } from "@shared-utils/database-types";
import { auth } from "@/auth";

/**
 * Function to fetch authenticated user ID from the session
 */
export async function getAuthenticatedUserId(): Promise<string> {
  // Fetch the session data using the auth function
  const session = await auth();

  // Check if the user object and user id are available in the session
  if (!session || !session.user || !session.user.id) {
    // Throw an error if the user is not authenticated
    throw new Error("User is not authenticated. Database calls should not be made.");
  }

  // Return the user id from the session
  return session.user.id;
}

/**
 * Fetch one or multiple items from DynamoDB based on the provided item type and identifiers.
 * This wrapper function automatically injects the authenticated user's ID, eliminating the need 
 * to pass the user ID manually.
 *
 * This function supports fetching a single item or multiple items at once. It generates the keys 
 * based on the item type and identifiers, and optionally allows specifying which attributes to fetch 
 * (projection). It handles both single and batch item fetches, ensuring proper sorting of results 
 * and logging.
 *
 * @template T - The valid item type, which can be 'user', 'presentation', 'slide', 'topic', or 'source'.
 * @param {T} itemType - The type of item being fetched. Determines the structure of the keys and results.
 * @param {Omit<Identifiers<T>, "user_id"> | Omit<Identifiers<T>, "user_id">[]} identifiers - The identifiers 
 *        used to generate the primary key (PK) and sort key (SK), excluding the user_id.
 *        Can be a single identifier object for fetching a single item or an array of identifier objects 
 *        for batch fetching.
 * @param {string[]} [attributes] - An optional array of attribute names to project (i.e., retrieve specific 
 *        attributes only).
 * @returns {Promise<Partial<DBItemMap<T>> | DBItemMap<T> | null | (Partial<DBItemMap<T>> | null)[] | (DBItemMap<T> | null)[]>} 
 *          - A promise that resolves with the fetched item(s). Returns `null` if the item does not exist.
 *            When fetching a single item, it returns a single object (or null). When fetching multiple items, 
 *            it returns an array of objects (or null values for missing items).
 *
 * @throws Will throw an error if the user is not authenticated or if there is an issue fetching the item(s) 
 *         from DynamoDB.
 *
 * Example usage:
 * ```typescript
 * const user = await getItemsWithAuth('user', {});
 * const slides = await getItemsWithAuth('slide', [
 *   { presentation_id: '67890', slide_id: '11111' },
 *   { presentation_id: '67890', slide_id: '22222' }
 * ]);
 * ```
 */
export async function getItemsWithAuth<T extends ValidItemTypes>(
  itemType: T,
  identifiers: Omit<Identifiers<T>, "user_id"> | Omit<Identifiers<T>, "user_id">[],
  attributes?: string[]
) {
  const userId = await getAuthenticatedUserId();

  // Add the user_id to the identifiers and cast them to the appropriate type
  const enrichedIdentifiers = Array.isArray(identifiers)
    ? (identifiers.map(id => ({ ...id, user_id: userId })) as Identifiers<T>[])
    : ({ ...identifiers, user_id: userId } as Identifiers<T>);

  // Call the original function with the enriched identifiers
  return dynamoDBInterface.getItems(itemType, enrichedIdentifiers, attributes);
}

/**
 * Update one or multiple items in DynamoDB.
 * This wrapper function automatically injects the authenticated user's ID, unless the `user_id`
 * is provided in the items. If `user_id` is included, it validates that it matches the authenticated user's ID.
 * 
 * This function allows updating a single item or performing a transactional update of multiple items.
 * It validates the identifiers of each item, builds the appropriate DynamoDB key, and generates the 
 * update expression. The function handles single item updates as well as multiple item updates using 
 * DynamoDB's `TransactWriteItemsCommand`.
 *
 * @template T - The valid item type, which can be 'user', 'presentation', 'slide', 'topic', or 'source'.
 * @param {T} itemType - The type of item being updated. Determines the structure of the keys and update logic.
 * @param {Omit<ItemWithIdentifiers<T>, "user_id">[] | ItemWithIdentifiers<T>[]} items - An array of items 
 *        to update. The items may optionally include the `user_id`. If `user_id` is present, it will be 
 *        validated against the authenticated user's ID. If `user_id` is missing, the function will automatically 
 *        assign the authenticated user's ID.
 *
 * @returns {Promise<void>} - A promise that resolves when the update operation is complete.
 *            If there is an error during the update, the function will throw an error.
 *
 * @throws Will throw an error if the user is not authenticated, if the update operation fails, 
 *         or if any item has a `user_id` that doesn't match the authenticated user's ID.
 *
 * Example usage:
 * ```typescript
 * await updateItemsWithAuth('slide', [
 *   { presentation_id: '67890', slide_id: '11111', title: 'New Slide Title' },
 *   { presentation_id: '67890', slide_id: '22222', content: 'Updated slide content', user_id: '12345' }
 * ]);
 * ```
 * In this example, the first item is missing `user_id`, so it will be enriched with the authenticated user's ID.
 * The second item includes `user_id`, so it will be validated against the authenticated user's ID before proceeding.
 */
export async function updateItemsWithAuth<T extends ValidItemTypes>(
  itemType: T,
  items: Omit<ItemWithIdentifiers<T>, "user_id">[] | ItemWithIdentifiers<T>[]
): Promise<void> {
  const userId = await getAuthenticatedUserId();

  // Check each item to ensure the user_id matches or is missing (optional user_id)
  const enrichedItems = items.map(item => {
    // Type guard to check if user_id exists on the item
    if ('user_id' in item) {
      // If user_id is included, validate it matches the authenticated user
      if (item.user_id && item.user_id !== userId) {
        throw new Error(`Mismatched user_id. Authenticated user ID does not match the provided user_id.`);
      }

      // If user_id matches or is missing, proceed with the item
      return { ...item };  // user_id is already in the item, no need to add
    } else {
      // If user_id is not present, add the authenticated user_id
      return {
        ...item,
        user_id: userId,
      };
    }
  }) as ItemWithIdentifiers<T>[];

  // Proceed with the update using the enriched items
  return dynamoDBInterface.updateItems(itemType, enrichedItems);
}

/**
 * Delete one or multiple items from DynamoDB.
 * This wrapper function automatically injects the authenticated user's ID, eliminating the need 
 * to pass the user ID manually.
 *
 * This function allows deleting a single item or multiple items based on the provided item type 
 * and identifiers. It builds the keys for each item using the identifiers and performs either 
 * a single delete or a transaction delete for multiple items.
 *
 * @template T - The valid item type, which can be 'user', 'presentation', 'slide', 'topic', or 'source'.
 * @param {T} itemType - The type of item being deleted. Determines the structure of the keys.
 * @param {Omit<Identifiers<T>, "user_id">[]} identifiers - An array of identifier objects for the items 
 *        to delete, excluding the user_id. Each object should contain the required keys.
 * @returns {Promise<void>} - A promise that resolves when the delete operation is complete. If there 
 *            is an error, the function will throw an error.
 *
 * @throws Will throw an error if the user is not authenticated or if the delete operation fails.
 *
 * Example usage:
 * ```typescript
 * await deleteItemsWithAuth('slide', [
 *   { presentation_id: '67890', slide_id: '11111' },
 *   { presentation_id: '67890', slide_id: '22222' }
 * ]);
 * ```
 */
export async function deleteItemsWithAuth<T extends ValidItemTypes>(
  itemType: T,
  identifiers: Omit<Identifiers<T>, "user_id">[]
): Promise<void> {
  const userId = await getAuthenticatedUserId();

  // Add the user_id to the identifiers and cast them to the appropriate type
  const enrichedIdentifiers = identifiers.map(id => ({ ...id, user_id: userId })) as Identifiers<T>[];

  // Call the original function with the enriched identifiers
  return dynamoDBInterface.deleteItems(itemType, enrichedIdentifiers);
}

/**
 * Get all slides for a specific presentation from DynamoDB.
 * This wrapper function automatically injects the authenticated user's ID, eliminating the need 
 * to pass the user ID manually.
 *
 * This function fetches all slides for a given presentation. It uses the authenticated user ID 
 * and presentation ID to build the partition key and scans for items with a matching sort key prefix.
 *
 * @param {string} presentationID - The presentation ID for which to fetch slides.
 * @param {string[]} [attributes] - An optional array of attribute names to fetch. If provided, only 
 *        these attributes will be fetched.
 * @returns {Promise<Slide[]>} - A promise that resolves with an array of slides. Returns an empty array if no slides are found.
 *
 * @throws Will throw an error if the user is not authenticated or if the fetch operation fails.
 */
export async function getAllItemsForPresentationWithAuth(
  itemType: "slide",
  presentationID: string,
  attributes?: string[]
): Promise<Slide[]>;

/**
 * Get all topics for a specific presentation from DynamoDB.
 * This wrapper function automatically injects the authenticated user's ID, eliminating the need 
 * to pass the user ID manually.
 *
 * This function fetches all topics for a given presentation. It uses the authenticated user ID 
 * and presentation ID to build the partition key and scans for items with a matching sort key prefix.
 *
 * @param {string} presentationID - The presentation ID for which to fetch topics.
 * @param {string[]} [attributes] - An optional array of attribute names to fetch. If provided, only 
 *        these attributes will be fetched.
 * @returns {Promise<Topic[]>} - A promise that resolves with an array of topics. Returns an empty array if no topics are found.
 *
 * @throws Will throw an error if the user is not authenticated or if the fetch operation fails.
 */
export async function getAllItemsForPresentationWithAuth(
  itemType: "topic",
  presentationID: string,
  attributes?: string[]
): Promise<Topic[]>;

/**
 * Get all sources for a specific presentation from DynamoDB.
 * This wrapper function automatically injects the authenticated user's ID, eliminating the need 
 * to pass the user ID manually.
 *
 * This function fetches all sources for a given presentation. It uses the authenticated user ID 
 * and presentation ID to build the partition key and scans for items with a matching sort key prefix.
 *
 * @param {string} presentationID - The presentation ID for which to fetch sources.
 * @param {string[]} [attributes] - An optional array of attribute names to fetch. If provided, only 
 *        these attributes will be fetched.
 * @returns {Promise<Source[]>} - A promise that resolves with an array of sources. Returns an empty array if no sources are found.
 *
 * @throws Will throw an error if the user is not authenticated or if the fetch operation fails.
 */
export async function getAllItemsForPresentationWithAuth(
  itemType: "source",
  presentationID: string,
  attributes?: string[]
): Promise<Source[]>;

/**
 * Get all items for a specific presentation from DynamoDB.
 * This wrapper function automatically injects the authenticated user's ID, eliminating the need 
 * to pass the user ID manually.
 *
 * This function fetches all items of a specific type (slide, topic, or source) for a given presentation.
 * It uses the authenticated user ID and presentation ID to build the partition key and scans for items 
 * with a matching sort key prefix.
 *
 * @param {'slide' | 'topic' | 'source'} itemType - The type of items to fetch (slide, topic, or source).
 * @param {string} presentationID - The presentation ID for which to fetch items.
 * @param {string[]} [attributes] - An optional array of attribute names to fetch. If provided, only 
 *        these attributes will be fetched.
 * @returns {Promise<Slide[] | Topic[] | Source[]>} - A promise that resolves with an array of items. 
 *          Returns an empty array if no items are found.
 *
 * @throws Will throw an error if the user is not authenticated or if the fetch operation fails.
 *
 * Example usage:
 * ```typescript
 * const slides = await getAllItemsForPresentationWithAuth("slide", "67890");
 * const topics = await getAllItemsForPresentationWithAuth("topic", "67890", ["title", "description"]);
 * const sources = await getAllItemsForPresentationWithAuth("source", "67890");
 * ```
 */
export async function getAllItemsForPresentationWithAuth(
  itemType: "slide" | "topic" | "source",
  presentationID: string,
  attributes?: string[]
): Promise<Slide[] | Topic[] | Source[]> {
  const userId = await getAuthenticatedUserId();

  // Use a type guard to narrow down the itemType
  if (itemType === "slide") {
    return dynamoDBInterface.getAllItemsForPresentation("slide", userId, presentationID, attributes);
  } else if (itemType === "topic") {
    return dynamoDBInterface.getAllItemsForPresentation("topic", userId, presentationID, attributes);
  } else {
    return dynamoDBInterface.getAllItemsForPresentation("source", userId, presentationID, attributes);
  }
}

/**
 * Delete all items for a specific presentation from DynamoDB.
 * This wrapper function automatically injects the authenticated user's ID, eliminating the need 
 * to pass the user ID manually.
 *
 * This function deletes all items of a specific type (slide, topic, or source) for a given presentation.
 * It first queries the items by their partition and sort keys, then deletes them in batches.
 *
 * @param {'slide' | 'topic' | 'source'} itemType - The type of items to delete (slide, topic, or source).
 * @param {string} presentationID - The presentation ID for which to delete items.
 * @returns {Promise<void>} - A promise that resolves when all items are deleted. If there are no items, 
 *          the function completes without error.
 *
 * @throws Will throw an error if the user is not authenticated or if the delete operation fails.
 *
 * Example usage:
 * ```typescript
 * await deleteAllItemsForPresentationWithAuth('67890', 'slide');
 * ```
 */
export async function deleteAllItemsForPresentationWithAuth(
  itemType: "slide" | "topic" | "source",
  presentationID: string,
): Promise<void> {
  const userId = await getAuthenticatedUserId();

  // Call the original function with the authenticated user ID
  return dynamoDBInterface.deleteAllItemsForPresentation(itemType, userId, presentationID);
}


/**
 * Fetch presentations for the authenticated user.
 * This wrapper function automatically injects the authenticated user's ID, eliminating the need 
 * to pass the user ID manually.
 *
 * @param {string} [gsi1sk] - Optional GSI1SK value to start fetching from (for pagination).
 * @param {number} [n=25] - Number of items to fetch (default: 25).
 * @returns {Promise<Array<{presentation_id: string, topic: string, gsi1sk: string, status: string}>>} - Array of presentation objects.
 *
 * @throws Will throw an error if the user is not authenticated or if there's an issue fetching the presentations.
 *
 * Example usage:
 * ```typescript
 * const presentations = await fetchPresentationsForAuthenticatedUser();
 * // For pagination:
 * const nextPage = await fetchPresentationsForAuthenticatedUser(lastFetchedGSI1SK);
 * ```
 */
export async function fetchPresentationsForAuthenticatedUser(
  gsi1sk?: string,
  n: number = 25
): Promise<Array<{presentation_id: string, topic: string, gsi1sk: string, status: string}>> {
  const userId = await getAuthenticatedUserId();

  try {
    return await dynamoDBInterface.fetchPresentations(userId, gsi1sk, n);
  } catch (error) {
    console.error('Error fetching presentations for authenticated user:', error);
    throw error;
  }
}