# backend/dynamodb_interface.py
import os
import time
from dotenv import load_dotenv
from decimal import Decimal
from aiobotocore.session import get_session
from typing import List, Dict, Any, Union, Literal, Optional
from pydantic import BaseModel
from database_models import *
from session_log_config import get_child_logger

logger = get_child_logger(os.path.abspath(__file__))

TABLE_NAME = os.getenv("DYNAMODB_TABLE_NAME")
AWS_REGION = os.getenv("AWS_REGION")

if not TABLE_NAME or not AWS_REGION:
    raise ValueError("Missing environment variables for DynamoDB configuration")

from boto3.dynamodb.types import TypeSerializer, TypeDeserializer

serializer = TypeSerializer()
deserializer = TypeDeserializer()

item_types = ['user', 'presentation', 'slide', 'topic', 'source']
item_types_literal = Literal['user', 'presentation', 'slide', 'topic', 'source']
item_ids_by_type = {
    'user': ['user_id'],
    'presentation': ['user_id', 'presentation_id'],
    'slide': ['user_id', 'presentation_id', 'slide_id'],
    'topic': ['user_id', 'presentation_id', 'topic_id'],
    'source': ['user_id', 'presentation_id', 'source_id']
}
# Utility functions

def log_debug(message: str, data: Any = None):
    if data:
        logger.debug(f"{message}: {data}")
    else:
        logger.debug(message)

def serialize_item(item: Dict[str, Any]) -> Dict[str, Any]:
    log_debug("Serializing item", item)
    return {k: serializer.serialize(v) for k, v in item.items()}

def deserialize_item(item: Dict[str, Any]) -> Dict[str, Any]:
    log_debug("Deserializing item", item)
    return {k: deserializer.deserialize(v) for k, v in item.items()}

def build_pk(item_type: str, identifiers: Dict[str, str]) -> str:
    user_id = identifiers.get('user_id')
    if not user_id:
        raise ValueError("Missing user_id in identifiers")
    
    log_debug(f"Building PK for item_type {item_type} with user_id {user_id}")
    
    if item_type in item_types:
        return f"USER#{user_id}"
    raise ValueError(f"Unknown item type: {item_type}")

def build_sk(item_type: str, identifiers: Dict[str, str]) -> str:
    log_debug(f"Building SK for item_type {item_type} with identifiers {identifiers}")
    
    if item_type == 'user':
        return 'PROFILE'
    elif item_type in ['presentation', 'slide', 'topic', 'source']:
        presentation_id = identifiers.get('presentation_id')
        if not presentation_id:
            raise ValueError(f"Missing presentation_id in identifiers for {item_type}")
        
        if item_type == 'presentation':
            return f"PRESENTATION#{presentation_id}"
        else:
            item_id = identifiers.get(f'{item_type}_id')
            if not item_id:
                raise ValueError(f"Missing {item_type}_id in identifiers")
            return f"PRESENTATION#{presentation_id}#{item_type.upper()}#{item_id}"
    
    raise ValueError(f"Unknown item type: {item_type}")

def build_keys(item_type: str, identifiers: Dict[str, str]) -> Dict[str, Dict[str, str]]:
    pk = build_pk(item_type, identifiers)
    sk = build_sk(item_type, identifiers)
    return {'PK': {'S': pk}, 'SK': {'S': sk}}

def build_gsi1sk() -> str:
    timestamp = int(time.time() * 1000)
    log_debug(f"Building GSI1SK with timestamp {timestamp}")
    return f"LASTUPDATE#{timestamp}"

def prepare_projection_expression(attributes: List[str]) -> Dict[str, Any]:
    if attributes:
        attributes = ['PK', 'SK', 'GSI1SK'] + attributes
        projection_expression = ', '.join([f'#{attr}' for attr in attributes])
        expression_attribute_names = {f'#{attr}': attr for attr in attributes}
        return {
            'ProjectionExpression': projection_expression,
            'ExpressionAttributeNames': expression_attribute_names
        }
    return {}

