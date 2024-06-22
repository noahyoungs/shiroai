// dynamodb.ts
import { DynamoDBClient } from "@aws-sdk/client-dynamodb";
import {
  GetItemCommand,
  PutItemCommand,
  QueryCommand,
  UpdateItemCommand,
  TransactWriteItemsCommand,
  DeleteItemCommand,
  BatchGetItemCommand
} from "@aws-sdk/client-dynamodb";
import { marshall as Marshall } from "@aws-sdk/util-dynamodb";
import { unmarshall } from "@aws-sdk/util-dynamodb";
import { uuidv7 } from "uuidv7";
import { Slide } from "@/utils/slide-types";

const client = new DynamoDBClient({});

const tableName = "AiPresenter2"; 

export async function getPresentationsByUserID(userID: string, attributes: string[], limit: number, lastEvaluatedKey?: any) {
  attributes.push("PK");

  const params: any = {
    TableName: tableName,
    IndexName: "user-index",
    KeyConditionExpression: "#userAttr = :user",
    FilterExpression: "begins_with(SK, :prefix)",
    ExpressionAttributeNames: {
      "#userAttr": "user",
    },
    ExpressionAttributeValues: {
      ":user": { S: userID },
      ":prefix": { S: "PRESENTATION#" },
    },
    ProjectionExpression: attributes.map((attr) => `#${attr}`).join(", "),
    Limit: limit,
    ScanIndexForward: false // To get items in descending order
  };

  if (lastEvaluatedKey) {
    params.ExclusiveStartKey = lastEvaluatedKey;
  }

  // Add the attribute names to ExpressionAttributeNames
  attributes.forEach((attr) => {
    (params.ExpressionAttributeNames as { [key: string]: string })[`#${attr}`] = attr;
  });

  const command = new QueryCommand(params);
  const response = await client.send(command);

  const presentations = response.Items?.map((item) => {
    const unmarshalled = unmarshall(item);
    const { SK, PK, ...presentationFields } = unmarshalled;
    const filteredFields = attributes.reduce((acc: any, attr) => {
      acc[attr] = presentationFields[attr];
      return acc;
    }, {});

    const presentation: any = {
      ...filteredFields,
    };

    if (PK) {
      presentation.id = PK.split("#")[1];
    }

    return presentation;
  });

  return {
    presentations,
    lastEvaluatedKey: response.LastEvaluatedKey,
  };
}

export async function getPresentationByID(presentationID: string, attributes: string[]) {
  attributes.push("PK");

  const params = {
    TableName: tableName,
    Key: {
      PK: { S: `PRESENTATION#${presentationID}` },
      SK: { S: `PRESENTATION#${presentationID}` },
    },
    ProjectionExpression: attributes.map((attr) => `#${attr}`).join(", "),
    ExpressionAttributeNames: {},
  };

  // Add the attribute names to ExpressionAttributeNames
  attributes.forEach((attr) => {
    (params.ExpressionAttributeNames as { [key: string]: string })[`#${attr}`] = attr;
  });

  const command = new GetItemCommand(params);
  const response = await client.send(command);

  if (response.Item) {
    const unmarshalled = unmarshall(response.Item);
    const { SK, PK, ...presentationFields } = unmarshalled;

    const filteredFields = attributes.reduce((acc: any, attr) => {
      acc[attr] = presentationFields[attr];
      return acc;
    }, {});

    const presentation: any = {
      ...filteredFields,
    };

    if (PK) {
      presentation.id = PK.split("#")[1];
    }

    return presentation;
  }

  return null;
}

