# backend/dynamodb_interface.py

import os
import time
from dotenv import load_dotenv
from aiobotocore.session import get_session
import json
from typing import List, Dict, Any, Union
import asyncio
from uuid_extensions import uuid7str
from backend.database_models import *
from boto3.dynamodb.types import TypeDeserializer, TypeSerializer

load_dotenv()

TABLE_NAME = os.getenv("DYNAMODB_TABLE_NAME")

# Initialize TypeSerializer and TypeDeserializer
serializer = TypeSerializer()
deserializer = TypeDeserializer()

# Utility function to serialize items for DynamoDB
def serialize_item(item: Dict[str, Any]) -> Dict[str, Any]:
    return {k: serializer.serialize(v) for k, v in item.items()}

# Utility function to deserialize items from DynamoDB
def deserialize_item(item: Dict[str, Any]) -> Dict[str, Any]:
    return {k: deserializer.deserialize(v) for k, v in item.items()}

# Utility function to create DynamoDB client
async def create_dynamodb_client():
    session = get_session()
    return session.create_client('dynamodb', region_name=os.getenv("AWS_REGION"))

# Utility function to construct keys for DynamoDB operations
def construct_keys(item_type: str, identifiers: Dict[str, str]) -> Dict[str, str]:
    if item_type == 'user':
        return {'PK': f"USER#{identifiers['user_id']}", 'SK': 'PROFILE'}
    elif item_type == 'presentation':
        return {'PK': f"USER#{identifiers['user_id']}", 'SK': f"PRESENTATION#{identifiers['presentation_id']}"}
    elif item_type == 'slide':
        return {'PK': f"USER#{identifiers['user_id']}", 'SK': f"PRESENTATION#{identifiers['presentation_id']}#SLIDE#{identifiers['slide_id']}"}
    elif item_type == 'topic':
        return {'PK': f"USER#{identifiers['user_id']}", 'SK': f"PRESENTATION#{identifiers['presentation_id']}#TOPIC#{identifiers['topic_id']}"}
    elif item_type == 'source':
        return {'PK': f"USER#{identifiers['user_id']}", 'SK': f"PRESENTATION#{identifiers['presentation_id']}#SOURCE#{identifiers['source_id']}"}
    else:
        raise ValueError(f"Unknown item_type: {item_type}")

# Function to get items from DynamoDB
async def get_items(item_type: str, identifiers: Dict[str, str], attributes: List[str] = None, return_type: str = 'dict') -> Union[Dict[str, Any], BaseModel]:
    client = await create_dynamodb_client()
    try:
        keys = construct_keys(item_type, identifiers)
        params = {
            'TableName': TABLE_NAME,
            'Key': serialize_item(keys)
        }

        if attributes:
            params['ProjectionExpression'] = ', '.join(attributes)
            params['ExpressionAttributeNames'] = {f"#{attr}": attr for attr in attributes}

        response = await client.get_item(**params)

        if 'Item' not in response:
            return None

        item = deserialize_item(response['Item'])

        if item_type in ['slide', 'topic'] and return_type == 'model':
            model_cls = SlideModel if item_type == 'slide' else TopicModel
            return model_cls(**item)
        return item

    finally:
        await client.close()

# Function to update or create items in DynamoDB
async def update_items(item_type: str, items: Union[List[Dict[str, Any]], List[BaseModel]]) -> None:
    client = await create_dynamodb_client()
    try:
        requests = []

        for item in items:
            if isinstance(item, BaseModel):
                item = item.dict()

            keys = construct_keys(item_type, item)
            serialized_item = serialize_item({**keys, **item})

            # Update last_updated and GSI1SK if needed
            if item_type != 'user':
                last_updated = str(int(time.time()))
                serialized_item['last_updated'] = serializer.serialize(last_updated)
                serialized_item['GSI1SK'] = serializer.serialize(f"LASTUPDATE#{last_updated}#PRESENTATION#{item.get('presentation_id')}")

            requests.append({
                'PutRequest': {
                    'Item': serialized_item
                }
            })

        if requests:
            await client.batch_write_item(RequestItems={TABLE_NAME: requests})

    finally:
        await client.close()

# Function to delete items from DynamoDB
async def delete_items(item_type: str, identifiers: List[Dict[str, str]]) -> None:
    client = await create_dynamodb_client()
    try:
        requests = []

        for id_set in identifiers:
            keys = construct_keys(item_type, id_set)
            serialized_keys = serialize_item(keys)

            requests.append({
                'DeleteRequest': {
                    'Key': serialized_keys
                }
            })

        if requests:
            await client.batch_write_item(RequestItems={TABLE_NAME: requests})

    finally:
        await client.close()

# Function to get all items for a presentation
async def get_all_items_for_presentation(user_id: str, presentation_id: str, item_type: str, attributes: List[str] = None, return_type: str = 'dict') -> Union[List[Dict[str, Any]], List[BaseModel]]:
    client = await create_dynamodb_client()
    try:
        pk = f"USER#{user_id}"
        sk_prefix = f"PRESENTATION#{presentation_id}#{item_type.upper()}#"

        params = {
            'TableName': TABLE_NAME,
            'KeyConditionExpression': '#pk = :pk and begins_with(#sk, :sk)',
            'ExpressionAttributeNames': {'#pk': 'PK', '#sk': 'SK'},
            'ExpressionAttributeValues': {':pk': {'S': pk}, ':sk': {'S': sk_prefix}}
        }

        if attributes:
            params['ProjectionExpression'] = ', '.join(attributes)
            params['ExpressionAttributeNames'].update({f"#{attr}": attr for attr in attributes})

        response = await client.query(**params)

        items = [deserialize_item(item) for item in response.get('Items', [])]

        if item_type in ['slide', 'topic'] and return_type == 'model':
            model_cls = SlideModel if item_type == 'slide' else TopicModel
            return [model_cls(**item) for item in items]
        return items

    finally:
        await client.close()

# Function to delete all items for a presentation
async def delete_all_items_for_presentation(user_id: str, presentation_id: str, item_type: str) -> None:
    client = await create_dynamodb_client()
    try:
        items_to_delete = await get_all_items_for_presentation(user_id, presentation_id, item_type)
        await delete_items(item_type, [{'user_id': user_id, 'presentation_id': presentation_id, **item} for item in items_to_delete])

    finally:
        await client.close()

# Function to get all presentations for a user
async def get_all_presentations_for_user(user_id: str, attributes: List[str] = None, return_type: str = 'dict') -> Union[List[Dict[str, Any]], List[BaseModel]]:
    client = await create_dynamodb_client()
    try:
        pk = f"USER#{user_id}"

        params = {
            'TableName': TABLE_NAME,
            'IndexName': 'GSI1',
            'KeyConditionExpression': '#pk = :pk',
            'ExpressionAttributeNames': {'#pk': 'GSI1PK'},
            'ExpressionAttributeValues': {':pk': {'S': pk}},
            'ScanIndexForward': False
        }

        if attributes:
            params['ProjectionExpression'] = ', '.join(attributes)
            params['ExpressionAttributeNames'].update({f"#{attr}": attr for attr in attributes})

        response = await client.query(**params)

        items = [deserialize_item(item) for item in response.get('Items', [])]

        if return_type == 'model':
            return [PresentationModel(**item) for item in items]
        return items

    finally:
        await client.close()