def convert_floats_to_decimals(item: Any) -> Any:
    """
    Recursively converts floats to Decimals in the given item, which can be a dictionary, list, or scalar value.
    """
    if isinstance(item, float):
        return Decimal(str(item))  # Convert float to Decimal
    elif isinstance(item, dict):
        return {key: convert_floats_to_decimals(value) for key, value in item.items()}
    elif isinstance(item, list):
        return [convert_floats_to_decimals(value) for value in item]
    else:
        return item

def build_update_expression(item_dict: Dict[str, Any], item_type: str) -> Dict[str, Any]:
    update_expression_parts = []
    expression_attribute_values = {}
    expression_attribute_names = {}

    # First, convert any floats to decimals in the item_dict
    item_dict = convert_floats_to_decimals(item_dict)

    for key, value in item_dict.items():
        if key not in ['PK', 'SK', 'last_updated', 'GSI1SK'] and key not in item_ids_by_type[item_type]:
            update_expression_parts.append(f'#{key} = :{key}')
            expression_attribute_values[f':{key}'] = serializer.serialize(value)
            expression_attribute_names[f'#{key}'] = key

    if item_type == 'presentation':
        update_expression_parts.append('#GSI1SK = :GSI1SK')
        expression_attribute_values[':GSI1SK'] = {'S': build_gsi1sk()}
        expression_attribute_names['#GSI1SK'] = 'GSI1SK'

    update_expression = 'SET ' + ', '.join(update_expression_parts)
    return {
        'UpdateExpression': update_expression,
        'ExpressionAttributeValues': expression_attribute_values,
        'ExpressionAttributeNames': expression_attribute_names
    }

def extract_identifiers(item_type: item_types_literal ,pk: str, sk: str, gsi1sk: Optional[str]) -> Dict[str, Optional[Union[str, int]]]:

    # Error if invalid pk or sk
    if not pk or not sk:
        logger.error(f"Invalid PK ({pk}) or SK ({sk})")

    user_id = pk.split('#')[1] if pk.startswith('USER#') else None

    sk_parts = sk.split('#')
    presentation_id = sk_parts[1] if len(sk_parts) > 1 and sk_parts[0] == 'PRESENTATION' else None
    item_id = sk_parts[3] if len(sk_parts) > 3 else None

    identifiers = {
        'user_id': user_id,
        'presentation_id': presentation_id,
    }

    if item_type=='presentation':
        try:
            if gsi1sk and gsi1sk.startswith('LASTUPDATED#'):
                identifiers['last_updated'] = int(gsi1sk.split('#')[1])
            else:
                identifiers['last_updated'] = None
        except Exception as e:
            identifiers['last_updated'] = None
            logger.warn(f"Error extracting last_updated from GSI1SK of presentation, not adding last_updated attribute: {e}")
    if item_id:
        item_type = sk_parts[2].lower() if len(sk_parts) > 2 else None
        if item_type:
            identifiers[f'{item_type}_id'] = item_id

    return {k: v for k, v in identifiers.items() if v is not None}

def create_model_instance(item_type: str, item_dict: Dict[str, Any], attributes: Optional[List[str]] = None) -> BaseModel:
    if item_type == 'slide':
        slide_type = item_dict.get('slide_type')
        model_cls = {
            'short_bullets_slide': ShortBulletsSlide,
            'markdown_slide': MarkdownSlide,
            'simple_mermaid_slide': SimpleMermaidSlide,
            'section_header_slide': SectionHeaderSlide,
            'presentation_title_slide': PresentationTitleSlide
        }.get(slide_type, BaseSlide)
    elif item_type == 'topic':
        model_cls = Topic
    else:
        raise ValueError(f"Unsupported item type for model creation: {item_type}")

    return (model_cls.partial() if attributes else model_cls).model_construct(**item_dict)