export async function updatePresentationByID(
  presentationID: string,
  presentation: any
) {
  if (!presentationID) {
    throw new Error("Presentation ID is required.");
  }

  const updateExpressions: string[] = [];
  const expressionAttributeNames: { [key: string]: string } = {};
  const expressionAttributeValues: { [key: string]: any } = {};

  for (const [key, value] of Object.entries(presentation)) {
    updateExpressions.push(`#${key} = :${key}`);
    expressionAttributeNames[`#${key}`] = key;
    
    switch (typeof value) {
      case "string":
        expressionAttributeValues[`:${key}`] = { S: value };
        break;
      case "number":
        expressionAttributeValues[`:${key}`] = { N: value.toString() };
        break;
      case "boolean":
        expressionAttributeValues[`:${key}`] = { BOOL: value };
        break;
      // Add more cases for other data types if needed
      default:
        expressionAttributeValues[`:${key}`] = { S: value?.toString() };
    }
  }

  const params = {
    TableName: tableName,
    Key: {
      PK: { S: `PRESENTATION#${presentationID}` },
      SK: { S: `PRESENTATION#${presentationID}` },
    },
    UpdateExpression: `SET ${updateExpressions.join(", ")}`,
    ExpressionAttributeNames: expressionAttributeNames,
    ExpressionAttributeValues: expressionAttributeValues,
  };

  const command = new UpdateItemCommand(params);
  await client.send(command);
  console.log("Updated presentation with ID: ", presentationID);
}

export async function createSource(presentationID: string, source: any) {
  if (!presentationID) {
    throw new Error("Presentation ID is required.");
  }

  const sourceID = uuidv7();

  const params = {
    TableName: tableName,
    Item: {
      PK: { S: `PRESENTATION#${presentationID}` },
      SK: { S: `SOURCE#${sourceID}` },
      ...Marshall(source),
    },
  };

  const command = new PutItemCommand(params);
  await client.send(command);
  console.log("Created new source with ID: ", sourceID);
  return sourceID;
}

export async function getSources(presentationID: string, attributes?: string[]) {
  const params = {
    TableName: tableName,
    KeyConditionExpression: "PK = :pk AND begins_with(SK, :sk)",
    ExpressionAttributeValues: {
      ":pk": { S: `PRESENTATION#${presentationID}` },
      ":sk": { S: "SOURCE#" },
    },
    ProjectionExpression: attributes ? attributes.join(", ") : undefined,
  };

  const command = new QueryCommand(params);
  const response = await client.send(command);

  const sources = response.Items?.map((item) => {
    const unmarshalled = unmarshall(item);
    const simplified: any = {};

    for (const [k, v] of Object.entries(unmarshalled)) {
      if (k === "SK") {
        simplified["id"] = (v as string).split("#")[1];
      } else if (k === "PK") {
        simplified["presentation_id"] = (v as string).split("#")[1];
      } else if (k === "web_source") {
        simplified[k] = JSON.parse(v as string);
      } else if (typeof v === "string") {
        simplified[k] = v;
      } else if (typeof v === "number") {
        simplified[k] = v;
      } else if (typeof v === "boolean") {
        simplified[k] = v;
      }
    }

    return simplified;
  });

  return sources;
}

/**
 * Updates one or more slides in a DynamoDB table.
 *
 * @param {string} presentationID - The ID of the presentation.
 * @param {Partial<Slide> | Partial<Slide>[]} slides - A single slide or an array of slides with partial attributes to update. Each slide must contain an `id` property.
 * @returns {Promise<boolean>} - A promise that resolves to a boolean indicating the success of the operation.
 *
 * @example
 * const slideUpdate = { id: 'slide1', slide_title: 'Updated Title' };
 * const success = await updateSlides('presentation123', slideUpdate);
 *
 * @example
 * const slidesUpdate = [
 *   { id: 'slide1', slide_title: 'Updated Title' },
 *   { id: 'slide2', slide_content: 'Updated Content' }
 * ];
 * const success = await updateSlides('presentation123', slidesUpdate);
 *
 * @throws Will throw an error if DynamoDB update fails.
 *
 * @description
 * This function updates the specified attributes of one or more slides in the DynamoDB table. If the `slides` parameter is an array, a batch update is performed using `TransactWriteItemsCommand`. Otherwise, a single update is performed using `UpdateItemCommand`. Only the specified attributes are updated; any unspecified attributes remain unaffected.
 */
