import { DynamoDBClient } from "@aws-sdk/client-dynamodb";
import {
  GetItemCommand,
  PutItemCommand,
  QueryCommand,
  UpdateItemCommand,
  TransactWriteItemsCommand,
  DeleteItemCommand,
} from "@aws-sdk/client-dynamodb";
import { marshall as Marshall } from "@aws-sdk/util-dynamodb";
import { unmarshall } from "@aws-sdk/util-dynamodb";
import { uuidv7 } from "uuidv7";
import { Slide } from "@/utils/slide-types";

const client = new DynamoDBClient({});

const tableName = "AiPresenter2"; 
const slideOrderGSIName = "slide-order-index";

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
 * Batch updates multiple slides in a presentation.
 * @param {string} presentationID - The ID of the presentation.
 * @param {Partial<Slide>[]} slides - An array of partial slide objects to update.
 * @returns {Promise<boolean>} - A promise that resolves to true if the update is successful, false otherwise.
 * 
 * Note: If a slide object in the `slides` array has only a subset of the attributes compared to the existing slide in DynamoDB,
 * only the attributes present in the slide object will be updated. Attributes that exist in DynamoDB but are not present
 * in the slide object will remain unchanged. This allows for partial updates of slide attributes without affecting the
 * attributes that are not included in the update request.
 */
