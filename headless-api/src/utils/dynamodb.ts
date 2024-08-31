// headless-api/src/utils/dynamodb.ts

import { DynamoDBClient } from "@aws-sdk/client-dynamodb";
import {
  GetItemCommand,
  QueryCommand,
} from "@aws-sdk/client-dynamodb";
import { unmarshall } from "@aws-sdk/util-dynamodb";
import { Slide } from "../../../frontend/src/utils/slide-types";

const client = new DynamoDBClient({});

const tableName = "AiPresenter2";

/**
 * Retrieves a presentation by its ID from a DynamoDB table, returning specified attributes.
 *
 * @param {string} presentationID - The unique identifier for the presentation.
 * @param {string[]} attributes - An array of attribute names to be retrieved from the presentation.
 * @returns {Promise<object | null>} - A promise that resolves to an object containing the requested presentation attributes, or null if the presentation is not found.
 *
 * @example
 * const presentationID = '12345';
 * const attributes = ['title', 'createdAt'];
 * const presentation = await getPresentationByID(presentationID, attributes);
 * if (presentation) {
 *   console.log(`Presentation Title: ${presentation.title}`);
 *   console.log(`Created At: ${presentation.createdAt}`);
 * } else {
 *   console.log('Presentation not found');
 * }
 */
export async function getPresentationByID(
  presentationID: string,
  attributes: string[]
) {
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
    (params.ExpressionAttributeNames as { [key: string]: string })[`#${attr}`] =
      attr;
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

/**
 * Retrieves all slides for a given presentation from DynamoDB.
 *
 * @param {string} presentationID - The ID of the presentation.
 * @param {string[]} [attributes] - An optional array of attribute names to retrieve. If not specified, all attributes are retrieved.
 * @returns {PromisePartial<<Slide[]>>} - A promise that resolves to an array of slides, or partial slides if attributes are specified.
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
): Promise<Partial<Slide[]>> {
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

    const slides: Slide[] =
      response.Items?.map((item) => {
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
          generation_messages: slideFields.generation_messages,
          speaker_notes: slideFields.speaker_notes,
          script: slideFields.script,
        };

        return slide;
      }) || [];

    return slides;
  } catch (error) {
    console.error("Error retrieving slides:", error);
    return [];
  }
}