export async function updateSlides(
  presentationID: string,
  slides: Partial<Slide> | Partial<Slide>[]
): Promise<boolean> {
  const currentTimestamp = Math.floor(Date.now() / 1000);

  if (Array.isArray(slides)) {
    if (slides.length === 0) {
      console.error("Dynamodb updateSlides: Slides array cannot be empty.");
      return false;
    }

    const updateRequests: any[] = [];

    for (const slide of slides) {
      const { id, ...slideFields } = slide;

      if (id === undefined) {
        console.error(`Slide ID is undefined for slide:`, slide);
        continue;
      }

      if (Object.keys(slideFields).length === 0) {
        console.error(`Slide with ID ${id} contains only the ID property.`);
        continue;
      }

      const updateExpression: string[] = [];
      const expressionAttributeValues: { [key: string]: any } = {};
      const expressionAttributeNames: { [key: string]: string } = {};

      for (const [key, value] of Object.entries(slideFields)) {
        if (value === undefined) {
          console.error(`Skipping undefined value for key: ${key}`);
          continue;
        }

        let attributeValue: any;
        if (Array.isArray(value) || typeof value === "object") {
          attributeValue = { S: JSON.stringify(value) };
        } else if (typeof value === "string") {
          attributeValue = { S: value };
        } else if (typeof value === "number") {
          attributeValue = { N: value.toString() };
        } else if (typeof value === "boolean") {
          attributeValue = { BOOL: value };
        } else {
          console.error(`Unsupported attribute type for key: ${key}`);
          continue;
        }

        const attributeName = `#${key}`;
        updateExpression.push(`${attributeName} = :${key}`);
        expressionAttributeNames[attributeName] = key;
        expressionAttributeValues[`:${key}`] = attributeValue;
      }

      updateExpression.push("#time_updated = :time_updated");
      expressionAttributeNames["#time_updated"] = "time_updated";
      expressionAttributeValues[":time_updated"] = {
        N: currentTimestamp.toString(),
      };

      const updateRequest = {
        Update: {
          TableName: tableName,
          Key: {
            PK: { S: `PRESENTATION#${presentationID}` },
            SK: { S: `SLIDE#${id}` },
          },
          UpdateExpression: "SET " + updateExpression.join(", "),
          ExpressionAttributeValues: expressionAttributeValues,
          ExpressionAttributeNames: expressionAttributeNames,
        },
      };

      updateRequests.push(updateRequest);
    }

    if (updateRequests.length === 0) {
      console.error("No valid slides to update.");
      return false;
    }

    const command = new TransactWriteItemsCommand({
      TransactItems: updateRequests,
    });

    try {
      console.log("Sending batch update request to DynamoDB...");
      const response = await client.send(command);
      console.log("Batch update response:", response);
      return response.$metadata.httpStatusCode === 200;
    } catch (error) {
      console.error("Error during batch update:", error);
      return false;
    }
  } else {
    const { id, ...slideFields } = slides;

    if (id === undefined) {
      console.error("Slide ID is undefined.");
      return false;
    }

    if (Object.keys(slideFields).length === 0) {
      console.error(`Slide with ID ${id} contains only the ID property.`);
      return false;
    }

    const updateExpression: string[] = [];
    const expressionAttributeValues: { [key: string]: any } = {};
    const expressionAttributeNames: { [key: string]: string } = {};

    for (const [key, value] of Object.entries(slideFields)) {
      if (value === undefined) {
        console.error(`Skipping undefined value for key: ${key}`);
        continue;
      }

      let attributeValue: any;
      if (Array.isArray(value) || typeof value === "object") {
        attributeValue = { S: JSON.stringify(value) };
      } else if (typeof value === "string") {
        attributeValue = { S: value };
      } else if (typeof value === "number") {
        attributeValue = { N: value.toString() };
      } else if (typeof value === "boolean") {
        attributeValue = { BOOL: value };
      } else {
        console.error(`Unsupported attribute type for key: ${key}`);
        continue;
      }

      const attributeName = `#${key}`;
      updateExpression.push(`${attributeName} = :${key}`);
      expressionAttributeNames[attributeName] = key;
      expressionAttributeValues[`:${key}`] = attributeValue;
    }

    updateExpression.push("#time_updated = :time_updated");
    expressionAttributeNames["#time_updated"] = "time_updated";
    expressionAttributeValues[":time_updated"] = {
      N: currentTimestamp.toString(),
    };

    const params = {
      TableName: tableName,
      Key: {
        PK: { S: `PRESENTATION#${presentationID}` },
        SK: { S: `SLIDE#${id}` },
      },
      UpdateExpression: "SET " + updateExpression.join(", "),
      ExpressionAttributeValues: expressionAttributeValues,
      ExpressionAttributeNames: expressionAttributeNames,
    };

    const command = new UpdateItemCommand(params);

    try {
      console.log("Sending single slide update request to DynamoDB...");
      const response = await client.send(command);
      console.log("Single slide update response:", response);
      return response.$metadata.httpStatusCode === 200;
    } catch (error) {
      console.error("Error during single slide update:", error);
      return false;
    }
  }
}

