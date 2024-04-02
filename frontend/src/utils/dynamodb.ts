//dynamodb.ts
import { DynamoDBClient } from "@aws-sdk/client-dynamodb";
import {
  GetItemCommand,
  PutItemCommand,
  QueryCommand,
  UpdateItemCommand,
} from "@aws-sdk/client-dynamodb";
import { marshall as Marshall } from "@aws-sdk/util-dynamodb";
import { unmarshall } from "@aws-sdk/util-dynamodb";
import { uuidv7 } from "uuidv7";

const client = new DynamoDBClient({});

const tableName = "AiPresenter2"; 

export async function getPresentationsByUserID(userID: string, attributes: string[]) {
  attributes.push("PK")
  const params = {
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
  };

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

  return presentations;
}

export async function getSlidesByPresentationID(presentationID: string) {
  const params = {
    TableName: tableName,
    KeyConditionExpression: "PK = :presentationID",
    FilterExpression: "begins_with(SK, :prefix)",
    ExpressionAttributeValues: {
      ":presentationID": { S: `PRESENTATION#${presentationID}` },
      ":prefix": { S: "SLIDE#" },
    },
  };

  const command = new QueryCommand(params);
  const response = await client.send(command);
  return response.Items;
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

export async function getSlideByID(presentationID: string, slideID: string) {
  const params = {
    TableName: tableName,
    Key: {
      PK: { S: `PRESENTATION#${presentationID}` },
      SK: { S: `SLIDE#${slideID}` },
    },
  };

  const command = new GetItemCommand(params);
  const response = await client.send(command);
  return response.Item;
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