async def execute_db_operation(client, operation: str, params: Dict[str, Any]):
    log_debug(f"Executing {operation} with parameters", params)
    method = getattr(client, operation)
    return await method(**params)

# Function implementations

async def get_items(item_type: item_types_literal, 
                    identifiers: Union[Dict[str, str], List[Dict[str, str]]], 
                    attributes: Optional[List[str]] = None, 
                    return_type: Optional[Literal['dict', 'model']] = 'dict',
                    consistent_read: bool = False) -> Union[Dict, BaseModel, None, List[Union[Dict, None]], List[Union[BaseModel, None]]]:
    """
    Fetch one or multiple items of a specified type from the DynamoDB table.

    Args:
        item_type (item_types_literal): The type of item to fetch ('user', 'presentation', 'slide', 'topic', or 'source').
        identifiers (Union[Dict[str, str], List[Dict[str, str]]]): A dictionary or list of dictionaries containing identifiers for the item(s) to fetch.
        attributes (Optional[List[str]], optional): A list of specific attributes to retrieve. If None, all attributes are retrieved. Defaults to None.
        return_type (Optional[Literal['dict', 'model']], optional): The desired return type, either 'dict' or 'model'. Defaults to 'dict'. 'model' is only supported for 'slide' and 'topic' item types.
        consistent_read (bool, optional): Whether to use strongly consistent reads. Defaults to False.

    Returns:
        Union[Dict, BaseModel, None, List[Union[Dict, None]], List[Union[BaseModel, None]]]: If one item is fetched, a dictionary or model instance is returned. If multiple items are fetched, a list of dictionaries or model instances is returned. If no items match a provided identifier, None is returned in its place.

    Raises:
        ValueError: If an unsupported item type is provided for model creation or if required identifiers are missing.
        botocore.exceptions.ClientError: If an error occurs during the DynamoDB operation like AccessDeniedException which occurs when the IAM user does not have permission to perform the operation.
    """
    
    logger.debug(f"Fetching {item_type} items with identifiers: {identifiers}, consistent read: {consistent_read}")

    async with get_session().create_client('dynamodb', region_name=AWS_REGION) as client:
        is_single_item = isinstance(identifiers, dict)
        items_to_fetch = [identifiers] if is_single_item else identifiers

        keys_to_get = [build_keys(item_type, item_identifiers) for item_identifiers in items_to_fetch]
        projection_params = prepare_projection_expression(attributes)

        if len(items_to_fetch) == 1:
            request_params = {'TableName': TABLE_NAME, 'Key': keys_to_get[0], 'ConsistentRead': consistent_read, **projection_params}
            response = await execute_db_operation(client, 'get_item', request_params)
            items = [response.get('Item', {})] if 'Item' in response else []
        else:
            if consistent_read:
                logger.warning("Strongly consistent reads are not supported for BatchGetItem. Falling back to eventually consistent reads.")
            request_params = {TABLE_NAME: {'Keys': keys_to_get, **projection_params}}
            response = await execute_db_operation(client, 'batch_get_item', {'RequestItems': request_params})
            items = response.get('Responses', {}).get(TABLE_NAME, [])

        deserialized_items = {(item['PK']['S'], item['SK']['S']): deserialize_item(item) for item in items}

        sorted_items = []
        for key in keys_to_get:
            item = deserialized_items.get((key['PK']['S'], key['SK']['S']), None)
            if item:
                identifiers = extract_identifiers(item_type, key['PK']['S'], key['SK']['S'], item.get('GSI1SK'))
                filtered_item = {k: v for k, v in item.items() if k not in ['PK', 'SK', 'GSI1SK']}
                filtered_item.update(identifiers)
                sorted_items.append(filtered_item)
            else:
                sorted_items.append(None)

        if return_type == 'model' and item_type in ['slide', 'topic']:
            result = [create_model_instance(item_type, item, attributes) if item else None for item in sorted_items]
        else:
            result = sorted_items

        logger.info(f"Fetched {len(result)} {item_type} items. {len([item for item in result if item is not None])} found")
        return result[0] if is_single_item and result else result