/**
 * Retrieves all slides for a given presentation from DynamoDB.
 *
 * @param {string} presentationID - The ID of the presentation.
 * @param {string[]} [attributes] - An optional array of attribute names to retrieve. If not specified, all attributes are retrieved.
 * @returns {Promise<Slide[]>} - A promise that resolves to an array of slides.
 *
 * @example
 * const slides = await getAllSlides('presentation123');
 *
 * @example
 * const slides = await getAllSlides('presentation123', ['slide_title', 'slide_content']);
 *
 * @throws Will throw an error if DynamoDB query fails.
 *
 * @description
 * This function queries the DynamoDB table to retrieve all slides associated with the specified presentation ID. If the `attributes` parameter is provided, only those attributes are retrieved. Otherwise, all attributes are retrieved. The function handles the unmarshalling of DynamoDB items and parsing of JSON strings where applicable.
 */
export async function getAllSlides(
  presentationID: string,
  attributes?: string[]
): Promise<Slide[]> {
  const params: any = {
    TableName: tableName,
    KeyConditionExpression: "PK = :pk AND begins_with(SK, :sk)",
    ExpressionAttributeValues: {
      ":pk": { S: `PRESENTATION#${presentationID}` },
      ":sk": { S: "SLIDE#" },
    },
  };

  if (attributes) {
    params.ProjectionExpression = attributes.join(", ");
  }

  try {
    const command = new QueryCommand(params);
    const response = await client.send(command);

    const slides: Slide[] = response.Items?.map((item) => {
      const unmarshalled = unmarshall(item);
      const { SK, PK, ...slideFields } = unmarshalled;

      for (const key in slideFields) {
        if (typeof slideFields[key] === "string") {
          try {
            slideFields[key] = JSON.parse(slideFields[key]);
          } catch (error) {
            // Ignore parsing error and keep the field as a string
          }
        }
      }

      const slide: Slide = {
        id: SK.split("#")[1],
        slide_type: slideFields.slide_type,
        slide_title: slideFields.slide_title,
        topic_id: slideFields.topic_id,
        slide_content: slideFields.slide_content,
        sequential: slideFields.sequential,
        image: slideFields.image,
        layout: slideFields.layout,
        hidden: slideFields.hidden,
        image_position: slideFields.image_position,
        previous: slideFields.previous,
        next: slideFields.next,
      };

      return slide;
    }) || [];

    return slides;
  } catch (error) {
    console.error("Error retrieving slides:", error);
    return [];
  }
}

// Function overloads
export async function getSlides(presentationID: string, slideIDs: string, attributes?: string[]): Promise<Slide | null>;
export async function getSlides(presentationID: string, slideIDs: string[], attributes?: string[]): Promise<Slide[] | null>;

