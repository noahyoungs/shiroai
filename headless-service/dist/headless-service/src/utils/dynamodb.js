"use strict";
var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
var __rest = (this && this.__rest) || function (s, e) {
    var t = {};
    for (var p in s) if (Object.prototype.hasOwnProperty.call(s, p) && e.indexOf(p) < 0)
        t[p] = s[p];
    if (s != null && typeof Object.getOwnPropertySymbols === "function")
        for (var i = 0, p = Object.getOwnPropertySymbols(s); i < p.length; i++) {
            if (e.indexOf(p[i]) < 0 && Object.prototype.propertyIsEnumerable.call(s, p[i]))
                t[p[i]] = s[p[i]];
        }
    return t;
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.getPresentationByID = getPresentationByID;
exports.getAllSlides = getAllSlides;
// dynamodb.ts
const client_dynamodb_1 = require("@aws-sdk/client-dynamodb");
const client_dynamodb_2 = require("@aws-sdk/client-dynamodb");
const util_dynamodb_1 = require("@aws-sdk/util-dynamodb");
const client = new client_dynamodb_1.DynamoDBClient({});
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
function getPresentationByID(presentationID, attributes) {
    return __awaiter(this, void 0, void 0, function* () {
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
            params.ExpressionAttributeNames[`#${attr}`] =
                attr;
        });
        const command = new client_dynamodb_2.GetItemCommand(params);
        const response = yield client.send(command);
        if (response.Item) {
            const unmarshalled = (0, util_dynamodb_1.unmarshall)(response.Item);
            const { SK, PK } = unmarshalled, presentationFields = __rest(unmarshalled, ["SK", "PK"]);
            const filteredFields = attributes.reduce((acc, attr) => {
                acc[attr] = presentationFields[attr];
                return acc;
            }, {});
            const presentation = Object.assign({}, filteredFields);
            if (PK) {
                presentation.id = PK.split("#")[1];
            }
            return presentation;
        }
        return null;
    });
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
function getAllSlides(presentationID, attributes) {
    return __awaiter(this, void 0, void 0, function* () {
        var _a;
        const params = {
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
            const command = new client_dynamodb_2.QueryCommand(params);
            const response = yield client.send(command);
            const slides = ((_a = response.Items) === null || _a === void 0 ? void 0 : _a.map((item) => {
                const unmarshalled = (0, util_dynamodb_1.unmarshall)(item);
                const { SK, PK } = unmarshalled, slideFields = __rest(unmarshalled, ["SK", "PK"]);
                for (const key in slideFields) {
                    if (typeof slideFields[key] === "string") {
                        try {
                            slideFields[key] = JSON.parse(slideFields[key]);
                        }
                        catch (error) {
                            // Ignore parsing error and keep the field as a string
                        }
                    }
                }
                const slide = {
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
                };
                return slide;
            })) || [];
            return slides;
        }
        catch (error) {
            console.error("Error retrieving slides:", error);
            return [];
        }
    });
}
