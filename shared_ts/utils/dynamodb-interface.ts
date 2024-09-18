import {
  DynamoDBClient,
  GetItemCommand,
  BatchGetItemCommand,
  UpdateItemCommand,
  TransactWriteItemsCommand,
  DeleteItemCommand,
  QueryCommand,
  QueryCommandInput,
} from "@aws-sdk/client-dynamodb";
import { marshall, unmarshall } from "@aws-sdk/util-dynamodb";
import { ValidItemTypes, Identifiers, DBItemMap, ItemWithIdentifiers, Slide, Topic, Source } from "./database-types";
import { AttributeValue } from "@aws-sdk/client-dynamodb";
import { Logger } from "pino";

const itemIdsByType: Record<ValidItemTypes, string[]> = {
  user: ['user_id'],
  presentation: ['user_id', 'presentation_id'],
  slide: ['user_id', 'presentation_id', 'slide_id'],
  topic: ['user_id', 'presentation_id', 'topic_id'],
  source: ['user_id', 'presentation_id', 'source_id']
}

export class DynamoDBInterface {
  private client: DynamoDBClient;
  private tableName: string;
  private logger: Logger;

  constructor(logger: Logger, client: DynamoDBClient, tableName: string) {
    this.client = client;
    this.tableName = tableName;
    this.logger = logger;
  }


  // Utility functions

  // Centralized logging and key building logic
  private logAndBuildKey<T extends ValidItemTypes>(itemType: T, identifiers: Identifiers<T>): { PK: string; SK: string } {
    this.logger.debug(`Building key for ${itemType} with identifiers: ${JSON.stringify(identifiers)}`);
    return this.buildKey(itemType, identifiers);
  }

  // Build key based on item type and check for missing identifiers
  private buildKey<T extends ValidItemTypes>(itemType: T, identifiers: Identifiers<T>): { PK: string; SK: string } {
    const keyMap: Record<ValidItemTypes, () => { PK: string; SK: string }> = {
      user: () => {
        if (!('user_id' in identifiers)) {
          this.throwMissingIdentifierError('user_id', itemType);
        }
        return { PK: `USER#${identifiers.user_id}`, SK: `PROFILE` };
      },
      presentation: () => {
        if (!('user_id' in identifiers) || !('presentation_id' in identifiers)) {
          this.throwMissingIdentifierError('user_id, presentation_id', itemType);
        }
        return { PK: `USER#${identifiers.user_id}`, SK: `PRESENTATION#${identifiers.presentation_id}` };
      },
      slide: () => {
        if (!('user_id' in identifiers) || !('presentation_id' in identifiers) || !('slide_id' in identifiers)) {
          this.throwMissingIdentifierError('user_id, presentation_id, slide_id', itemType);
        }
        return { PK: `USER#${identifiers.user_id}`, SK: `PRESENTATION#${identifiers.presentation_id}#SLIDE#${identifiers.slide_id}` };
      },
      topic: () => {
        if (!('user_id' in identifiers) || !('presentation_id' in identifiers) || !('topic_id' in identifiers)) {
          this.throwMissingIdentifierError('user_id, presentation_id, topic_id', itemType);
        }
        return { PK: `USER#${identifiers.user_id}`, SK: `PRESENTATION#${identifiers.presentation_id}#TOPIC#${identifiers.topic_id}` };
      },
      source: () => {
        if (!('user_id' in identifiers) || !('presentation_id' in identifiers) || !('source_id' in identifiers)) {
          this.throwMissingIdentifierError('user_id, presentation_id, source_id', itemType);
        }
        return { PK: `USER#${identifiers.user_id}`, SK: `PRESENTATION#${identifiers.presentation_id}#SOURCE#${identifiers.source_id}` };
      },
    };

    const buildFn = keyMap[itemType];
    if (!buildFn) {
      const errorMessage = `Invalid item type: ${itemType}`;
      this.logger.error(errorMessage);
      throw new Error(errorMessage);
    }

    return buildFn();
  }

  // Helper function to throw an error for missing identifiers
  private throwMissingIdentifierError(missingIdentifiers: string, itemType: ValidItemTypes): never {
    const errorMessage = `Missing required identifiers: ${missingIdentifiers} for item type: ${itemType}`;
    this.logger.error(errorMessage);
    throw new Error(errorMessage);
  }