/**
 * Retrieves one or more slides by their IDs for a given presentation from DynamoDB.
 *
 * @param {string} presentationID - The ID of the presentation.
 * @param {string | string[]} slideIDs - A single slide ID or an array of slide IDs to retrieve.
 * @param {string[]} [attributes] - An optional array of attribute names to retrieve. If not specified, all attributes are retrieved.
 * @returns {Promise<Slide | Slide[] | null>} - A promise that resolves to a single slide, an array of slides, or null if no slides are found.
 *
 * @example
 * const slide = await getSlides('presentation123', 'slide1');
 *
 * @example
 * const slides = await getSlides('presentation123', ['slide1', 'slide2'], ['slide_title', 'slide_content']);
 *
 * @throws Will throw an error if DynamoDB query fails.
 *
 * @description
 * This function retrieves one or more slides by their IDs for a specified presentation from the DynamoDB table. If the `slideIDs` parameter is an array, a batch get operation is performed using `BatchGetItemCommand`. Otherwise, a single get operation is performed using `GetItemCommand`. If the `attributes` parameter is provided, only those attributes are retrieved. Otherwise, all attributes are retrieved. The function handles the unmarshalling of DynamoDB items and parsing of JSON strings where applicable.
 */
export async function getSlides(
  presentationID: string,
  slideIDs: string | string[],
  attributes?: string[]
): Promise<Slide | Slide[] | null> {
  if (Array.isArray(slideIDs)) {
    if (slideIDs.length === 0) {
      console.error("Slide IDs array cannot be empty.");
      return null;
    }

    const keys = slideIDs.map(id => ({
      PK: { S: `PRESENTATION#${presentationID}` },
      SK: { S: `SLIDE#${id}` },
    }));

    const params = {
      RequestItems: {
        [tableName]: {
          Keys: keys,
          ProjectionExpression: attributes ? attributes.join(", ") : undefined,
        },
      },
    };

    try {
      const command = new BatchGetItemCommand(params);
      const response = await client.send(command);

      const slides: Slide[] = response.Responses?.[tableName]?.map((item) => {
        const unmarshalled = unmarshall(item);
        const { SK, PK, ...slideFields } = unmarshalled;

        for (const key in slideFields) {
          if (typeof slideFields[key] === "string") {
            try {
              slideFields[key] = JSON.parse(slideFields[key]);
            } catch (error) {
              // Ignore parsing error and keep the field as a string
            }
          }
        }

        const slide: Slide = {
          id: SK.split("#")[1],
          slide_type: slideFields.slide_type,
          slide_title: slideFields.slide_title,
          topic_id: slideFields.topic_id,
          slide_content: slideFields.slide_content,
          sequential: slideFields.sequential,
          image: slideFields.image,
          layout: slideFields.layout,
          hidden: slideFields.hidden,
          image_position: slideFields.image_position,
          previous: slideFields.previous,
          next: slideFields.next,
        };

        return slide;
      }) || [];

      return slides;
    } catch (error) {
      console.error("Error retrieving slides:", error);
      return null;
    }
  } else {
    const params: any = {
      TableName: tableName,
      Key: {
        PK: { S: `PRESENTATION#${presentationID}` },
        SK: { S: `SLIDE#${slideIDs}` },
      },
    };

    if (attributes) {
      params.ProjectionExpression = attributes.join(", ");
    }

    try {
      const command = new GetItemCommand(params);
      const response = await client.send(command);

      if (response.Item) {
        const unmarshalled = unmarshall(response.Item);
        const { SK, PK, ...slideFields } = unmarshalled;

        for (const key in slideFields) {
          if (typeof slideFields[key] === "string") {
            try {
              slideFields[key] = JSON.parse(slideFields[key]);
            } catch (error) {
              // Ignore parsing error and keep the field as a string
            }
          }
        }

        const slide: Slide = {
          id: SK.split("#")[1],
          slide_type: slideFields.slide_type,
          slide_title: slideFields.slide_title,
          topic_id: slideFields.topic_id,
          slide_content: slideFields.slide_content,
          sequential: slideFields.sequential,
          image: slideFields.image,
          layout: slideFields.layout,
          hidden: slideFields.hidden,
          image_position: slideFields.image_position,
          previous: slideFields.previous,
          next: slideFields.next,
        };

        return slide;
      }

      return null;
    } catch (error) {
      console.error("Error retrieving slide:", error);
      return null;
    }
  }
}
