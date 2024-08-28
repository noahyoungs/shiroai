import os
import time
import json
import boto3
from dotenv import load_dotenv
from typing import List, Dict
from slide_models import *

load_dotenv()

# Load environment variables
AWS_REGION = os.getenv('AWS_REGION')

# Reserved DynamoDB attribute names
reserved_attrs = ['status', 'type', 'order', 'content', 'user', 'name', 'url']

# Initialize a Boto3 client for DynamoDB
dynamodb_client = boto3.client('dynamodb', region_name=AWS_REGION)

def get_table():
    """Get the DynamoDB table name."""
    response = dynamodb_client.describe_table(TableName=os.getenv('DYNAMODB_TABLE_NAME'))
    return response['Table']['TableName']

def get_all_slides(presentation_id, attributes=None) -> List[Dict]:
    """
    Retrieve all slides in a presentation.
    """
    table_name = get_table()

    key_condition_expression = 'PK = :pk AND begins_with(SK, :sk)'
    expression_attribute_values = {
        ':pk': {'S': f'PRESENTATION#{presentation_id}'},
        ':sk': {'S': 'SLIDE#'}
    }

    print(f"Querying DynamoDB with KeyConditionExpression: {key_condition_expression}")
    print(f"ExpressionAttributeValues: {expression_attribute_values}")

    # Initialize variables for query parameters
    query_params = {
        "TableName": table_name,
        "KeyConditionExpression": key_condition_expression,
        "ExpressionAttributeValues": expression_attribute_values
    }

    if attributes:
        expression_attribute_names = {}
        for attr in attributes:
            if attr in reserved_attrs:
                expression_attribute_names[f'#{attr}'] = attr
        projection_expression = ', '.join(
            f'#{attr}' if attr in reserved_attrs else attr for attr in attributes)
        
        query_params["ProjectionExpression"] = projection_expression
        
        if expression_attribute_names:
            query_params["ExpressionAttributeNames"] = expression_attribute_names

    response = dynamodb_client.query(**query_params)

    print(f"DynamoDB response: {response}")

    if not response['Items']:
        print(f"No slides found for presentation ID {presentation_id}.")
        return []

    slides = []
    for item in response['Items']:
        simplified_item = {}
        for k, v in item.items():
            if k == 'SK':
                simplified_item['id'] = v['S'].split('#')[1]
            elif k == 'PK':
                simplified_item['presentation_id'] = v['S'].split('#')[1]
            elif 'S' in v:
                try:
                    simplified_item[k] = json.loads(v['S'])
                except json.JSONDecodeError:
                    simplified_item[k] = v['S']
            elif 'N' in v:
                simplified_item[k] = int(v['N'])
            elif 'BOOL' in v:
                simplified_item[k] = v['BOOL']

        slides.append(simplified_item)
        
            

    return slides

def update_presentation(presentation_id, **kwargs):
    """
    Update attributes of a presentation in the DynamoDB table.

    Args:
        presentation_id (str): The ID of the presentation to update.
        **kwargs: Arbitrary keyword arguments representing the attributes and their values to update.

    Returns:
        dict: The updated attributes of the presentation.
    """
    table_name = get_table()
    
    update_expression = 'SET '
    expression_attribute_values = {}
    expression_attribute_names = {}
    for key, value in kwargs.items():
        # Use reserved keyword handling for known attributes
        if key in reserved_attrs:
            attr_name_key = f'#{key}'
            update_expression += f'{attr_name_key} = :{key}, '
            expression_attribute_names[attr_name_key] = key
        else:
            update_expression += f'{key} = :{key}, '
        # Set the value type based on Python type
        if isinstance(value, str):
            expression_attribute_values[f':{key}'] = {'S': value}
        elif isinstance(value, int):
            expression_attribute_values[f':{key}'] = {'N': str(value)}
        elif isinstance(value, bool):
            expression_attribute_values[f':{key}'] = {'BOOL': value}
    
    # Set the time_updated attribute to the current Unix timestamp
    current_timestamp = int(time.time())
    update_expression += '#time_updated = :time_updated, '
    expression_attribute_names['#time_updated'] = 'time_updated'
    expression_attribute_values[':time_updated'] = {'N': str(current_timestamp)}
    
    # Remove the trailing comma and space from the update expression
    update_expression = update_expression.rstrip(', ')
    
    update_params = {
        "TableName": table_name,
        "Key": {
            'PK': {'S': f'PRESENTATION#{presentation_id}'},
            'SK': {'S': f'PRESENTATION#{presentation_id}'}
        },
        "UpdateExpression": update_expression,
        "ExpressionAttributeValues": expression_attribute_values,
        "ExpressionAttributeNames": expression_attribute_names,
        "ReturnValues": 'ALL_NEW'
    }
    
    response = dynamodb_client.update_item(**update_params)
    return response['Attributes']

def get_presentation(presentation_id, attributes=None):
    """
    Retrieve a presentation from the DynamoDB table.

    Args:
        presentation_id (str): The ID of the presentation to retrieve.
        attributes (list, optional): A list of attribute names to retrieve. If not provided, all attributes will be retrieved.

    Returns:
        dict: A dictionary representing the retrieved presentation with simplified attribute values.
              The dictionary includes the original presentation ID as the "id" key.
        None: If the presentation is not found in the table.
    """
    table_name = get_table()
    
    key = {
        'PK': {'S': f'PRESENTATION#{presentation_id}'},
        'SK': {'S': f'PRESENTATION#{presentation_id}'}
    }
    
    if attributes:
        projection_expression = ', '.join(
            f'#{attr}' if attr in reserved_attrs else attr for attr in attributes)
        expression_attribute_names = {
            f'#{attr}': attr for attr in attributes if attr in reserved_attrs}
        if expression_attribute_names:
            response = dynamodb_client.get_item(
                TableName=table_name,
                Key=key,
                ProjectionExpression=projection_expression,
                ExpressionAttributeNames=expression_attribute_names
            )
        else:
            response = dynamodb_client.get_item(
                TableName=table_name,
                Key=key,
                ProjectionExpression=projection_expression
            )
    else:
        response = dynamodb_client.get_item(TableName=table_name, Key=key)
    
    if 'Item' in response:
        item = response['Item']
        simplified_item = {'id': presentation_id}
        for k, v in item.items():
            if 'S' in v:
                simplified_item[k] = v['S']
            elif 'N' in v:
                simplified_item[k] = int(v['N'])
            elif 'BOOL' in v:
                simplified_item[k] = v['BOOL']
        return simplified_item
    else:
        return None