  // Build GSI1SK based on presentationID and check for missing presentationID
  private buildGSI1SK(): string {
    const gsi1sk = `LASTUPDATE#${Date.now()}`;
    this.logger.debug(`Generated GSI1SK: ${gsi1sk}`);
    return gsi1sk;
  }

  // Add identifiers based on item type
  private addIdentifiersToItem(item: any, itemType: ValidItemTypes) {
    this.logger.debug(`Adding identifiers to item of type ${itemType}`);

    const { PK, SK, GSI1SK } = item;

    // Error if no PK or SK
    if (!PK || !SK) {
      const errorMessage = `invalid required keys PK (${PK}) and/or SK (${SK}) in item`;
      this.logger.error(errorMessage);
      throw new Error(errorMessage);
    }

    const ids: Record<string, string> = {
      user_id: PK.split('#')[1],
    };

    if (itemType === 'presentation') {
      try {
        if (GSI1SK.startsWith('LASTUPDATED#')) {
          const gsiParts = GSI1SK.split('#');
          ids.last_updated = gsiParts[1]; // Extract the timestamp part
        } else {
          throw new Error('Invalid GSI1SK format');
        }
      } catch (error: any) {
        this.logger.warn({ error, GSI1SK }, 'Error parsing GSI1SK for, last_updated not added to item');
      }
    }

    const skParts = SK.split('#');

    // Extract presentation_id for all item types except 'user'
    if (itemType !== 'user') {
      if (skParts.length < 2) {
        const errorMessage = `SK format is invalid for item type ${itemType}: ${SK}`;
        this.logger.error(errorMessage);
        throw new Error(errorMessage);
      }
      ids.presentation_id = skParts[1];
    }

    // Extract specific IDs based on item type
    if (itemType === 'presentation') {
      // Already handled above
    } else if (itemType === 'slide') {
      if (skParts.length < 4) {
        const errorMessage = `SK format is invalid for slide: ${SK}`;
        this.logger.error(errorMessage);
        throw new Error(errorMessage);
      }
      ids.slide_id = skParts[3];
    } else if (itemType === 'topic') {
      if (skParts.length < 4) {
        const errorMessage = `SK format is invalid for topic: ${SK}`;
        this.logger.error(errorMessage);
        throw new Error(errorMessage);
      }
      ids.topic_id = skParts[3];
    } else if (itemType === 'source') {
      if (skParts.length < 4) {
        const errorMessage = `SK format is invalid for source: ${SK}`;
        this.logger.error(errorMessage);
        throw new Error(errorMessage);
      }
      ids.source_id = skParts[3];
    }

    this.logger.debug(`Identifiers added to item: ${JSON.stringify(ids)}`);
    return { ...item, ...ids };
  }