export async function batchUpdateSlides(
  presentationID: string,
  slides: Partial<Slide>[]
): Promise<boolean> {
  if (slides.length === 0) {
    throw new Error("Slides array cannot be empty.");
  }

  const updateRequests: any[] = [];
  const currentTimestamp = Math.floor(Date.now() / 1000);

  for (const slide of slides) {
    const { id, ...slideFields } = slide;

    if (id === undefined) {
      console.log(`Slide ID is undefined for slide:`, slide);
      continue;
    }

    if (Object.keys(slideFields).length === 0) {
      throw new Error(`Slide with ID ${id} contains only the ID property.`);
    }

    const updateExpression: string[] = [];
    const expressionAttributeValues: { [key: string]: any } = {};
    const expressionAttributeNames: { [key: string]: string } = {};

    for (const [key, value] of Object.entries(slideFields)) {
      if (value === undefined) {
        console.log(`Skipping undefined value for key: ${key}`);
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
        console.log(`Unsupported attribute type for key: ${key}`);
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

    // console.log(`Prepared update request for slide ID ${id}:`, JSON.stringify(updateRequest));

    updateRequests.push(updateRequest);
  }

  if (updateRequests.length === 0) {
    throw new Error("No valid slides to update.");
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
}

/**
 * Retrieves all slides for a given presentation.
 * @param {string} presentationID - The ID of the presentation.
 * @param {string[]} [attributes] - Optional array of attributes to retrieve for each slide.
 * @returns {Promise<Slide[]>} - A promise that resolves to an array of slide objects.
 */
export async function getSlides(
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

  const command = new QueryCommand(params);
  const response = await client.send(command);

  const slides: Slide[] = response.Items?.map((item) => {
    const unmarshalled = unmarshall(item);
    const { SK, PK, ...slideFields } = unmarshalled;

    // Parse JSON-encoded fields
    for (const key in slideFields) {
      if (typeof slideFields[key] === "string") {
        try {
          slideFields[key] = JSON.parse(slideFields[key]);
        } catch (error) {
          // Ignore parsing error and keep the field as a string
        }
      }
    }

    // Assign random layout if not present and slide type is 'short_bullets_slide'
    if (slideFields.slide_type === 'short_bullets_slide' && !slideFields.layout) {
      slideFields.layout = Math.random() < 0.5 ? 'list' : 'grid';
    }

    // Randomly assign left or right to image_position if not present and slide type is 'section_header_slide'
    if (slideFields.slide_type === 'section_header_slide' && !slideFields.image_position) {
      slideFields.image_position = Math.random() < 0.5 ? 'left' : 'right';
    }

    // Set hidden to false if not present
    if (slideFields.hidden === undefined) {
      slideFields.hidden = false;
    }

    // Parse the slide content only
    const slide: Slide = {
      id: SK.split("#")[1],
      slide_type: slideFields.slide_type,
      slide_title: slideFields.slide_title,
      topic_id: slideFields.topic_id,
      slide_content: slideFields.slide_content,
      slide_order: slideFields.slide_order,
      sequential: slideFields.sequential,
      image: slideFields.image,
      layout: slideFields.layout,
      hidden: slideFields.hidden,
      image_position: slideFields.image_position
    };

    return slide;
  }) || [];

  return slides;
}

/**
 * Retrieves a single slide from a presentation.
 * @param {string} presentationID - The ID of the presentation.
 * @param {string} slideID - The ID of the slide to retrieve.
 * @param {string[]} [attributes] - Optional array of attributes to retrieve for the slide.
 * @returns {Promise<Slide | null>} - A promise that resolves to the slide object, or null if not found.
 */
export async function getSlide(
  presentationID: string,
  slideID: string,
  attributes?: string[]
): Promise<Slide | null> {
  const params: any = {
    TableName: tableName,
    Key: {
      PK: { S: `PRESENTATION#${presentationID}` },
      SK: { S: `SLIDE#${slideID}` },
    },
  };

  if (attributes) {
    params.ProjectionExpression = attributes.join(", ");
  }

  const command = new GetItemCommand(params);
  const response = await client.send(command);

  if (response.Item) {
    const unmarshalled = unmarshall(response.Item);
    const { SK, PK, ...slideFields } = unmarshalled;

    // Parse JSON-encoded fields
    for (const key in slideFields) {
      if (typeof slideFields[key] === "string") {
        try {
          slideFields[key] = JSON.parse(slideFields[key]);
        } catch (error) {
          // Ignore parsing error and keep the field as a string
        }
      }
    }

    // Assign random layout if not present and slide type is 'short_bullets_slide'
    if (slideFields.slide_type === 'short_bullets_slide' && !slideFields.layout) {
      slideFields.layout = Math.random() < 0.5 ? 'list' : 'grid';
    }

    // Randomly assign left or right to image_position if not present and slide type is 'section_header_slide'
    if (slideFields.slide_type === 'section_header_slide' && !slideFields.image_position) {
      slideFields.image_position = Math.random() < 0.5 ? 'left' : 'right';
    }

    // Set hidden to false if not present
    if (slideFields.hidden === undefined) {
      slideFields.hidden = false;
    }

    const slide: Slide = {
      id: SK.split("#")[1],
      slide_type: slideFields.slide_type,
      slide_title: slideFields.slide_title,
      topic_id: slideFields.topic_id,
      slide_content: slideFields.slide_content,
      slide_order: slideFields.slide_order,
      sequential: slideFields.sequential,
      image: slideFields.image,
      layout: slideFields.layout,
      hidden: slideFields.hidden,
      image_position: slideFields.image_position
    };

    return slide;
  }

  return null;
}



/**
 * Updates a single slide in a presentation.
 * @param {string} presentationID - The ID of the presentation.
 * @param {string} slideID - The ID of the slide to update.
 * @param {Partial<Slide>} slideData - An object containing the fields to update on the slide.
 * @returns {Promise<void>} - A promise that resolves when the update is complete.
 * 
 * Note: The `slideData` parameter is of type `Partial<Slide>`, meaning it can contain a subset of the attributes
 * defined in the `Slide` type. Only the attributes present in `slideData` will be updated in DynamoDB. Attributes
 * that exist in DynamoDB but are not present in `slideData` will remain unchanged. This allows for partial updates
 * of slide attributes without affecting the attributes that are not included in the update request.
 */
export async function updateSlide(
  presentationID: string,
  slideID: string,
  slideData: Partial<Slide>
): Promise<void> {
  const updateExpression: string[] = [];
  const expressionAttributeValues: { [key: string]: any } = {};
  const expressionAttributeNames: { [key: string]: string } = {};

  for (const [key, value] of Object.entries(slideData)) {
    if (value === undefined) {
      // console.log(`Value is undefined for key: ${key}`)
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
      console.log(`Unsupported attribute type for key: ${key}`);
      continue;
    }

    const attributeName = `#${key}`;
    updateExpression.push(`${attributeName} = :${key}`);
    expressionAttributeNames[attributeName] = key;
    expressionAttributeValues[`:${key}`] = attributeValue;
  }

  const currentTimestamp = Math.floor(Date.now() / 1000);
  updateExpression.push("#time_updated = :time_updated");
  expressionAttributeNames["#time_updated"] = "time_updated";
  expressionAttributeValues[":time_updated"] = {
    N: currentTimestamp.toString(),
  };

  const params = {
    TableName: tableName,
    Key: {
      PK: { S: `PRESENTATION#${presentationID}` },
      SK: { S: `SLIDE#${slideID}` },
    },
    UpdateExpression: "SET " + updateExpression.join(", "),
    ExpressionAttributeValues: expressionAttributeValues,
    ExpressionAttributeNames: expressionAttributeNames,
  };

  const command = new UpdateItemCommand(params);
  await client.send(command);
}

/**
 * Deletes a single slide from a presentation.
 * @param {string} presentationID - The ID of the presentation.
 * @param {string} slideID - The ID of the slide to delete.
 * @returns {Promise<void>} - A promise that resolves when the deletion is complete.
 */
export async function deleteSlide(
  presentationID: string,
  slideID: string
): Promise<void> {
  const params = {
    TableName: tableName,
    Key: {
      PK: { S: `PRESENTATION#${presentationID}` },
      SK: { S: `SLIDE#${slideID}` },
    },
  };

  const command = new DeleteItemCommand(params);
  await client.send(command);
}

/**
 * Retrieves the order of the next slide in a presentation.
 *
 * @param {string} presentationId - The ID of the presentation.
 * @param {number} currentSlideOrder - The order of the current slide.
 * @returns {Promise<number | null>} A promise that resolves to the order of the next slide, or null if no next slide is found.
 * @throws {Error} If an error occurs during the retrieval process.
 */
export const getNextSlideOrder = async (presentationId: string, currentSlideOrder: number): Promise<number | null> => {
  const params = {
    TableName: tableName,
    IndexName: slideOrderGSIName,
    KeyConditionExpression: 'PK = :pk AND #slide_order > :currentOrder',
    ProjectionExpression: '#slide_order, SK',
    ExpressionAttributeNames: {
      '#slide_order': 'slide_order',
    },
    ExpressionAttributeValues: {
      ':pk': { S: `PRESENTATION#${presentationId}` },
      ':currentOrder': { N: currentSlideOrder.toString() },
    },
    Limit: 1,
  };

  try {
    const result = await client.send(new QueryCommand(params));
    if (result.Items && result.Items.length > 0) {
      const nextSlide = unmarshall(result.Items[0]);
      if (nextSlide.SK && nextSlide.SK.startsWith('SLIDE#')) {
        return nextSlide.slide_order;
      }
    }
    return null;
  } catch (error) {
    console.error('Error getting next slide order:', error);
    throw error;
  }
};


/**
 * Adds a new slide in front of the slide with the specified order in a presentation.
 *
 * @param {string} presentationId - The ID of the presentation.
 * @param {number} targetSlideOrder - The order of the target slide.
 * @param {Partial<Slide>} slideData - An object containing the data for the new slide.
 * @returns {Promise<void>} - A promise that resolves when the slide is added.
 * @throws {Error} If an error occurs during the slide addition process.
 */
export const addSlideAfterOrder = async (
  presentationId: string,
  targetSlideOrder: number,
  slideData: Partial<Slide>
): Promise<void> => {
  try {
    const newSlideId = uuidv7();

    const nextSlideOrder = await getNextSlideOrder(presentationId, targetSlideOrder);
    let newSlideOrder: number;

    if (nextSlideOrder !== null) {
      newSlideOrder = Math.round((targetSlideOrder + nextSlideOrder) / 2);
    } else {
      newSlideOrder = targetSlideOrder + 1000;
    }

    const updatedSlideData: Partial<Slide> = {
      ...slideData,
      slide_order: newSlideOrder,
    };

    await updateSlide(presentationId, newSlideId, updatedSlideData);
  } catch (error) {
    console.error('Error adding slide:', error);
    throw error;
  }
};