async def update_items(item_type: item_types_literal, 
                       items: Union[List[Dict], List[BaseModel]]) -> None:
    """
    Update one or multiple items of a specified type in the DynamoDB table.

    Args:
        item_type (item_types_literal): The type of item to update ('user', 'presentation', 'slide', 'topic', or 'source').
        items (Union[List[Dict], List[BaseModel]]): A list of dictionaries or BaseModel instances representing the items to update.

    Returns:
        None

    Note:
        This function uses either UpdateItem for a single item or TransactWriteItems for multiple items.
    """

    logger.debug(f"Preparing to update {len(items)} {item_type} items")

    async with get_session().create_client('dynamodb', region_name=AWS_REGION) as client:
        items_to_update = []
        for item in items:
            item_dict = item.model_dump() if isinstance(item, BaseModel) else item
            keys = build_keys(item_type, item_dict)
            update_expression_params = build_update_expression(item_dict, item_type)

            items_to_update.append({
                'Update': {
                    'TableName': TABLE_NAME,
                    'Key': keys,
                    **update_expression_params
                }
            })

        if len(items_to_update) == 1:
            await execute_db_operation(client, 'update_item', items_to_update[0]['Update'])
        else:
            await execute_db_operation(client, 'transact_write_items', {'TransactItems': items_to_update})

        logger.info(f"Updated {len(items)} {item_type} items successfully")

async def delete_items(item_type: Literal['user', 'presentation', 'slide', 'topic', 'source'], 
                       identifiers: List[Dict[str, str]]) -> None:
    """
    Delete one or multiple items of a specified type from the DynamoDB table.

    Args:
        item_type (Literal['user', 'presentation', 'slide', 'topic', 'source']): The type of item to delete.
        identifiers (List[Dict[str, str]]): A list of dictionaries containing identifiers for the items to delete.

    Returns:
        None

    Note:
        This function uses either DeleteItem for a single item or TransactWriteItems for multiple items.
    """
    logger.debug(f"Preparing to delete {len(identifiers)} {item_type} items")

    async with get_session().create_client('dynamodb', region_name=AWS_REGION) as client:
        items_to_delete = []
        for item_identifiers in identifiers:
            pk = build_pk(item_type, item_identifiers)
            sk = build_sk(item_type, item_identifiers)
            items_to_delete.append({
                'Delete': {
                    'TableName': TABLE_NAME,
                    'Key': {'PK': {'S': pk}, 'SK': {'S': sk}}
                }
            })

        if len(items_to_delete) == 1:
            await execute_db_operation(client, 'delete_item', {'TableName': TABLE_NAME, 'Key': items_to_delete[0]['Delete']['Key']})
        else:
            await execute_db_operation(client, 'transact_write_items', {'TransactItems': items_to_delete})

        logger.info(f"Deleted {len(items_to_delete)} {item_type} items successfully")