  // Remove keys from item
  private removeKeysFromItem(item: any) {
  this.logger.debug(`Removing keys (PK, SK, GSI1SK) from item`);
  const { PK, SK, GSI1SK, ...rest } = item;
  return rest;
}

// Fetch single item
private async fetchSingleItem<T extends ValidItemTypes>(
  itemType: T,
  requestKey: { PK: string; SK: string },
  projectionExpression?: string,
  expressionAttributeNames?: Record<string, string>
) {
  const commandInput = {
    TableName: this.tableName,
    Key: marshall(requestKey),
    ...(projectionExpression && { ProjectionExpression: projectionExpression }),
    ...(expressionAttributeNames && { ExpressionAttributeNames: expressionAttributeNames }),
  };

  try {
    const command = new GetItemCommand(commandInput);
    const response = await this.client.send(command);
    const item = response.Item ? unmarshall(response.Item) : null;

    this.logger.debug(`Single item fetched for type ${itemType}: ${JSON.stringify(item)}`);
    this.logger.info(`Single item fetched for type ${itemType}: ${item ? 'non-null (found)' : 'null (not found)'}`);
    return item ? this.removeKeysFromItem(this.addIdentifiersToItem(item, itemType)) as (Partial<DBItemMap<T>> | DBItemMap<T>) : null;
  } catch (error: any) {
    this.logger.error({ error, commandInput }, `Error fetching item for type ${itemType}`);
    throw error;
  }
}

// Fetch multiple items
private async fetchMultipleItems<T extends ValidItemTypes>(
  itemType: T,
  requestKeys: { PK: string; SK: string }[],
  projectionExpression?: string,
  expressionAttributeNames?: Record<string, string>
) {
  const commandInput = {
    RequestItems: {
      [this.tableName]: {
        Keys: requestKeys.map(key => marshall(key)),
        ...(projectionExpression && { ProjectionExpression: projectionExpression }),
        ...(expressionAttributeNames && { ExpressionAttributeNames: expressionAttributeNames }),
      },
    },
  };

  try {
    const command = new BatchGetItemCommand(commandInput);
    const response = await this.client.send(command);
    const items = response.Responses?.[this.tableName]?.map((item: Record<string, AttributeValue>) => unmarshall(item)) || [];

    this.logger.debug(`Items fetched from db (unsorted): ${JSON.stringify(items)}`);

    const itemMap = items.reduce((acc, item) => {
      acc[`${item.PK}_${item.SK}`] = item;
      return acc;
    }, {} as Record<string, any>);

    const resultItems = requestKeys.map((requestKey) => {
      const itemKey = `${requestKey.PK}_${requestKey.SK}`;
      const matchingItem = itemMap[itemKey];
      return matchingItem ? this.removeKeysFromItem(this.addIdentifiersToItem(matchingItem, itemType)) as (Partial<DBItemMap<T>> | DBItemMap<T>) : null;
    });

    this.logger.debug(`Items fetched for type ${itemType} (sorted): ${JSON.stringify(resultItems)}`);
    this.logger.info(`${resultItems.length} items fetched for type ${itemType}, ${resultItems.filter(Boolean).length} non-null (found)`);
    return resultItems as (Partial<DBItemMap<T>> | DBItemMap<T>)[];
  } catch (error: any) {
    this.logger.error({ error, commandInput }, `Error fetching items for type ${itemType}`);
    throw error;
  }
}

// Utility function to validate and extract identifiers
private validateIdentifiers<T extends ValidItemTypes>(
  itemType: T,
  item: Partial<ItemWithIdentifiers<T>>
): Identifiers<T> {
  // Define the required fields for each item type
  const requiredFieldsMap: Record<ValidItemTypes, (keyof Identifiers<T>)[]> = {
    user: ['user_id'] as (keyof Identifiers<T>)[],
    presentation: ['user_id', 'presentation_id'] as (keyof Identifiers<T>)[],
    slide: ['user_id', 'presentation_id', 'slide_id'] as (keyof Identifiers<T>)[],
    topic: ['user_id', 'presentation_id', 'topic_id'] as (keyof Identifiers<T>)[],
    source: ['user_id', 'presentation_id', 'source_id'] as (keyof Identifiers<T>)[],
  };

  // Get the required fields for the given item type
  const requiredFields = requiredFieldsMap[itemType];

  // Create an object to hold the validated identifiers
  const identifiers = {} as Identifiers<T>;

  // Check if any required fields are missing
  for (const field of requiredFields) {
    const value = item[field];
    if (value === undefined || value === null) {
      throw new Error(`Missing required identifier '${String(field)}' for item type: ${itemType}`);
    }

    // Assign the value to the identifiers object after ensuring it's not undefined or null
    identifiers[field] = value as Identifiers<T>[typeof field];
  }

  return identifiers;
}

private getUpdateExpression<T extends ValidItemTypes>(
  item: ItemWithIdentifiers<T>,
  itemType: T
): [string, Record<string, any>, Record<string, any>] {
  this.logger.debug(`Generating update expression for item of type ${itemType}`);

  const omitAttributes = ['PK', 'SK', 'GSI1SK', 'last_updated'].concat(itemIdsByType[itemType]);
  let updateExpression = "SET ";
  const expressionAttributeValues: Record<string, any> = {};
  const expressionAttributeNames: Record<string, string> = {};

  // Iterate over the keys of the item and generate the update expression
  (Object.keys(item) as Array<keyof ItemWithIdentifiers<T>>).forEach((key, index) => {
    const value = item[key];

    // Log a warning if the value is undefined
    if (value === undefined) {
      this.logger.warn(`A value for attribute '${key as string}' is undefined. This attribute will be skipped.`);
      return; // Skip this iteration if the value is undefined
    }

    if (!omitAttributes.includes(key as string)) {
      const attrKey = `#attr${index}`;
      const valueKey = `:val${index}`;

      updateExpression += `${attrKey} = ${valueKey}, `;
      expressionAttributeNames[attrKey] = key as string;
      expressionAttributeValues[valueKey] = value;
    }
  });

  // Handle GSI1SK for presentation
  if (itemType == 'presentation') {
    const gsi1sk = this.buildGSI1SK();
    updateExpression += "#GSI1SK = :gsi1sk, ";
    expressionAttributeNames["#GSI1SK"] = "GSI1SK";
    expressionAttributeValues[":gsi1sk"] = gsi1sk;
  }

  // Remove trailing comma and space
  updateExpression = updateExpression.slice(0, -2);
  this.logger.debug(`Update expression generated: ${updateExpression}`);

  return [updateExpression, expressionAttributeNames, marshall(expressionAttributeValues)];
}


// Main CRUD operations

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
public async getItems<T extends ValidItemTypes>(
  itemType: T,
  identifiers: Identifiers<T> | Identifiers<T>[],
  attributes?: string[]
): Promise<
  | Partial<DBItemMap<T>>
  | DBItemMap<T>
  | null
  | (Partial<DBItemMap<T>> | null)[]
  | (DBItemMap<T> | null)[]
> {
  this.logger.info(`Fetching items of type ${itemType} with identifiers: ${JSON.stringify(identifiers)}`);

  const isSingle = !Array.isArray(identifiers);
  const requestKeys = (isSingle ? [identifiers] : identifiers).map(id => this.logAndBuildKey(itemType, id));

  let projectionExpression: string | undefined;
  let expressionAttributeNames: Record<string, string> | undefined;

  if (attributes && attributes.length > 0) {
    const allAttributes = ['PK', 'SK', 'GSI1SK', ...attributes];
    projectionExpression = allAttributes.map((attr, index) => `#attr${index}`).join(", ");
    expressionAttributeNames = allAttributes.reduce((acc, attr, index) => {
      acc[`#attr${index}`] = attr;
      return acc;
    }, {} as Record<string, string>);
  }

  if (isSingle) {
    return this.fetchSingleItem(itemType, requestKeys[0], projectionExpression, expressionAttributeNames);
  } else {
    return this.fetchMultipleItems(itemType, requestKeys, projectionExpression, expressionAttributeNames);
  }
}


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
public async updateItems<T extends ValidItemTypes>(
  itemType: T,
  items: ItemWithIdentifiers<T>[]
): Promise<void> {
  this.logger.info(`Updating items of type ${itemType}`);

  const transactItems = items.map(item => {
    // Check that the necessary identifiers are present (this is now guaranteed by types)
    const identifiers = this.validateIdentifiers(itemType, item);

    const key = this.logAndBuildKey(itemType, identifiers);
    const [updateExpression, expressionAttributeNames, expressionAttributeValues] = this.getUpdateExpression(item, itemType);

    return {
      Update: {
        TableName: this.tableName,
        Key: marshall(key),
        UpdateExpression: updateExpression,
        ExpressionAttributeNames: expressionAttributeNames,
        ExpressionAttributeValues: expressionAttributeValues,
      }
    };
  });

  try {
    if (items.length === 1) {
      this.logger.debug(`Updating a single item`);
      await this.client.send(new UpdateItemCommand(transactItems[0].Update));
    } else {
      this.logger.debug(`Performing transaction write for multiple items`);
      await this.client.send(new TransactWriteItemsCommand({ TransactItems: transactItems }));
    }
    this.logger.info(`Items successfully updated`);
  } catch (error: any) {
    this.logger.error({ error, items }, `Error updating items for type ${itemType}`);
    throw error;
  }
}


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
public async deleteItems<T extends ValidItemTypes>(
  itemType: T,
  identifiers: Identifiers<T>[]
): Promise<void> {
  this.logger.info(`Deleting items of type ${itemType}`);

  const deleteItems = identifiers.map(id => {
    const key = this.buildKey(itemType, id);
    return {
      Delete: {
        TableName: this.tableName,
        Key: marshall(key),
      }
    };
  });

  try {
    if (identifiers.length === 1) {
      this.logger.debug(`Deleting a single item`);
      await this.client.send(new DeleteItemCommand({
        TableName: this.tableName,
        Key: marshall(this.buildKey(itemType, identifiers[0])),
      }));
    } else {
      this.logger.debug(`Performing transaction delete for multiple items`);
      await this.client.send(new TransactWriteItemsCommand({ TransactItems: deleteItems }));
    }
    this.logger.info(`Items successfully deleted`);
  } catch (error: any) {
    this.logger.error({ error, identifiers }, `Error deleting items for type ${itemType}`);
    throw error;
  }
}

// Define overloads for the getAllItemsForPresentation function to specify return types based on itemType
/**
 * Get all slides for a specific presentation from DynamoDB.
 * 
 * @param {string} userID - The user ID associated with the presentation.
 * @param {string} presentationID - The presentation ID for which to fetch slides.
 * @param {string[]} [attributes] - An optional array of attribute names to fetch. If provided, only these attributes will be fetched.
 * @returns {Promise<Slide[]>} - A promise that resolves with an array of slides.
 *
 * @throws Will throw an error if the fetch operation fails.
 */
public async getAllItemsForPresentation(
  itemType: 'slide',
  userID: string,
  presentationID: string,
  attributes?: string[]
): Promise<Slide[]>;

/**
 * Get all topics for a specific presentation from DynamoDB.
 * 
 * @param {string} userID - The user ID associated with the presentation.
 * @param {string} presentationID - The presentation ID for which to fetch topics.
 * @param {string[]} [attributes] - An optional array of attribute names to fetch. If provided, only these attributes will be fetched.
 * @returns {Promise<Topic[]>} - A promise that resolves with an array of topics.
 *
 * @throws Will throw an error if the fetch operation fails.
 */
public async getAllItemsForPresentation(
  itemType: 'topic',
  userID: string,
  presentationID: string,
  attributes?: string[]
): Promise<Topic[]>;

/**
 * Get all sources for a specific presentation from DynamoDB.
 * 
 * @param {string} userID - The user ID associated with the presentation.
 * @param {string} presentationID - The presentation ID for which to fetch sources.
 * @param {string[]} [attributes] - An optional array of attribute names to fetch. If provided, only these attributes will be fetched.
 * @returns {Promise<Source[]>} - A promise that resolves with an array of sources.
 *
 * @throws Will throw an error if the fetch operation fails.
 */
public async getAllItemsForPresentation(
  itemType: 'source',
  userID: string,
  presentationID: string,
  attributes?: string[]
): Promise<Source[]>;

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
public async getAllItemsForPresentation(
  itemType: 'slide' | 'topic' | 'source',
  userID: string,
  presentationID: string,
  attributes?: string[]
): Promise<Slide[] | Topic[] | Source[]> {
  this.logger.info(`Fetching all ${itemType}s for presentation ${presentationID}`);

  const pk = `USER#${userID}`;
  const skPrefix = `PRESENTATION#${presentationID}#${itemType.toUpperCase()}#`;

  let projectionExpression: string | undefined;
  let expressionAttributeNames: Record<string, string> = {};

  if (attributes && attributes.length > 0) {
    const allAttributes = ['PK', 'SK', 'GSI1SK', ...attributes];
    projectionExpression = allAttributes.map((attr, index) => `#attr${index}`).join(", ");
    allAttributes.forEach((attr, index) => {
      expressionAttributeNames[`#attr${index}`] = attr;
    });
  }

  const queryParams = {
    TableName: this.tableName,
    KeyConditionExpression: "PK = :pk and begins_with(SK, :skPrefix)",
    ExpressionAttributeValues: marshall({
      ":pk": pk,
      ":skPrefix": skPrefix,
    }),
    ...(projectionExpression && { ProjectionExpression: projectionExpression }),
    ...(Object.keys(expressionAttributeNames).length > 0 && { ExpressionAttributeNames: expressionAttributeNames }),
  };

  try {
    const command = new QueryCommand(queryParams);
    const response = await this.client.send(command);
    const items = response.Items?.map(item => this.removeKeysFromItem(this.addIdentifiersToItem(unmarshall(item), itemType))) || [];

    this.logger.info(`Successfully fetched ${items.length} ${itemType}s for presentation ${presentationID}`);

    // TypeScript will correctly infer the return type based on itemType
    return items as Slide[] | Topic[] | Source[];
  } catch (error: any) {
    this.logger.error({ error }, `Error fetching ${itemType}s for presentation`);
    throw error;
  }
}

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
public async deleteAllItemsForPresentation(
  itemType: 'slide' | 'topic' | 'source',
  userID: string,
  presentationID: string,
): Promise<void> {
  this.logger.info(`Deleting all ${itemType}s for presentation ${presentationID}`);

  const pk = `USER#${userID}`;
  const skPrefix = `PRESENTATION#${presentationID}#${itemType.toUpperCase()}#`;

  const queryParams = {
    TableName: this.tableName,
    KeyConditionExpression: "PK = :pk and begins_with(SK, :skPrefix)",
    ExpressionAttributeValues: marshall({
      ":pk": pk,
      ":skPrefix": skPrefix,
    }),
    ProjectionExpression: "PK, SK",
  };

  try {
    // First, query to get all the keys
    const queryCommand = new QueryCommand(queryParams);
    const queryResponse = await this.client.send(queryCommand);
    const items = queryResponse.Items || [];

    if (items.length === 0) {
      this.logger.info(`No ${itemType}s found for presentation ${presentationID}`);
      return;
    }

    // Prepare delete requests
    const deleteRequests = items.map(item => ({
      Delete: {
        TableName: this.tableName,
        Key: item,
      }
    }));

    // Delete items in batches of 25 (DynamoDB limit for transact writes)
    for (let i = 0; i < deleteRequests.length; i += 25) {
      const batch = deleteRequests.slice(i, i + 25);
      await this.client.send(new TransactWriteItemsCommand({ TransactItems: batch }));
    }

    this.logger.info(`Successfully deleted ${items.length} ${itemType}s for presentation ${presentationID}`);
  } catch (error: any) {
    this.logger.error({ error }, `Error deleting ${itemType}s for presentation`);
    throw error;
  }
}

/**
 * Fetch presentations for a user, with optional pagination support.
 * 
 * @param {string} userID - The user ID to fetch presentations for.
 * @param {Record<string, AttributeValue>} [lastEvaluatedKey] - Optional LastEvaluatedKey from the previous query (for pagination).
 * @param {number} [n=25] - Number of items to fetch (default: 25).
 * @returns {Promise<{
*   presentations: Array<{presentation_id: string, topic: string, status: string}>,
*   lastEvaluatedKey?: Record<string, AttributeValue>
* }>} - Object containing an array of presentation objects and the LastEvaluatedKey for the next page.
*/
public async fetchPresentations(
  userID: string,
  lastEvaluatedKey?: Record<string, AttributeValue>,
  n: number = 25
): Promise<{
  presentations: Array<{presentation_id: string, topic: string, status: string}>,
  lastEvaluatedKey?: Record<string, AttributeValue>
}> {
  this.logger.info(`Fetching presentations for user ${userID}, with LastEvaluatedKey: ${JSON.stringify(lastEvaluatedKey)}`);

  const pk = `USER#${userID}`;
  const queryParams: QueryCommandInput = {
    TableName: this.tableName,
    IndexName: 'GSI1',
    KeyConditionExpression: 'PK = :pk',
    ExpressionAttributeValues: marshall({
      ':pk': pk
    }),
    ExpressionAttributeNames: {
      '#SK': 'SK',
      '#topic': 'topic',
      '#GSI1SK': 'GSI1SK',
      '#status': 'status'
    },
    Limit: n,
    ScanIndexForward: false,
    ProjectionExpression: '#SK, #topic, #GSI1SK, #status'
  };

  if (lastEvaluatedKey) {
    queryParams.ExclusiveStartKey = lastEvaluatedKey;
    this.logger.debug(`Using ExclusiveStartKey: ${JSON.stringify(lastEvaluatedKey)}`);
  }

  try {
    const command = new QueryCommand(queryParams);
    this.logger.debug(`Query params: ${JSON.stringify(queryParams)}`);
    const response = await this.client.send(command);
    
    const presentations = response.Items?.map(item => {
      const unmarshalledItem = unmarshall(item);
      return {
        presentation_id: unmarshalledItem.SK.split('#')[1],
        topic: unmarshalledItem.topic,
        status: unmarshalledItem.status
      };
    }) || [];

    this.logger.info(`Successfully fetched ${presentations.length} presentations`);
    return {
      presentations,
      lastEvaluatedKey: response.LastEvaluatedKey
    };
  } catch (error: any) {
    this.logger.error({ 
      error, 
      userID, 
      lastEvaluatedKey: JSON.stringify(lastEvaluatedKey), 
      queryParams: JSON.stringify(queryParams)
    }, 'Error fetching presentations');
    throw error;
  }
}

} // end class