async def get_all_items_for_presentation(
    item_type: Literal['slide', 'topic', 'source'],
    user_id: str,
    presentation_id: str,
    attributes: Optional[List[str]] = None,
    return_type: Optional[Literal['model', 'dict']] = 'dict',
    consistent_read: bool = False
) -> Union[List[Dict], List[BaseModel]]:
    """
    Fetch all items of a specified type for a given presentation.

    Args:
        item_type (Literal['slide', 'topic', 'source']): The type of items to fetch.
        user_id (str): The ID of the user who owns the presentation.
        presentation_id (str): The ID of the presentation.
        attributes (Optional[List[str]], optional): A list of specific attributes to retrieve. If None, all attributes are retrieved. Defaults to None.
        return_type (Optional[Literal['model', 'dict']], optional): The desired return type, either 'dict' or 'model'. Defaults to 'dict'.
        consistent_read (bool, optional): Whether to use strongly consistent reads. Defaults to False.

    Returns:
        Union[List[Dict], List[BaseModel]]: A list of fetched items in the specified return type.

    Note:
        This function uses a Query operation to fetch all items of the specified type for the given presentation.
    """

    logger.debug(f"Fetching all {item_type}s for presentation {presentation_id} of user {user_id}, consistent read: {consistent_read}")

    async with get_session().create_client('dynamodb', region_name=AWS_REGION) as client:
        query_params = {
            'TableName': TABLE_NAME,
            'KeyConditionExpression': '#PK = :pk AND begins_with(#SK, :sk_prefix)',
            'ExpressionAttributeNames': {
                '#PK': 'PK',
                '#SK': 'SK'
            },
            'ExpressionAttributeValues': {
                ':pk': {'S': f"USER#{user_id}"},
                ':sk_prefix': {'S': f"PRESENTATION#{presentation_id}#{item_type.upper()}#"}
            },
            'ConsistentRead': consistent_read
        }

        if attributes:
            query_params.update(prepare_projection_expression(attributes))

        response = await execute_db_operation(client, 'query', query_params)
        items = response.get('Items', [])

        deserialized_items = [deserialize_item(item) for item in items]

        for item in deserialized_items:
            identifiers = extract_identifiers(item_type, item['PK'], item['SK'], item.get('GSI1SK'))
            filtered_item = {k: v for k, v in item.items() if k not in ['PK', 'SK', 'GSI1SK']}
            filtered_item.update(identifiers)
            item.update(filtered_item)

        if return_type == 'model' and item_type in ['slide', 'topic']:
            result = [create_model_instance(item_type, item, attributes) for item in deserialized_items]
        else:
            result = deserialized_items

        logger.info(f"Fetched {len(result)} {item_type}s for presentation {presentation_id}")
        return result
    
async def delete_all_items_for_presentation(
    item_type: Literal['slide', 'topic', 'source'],
    user_id: str,
    presentation_id: str,
) -> None:
    """
    Delete all items of a specified type for a given presentation.

    Args:
        item_type (Literal['slide', 'topic', 'source']): The type of items to delete.
        user_id (str): The ID of the user who owns the presentation.
        presentation_id (str): The ID of the presentation.

    Returns:
        None

    Note:
        This function first queries for all items of the specified type for the given presentation,
        then uses TransactWriteItems to delete the items in batches of 25 (DynamoDB limit).
    """
    
    logger.debug(f"Deleting all {item_type}s for presentation {presentation_id} of user {user_id}")

    async with get_session().create_client('dynamodb', region_name=AWS_REGION) as client:
        query_params = {
            'TableName': TABLE_NAME,
            'KeyConditionExpression': '#PK = :pk AND begins_with(#SK, :sk_prefix)',
            'ExpressionAttributeNames': {
                '#PK': 'PK',
                '#SK': 'SK'
            },
            'ExpressionAttributeValues': {
                ':pk': {'S': f"USER#{user_id}"},
                ':sk_prefix': {'S': f"PRESENTATION#{presentation_id}#{item_type.upper()}#"}
            },
            'ProjectionExpression': 'PK, SK'
        }

        items_to_delete = []
        paginator = client.get_paginator('query')
        async for page in paginator.paginate(**query_params):
            items_to_delete.extend(page.get('Items', []))

        if not items_to_delete:
            logger.info(f"No {item_type}s found for presentation {presentation_id}")
            return

        delete_requests = [
            {'Delete': {'TableName': TABLE_NAME, 'Key': item}}
            for item in items_to_delete
        ]

        for i in range(0, len(delete_requests), 25):
            batch = delete_requests[i:i+25]
            await execute_db_operation(client, 'transact_write_items', {'TransactItems': batch})

        logger.info(f"Deleted {len(items_to_delete)} {item_type}s for presentation {presentation_id}")