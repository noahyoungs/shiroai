import os
import time
from dotenv import load_dotenv
from aiobotocore.session import get_session
import json
from typing import List, Dict, Any
import asyncio
from uuid_extensions import uuid7str
load_dotenv()

AWS_REGION = os.getenv('AWS_REGION')

reserved_attrs = ['status', 'type', 'order', 'content', 'user', 'name', 'url']


async def get_table():
    session = get_session()
    async with session.create_client('dynamodb', region_name=AWS_REGION) as client:
        response = await client.describe_table(TableName='AiPresenter2')
        return response['Table']['TableName']


async def get_presentation(presentation_id, attributes=None):
    """
   Retrieve a presentation from the DynamoDB table.

   Args:
       presentation_id (str): The ID of the presentation to retrieve.
       attributes (list, optional): A list of attribute names to retrieve. If not provided, all attributes will be retrieved.

   Returns:
       dict: A dictionary representing the retrieved presentation with simplified attribute values.
             The dictionary includes the original presentation ID as the "id" key.
       None: If the presentation is not found in the table.

   Description:
       This function retrieves a presentation from the DynamoDB table based on the provided presentation ID.
       It allows specifying a list of attribute names to retrieve, enabling projection of specific attributes.
       The function handles reserved keywords in the attribute names using expression attribute names.
       It uses the DynamoDB GetItem API to retrieve the item and simplifies the attribute values in the returned dictionary.

   Raises:
       botocore.exceptions.ClientError: If an error occurs while retrieving the item from DynamoDB.

   Example:
       presentation = await get_presentation('presentation123', attributes=['title', 'description', 'created_at'])
       if presentation:
           print(presentation)
       else:
           print("Presentation not found")
   """
    table_name = await get_table()
    async with get_session().create_client('dynamodb', region_name=AWS_REGION) as client:
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
                response = await client.get_item(TableName=table_name, Key=key, ProjectionExpression=projection_expression, ExpressionAttributeNames=expression_attribute_names)
            else:
                response = await client.get_item(TableName=table_name, Key=key, ProjectionExpression=projection_expression)
        else:
            response = await client.get_item(TableName=table_name, Key=key)
        if 'Item' in response:
            item = response['Item']
            # Add the original presentation ID as "id" in the returned dict
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


async def update_presentation(presentation_id, **kwargs):
    """
   Update attributes of a presentation in the DynamoDB table.

   Args:
       presentation_id (str): The ID of the presentation to update.
       **kwargs: Arbitrary keyword arguments representing the attributes and their values to update.

   Returns:
       dict: The updated attributes of the presentation.

   Description:
       This function updates the specified attributes of a presentation in the DynamoDB table.
       It constructs an update expression based on the provided keyword arguments, handling
       reserved keywords and different value types (string, integer, boolean).
       The function also updates the 'time_updated' attribute with the current Unix timestamp.
       It uses the DynamoDB UpdateItem API to perform the update operation and returns the
       updated attributes of the presentation.

   Raises:
       botocore.exceptions.ClientError: If an error occurs while updating the item in DynamoDB.

   Example:
       updated_attrs = await update_presentation(
           'presentation123',
           title='New Title',
           description='Updated description',
           is_published=True
       )
   """
    table_name = await get_table()
    async with get_session().create_client('dynamodb', region_name=AWS_REGION) as client:
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
        expression_attribute_values[':time_updated'] = {
            'N': str(current_timestamp)}
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
        response = await client.update_item(**update_params)
        return response['Attributes']


async def increment_presentation_attribute(presentation_id, attribute_key, increment_value):
    """
    Increment a numeric attribute of a presentation in the DynamoDB table.
    If the attribute doesn't exist, it will be created with the given increment_value.

    Args:
        presentation_id (str): The ID of the presentation to update.
        attribute_key (str): The name of the attribute to increment.
        increment_value (int or float): The value to increment the attribute by.

    Returns:
        dict: The updated attribute value of the presentation.

    Description:
        This function increments a specified numeric attribute of a presentation in the DynamoDB table.
        If the attribute doesn't exist, it will be created with the given increment_value.
        It uses the DynamoDB UpdateItem API with the ADD action to increment the attribute value.
        The function returns the updated value of the attribute.

    Raises:
        botocore.exceptions.ClientError: If an error occurs while updating the item in DynamoDB.
        ValueError: If the increment_value is not a numeric value.

    Example:
        updated_attribute = await increment_presentation_attribute(
            'presentation123',
            'view_count',
            1
        )
    """
    if not isinstance(increment_value, (int, float)):
        raise ValueError("The increment_value must be a numeric value.")

    table_name = await get_table()

    async with get_session().create_client('dynamodb', region_name=AWS_REGION) as client:
        update_params = {
            "TableName": table_name,
            "Key": {
                'PK': {'S': f'PRESENTATION#{presentation_id}'},
                'SK': {'S': f'PRESENTATION#{presentation_id}'}
            },
            "UpdateExpression": f"SET {attribute_key} = if_not_exists({attribute_key}, :start) + :increment",
            "ExpressionAttributeValues": {
                ":start": {'N': '0'},
                ":increment": {'N': str(increment_value)}
            },
            "ReturnValues": "UPDATED_NEW"
        }

        response = await client.update_item(**update_params)

    return response['Attributes'][attribute_key]


async def get_sources(presentation_id, attributes=None):
    table_name = await get_table()
    async with get_session().create_client('dynamodb', region_name=AWS_REGION) as client:
        key_condition_expression = 'PK = :pk AND begins_with(SK, :sk)'
        expression_attribute_values = {
            ':pk': {'S': f'PRESENTATION#{presentation_id}'},
            ':sk': {'S': 'SOURCE#'}
        }

        if attributes:
            projection_expression = ', '.join(attributes)
            response = await client.query(
                TableName=table_name,
                KeyConditionExpression=key_condition_expression,
                ExpressionAttributeValues=expression_attribute_values,
                ProjectionExpression=projection_expression
            )
        else:
            response = await client.query(
                TableName=table_name,
                KeyConditionExpression=key_condition_expression,
                ExpressionAttributeValues=expression_attribute_values
            )

        sources = []
        for item in response['Items']:
            simplified_item = {}
            for k, v in item.items():
                if k == 'SK':
                    simplified_item['id'] = v['S'].split('#')[1]
                elif k == 'PK':
                    simplified_item['presentation_id'] = v['S'].split('#')[1]
                elif k == 'web_source':
                    simplified_item[k] = json.loads(v['S'])
                elif 'S' in v:
                    simplified_item[k] = v['S']
                elif 'N' in v:
                    simplified_item[k] = int(v['N'])
                elif 'BOOL' in v:
                    simplified_item[k] = v['BOOL']
            sources.append(simplified_item)

        return sources


async def get_source(presentation_id, source_id, attributes=None):
    """
    Retrieve a source item from the DynamoDB table based on the provided presentation ID and source ID.

    Args:
        presentation_id (str): The ID of the presentation associated with the source.
        source_id (str): The ID of the source to retrieve.
        attributes (list, optional): A list of attributes to retrieve from the source item. If not provided,
            all attributes will be retrieved. Defaults to None.

    Returns:
        dict: A dictionary representing the simplified source item with the specified attributes.
            The dictionary contains the following keys:
            - 'id' (str): The ID of the source.
            - 'presentation_id' (str): The ID of the presentation associated with the source.
            - Other keys based on the retrieved attributes.
            If the source item is not found, None is returned.

    Raises:
        botocore.exceptions.ClientError: If an error occurs while interacting with the DynamoDB table.

    Description:
        This function retrieves a source item from the DynamoDB table based on the provided presentation ID
        and source ID. It uses the DynamoDB GetItem operation to fetch the item.

        If the `attributes` parameter is provided, only the specified attributes will be retrieved from the
        source item. The function constructs a projection expression based on the provided attributes.

        The retrieved item is simplified by converting the DynamoDB attribute values to their corresponding
        Python data types. The 'SK' attribute is used to extract the source ID, and the 'PK' attribute is
        used to extract the presentation ID. The 'web_source' attribute, if present, is parsed as JSON.

        If the source item is found, the simplified item is returned as a dictionary. If the source item is
        not found, None is returned.
    """

    table_name = await get_table()
    async with get_session().create_client('dynamodb', region_name=AWS_REGION) as client:
        key = {
            'PK': {'S': f'PRESENTATION#{presentation_id}'},
            'SK': {'S': f'SOURCE#{source_id}'}
        }

        if attributes:
            projection_expression = ', '.join(attributes)
            response = await client.get_item(
                TableName=table_name,
                Key=key,
                ProjectionExpression=projection_expression
            )
        else:
            response = await client.get_item(
                TableName=table_name,
                Key=key
            )

        if 'Item' in response:
            item = response['Item']
            simplified_item = {}
            for k, v in item.items():
                if k == 'SK':
                    simplified_item['id'] = v['S'].split('#')[1]
                elif k == 'PK':
                    simplified_item['presentation_id'] = v['S'].split('#')[1]
                elif k == 'web_source':
                    simplified_item[k] = json.loads(v['S'])
                elif 'S' in v:
                    simplified_item[k] = v['S']
                elif 'N' in v:
                    simplified_item[k] = int(v['N'])
                elif 'BOOL' in v:
                    simplified_item[k] = v['BOOL']
            return simplified_item
        else:
            return None


async def update_source(presentation_id, source_id, **kwargs):
    """
    Update the attributes of a source in the DynamoDB table.

    Parameters:
        presentation_id (str): The ID of the presentation.
        source_id (str): The ID of the source to update.
        **kwargs: Arbitrary keyword arguments representing the attributes to update.
            Each key-value pair in kwargs corresponds to an attribute and its new value.
            Supported attribute types are:
                - String attributes
                - Numeric attributes (passed as int)
                - Boolean attributes
                - 'web_source' attribute (passed as a dictionary, will be JSON-serialized)

    Returns:
        dict: The updated source item attributes.

    Raises:
        botocore.exceptions.ClientError: If an error occurs during the DynamoDB update operation.

    Example:
        # Update the 'name' and 'enabled' attributes of a source
        updated_source = await update_source(
            presentation_id='123',
            source_id='456',
            name='Updated Source Name',
            enabled=True
        )
    """
    table_name = await get_table()
    async with get_session().create_client('dynamodb', region_name=AWS_REGION) as client:
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
            if key == 'web_source':
                expression_attribute_values[f':{key}'] = {
                    'S': json.dumps(value)}
            elif isinstance(value, str):
                expression_attribute_values[f':{key}'] = {'S': value}
            elif isinstance(value, int):
                expression_attribute_values[f':{key}'] = {'N': str(value)}
            elif isinstance(value, bool):
                expression_attribute_values[f':{key}'] = {'BOOL': value}

        # Set the time_updated attribute to the current Unix timestamp
        current_timestamp = int(time.time())
        update_expression += '#time_updated = :time_updated, '
        expression_attribute_names['#time_updated'] = 'time_updated'
        expression_attribute_values[':time_updated'] = {
            'N': str(current_timestamp)}

        # Remove the trailing comma and space from the update expression
        update_expression = update_expression.rstrip(', ')

        update_params = {
            "TableName": table_name,
            "Key": {
                'PK': {'S': f'PRESENTATION#{presentation_id}'},
                'SK': {'S': f'SOURCE#{source_id}'}
            },
            "UpdateExpression": update_expression,
            "ExpressionAttributeValues": expression_attribute_values,
            "ExpressionAttributeNames": expression_attribute_names,
            "ReturnValues": 'ALL_NEW'
        }

        response = await client.update_item(**update_params)

        return response['Attributes']


async def delete_source(presentation_id, source_id):
   """
   Delete a source from the DynamoDB table.

   This function deletes a source item from the DynamoDB table based on the provided
   presentation ID and source ID. It constructs the primary key (PK) and sort key (SK)
   using the provided IDs and attempts to delete the item from the table.

   Args:
       presentation_id (str): The ID of the presentation associated with the source.
       source_id (str): The ID of the source to be deleted.

   Returns:
       bool: True if the source is successfully deleted, False otherwise.

   Raises:
       Exception: If an error occurs during the deletion process.

   Example:
       result = await delete_source("presentation123", "source456")
       if result:
           print("Source deleted successfully.")
       else:
           print("Failed to delete the source.")
   """
   table_name = await get_table()

   async with get_session().create_client('dynamodb', region_name=AWS_REGION) as client:
       key = {
           'PK': {'S': f'PRESENTATION#{presentation_id}'},
           'SK': {'S': f'SOURCE#{source_id}'}
       }

       try:
           response = await client.delete_item(
               TableName=table_name,
               Key=key
           )

           if response['ResponseMetadata']['HTTPStatusCode'] == 200:
               return True
           else:
               return False
       except Exception as e:
           print(f"Error deleting source: {e}")
           return False


async def batch_update_sources(presentation_id: str, sources: List[Dict[str, Any]]) -> bool:
    """
    Update multiple sources for a given presentation in a single DynamoDB transaction.

    Args:
        presentation_id (str): The ID of the presentation to which the sources belong.
        sources (List[Dict[str, Any]]): A list of source dictionaries to be updated. Each dictionary must contain an 'id' key.

    Returns:
        bool: True if the update operation was successful, False otherwise.

    Description:
        This function updates multiple sources for a given presentation in a single DynamoDB transaction.
        It iterates over each source dictionary in the 'sources' list and constructs an update request for each source.
        The update request includes the necessary update expressions, attribute values, and attribute names.
        The function handles reserved keywords for known attributes and sets the 'time_updated' attribute to the current Unix timestamp.
        The update requests are then executed in a single DynamoDB transact_write_items operation.

    Notes:
        - This function assumes the existence of a 'get_table' function that returns the name of the DynamoDB table.
        - The function uses the 'get_session' function to create a DynamoDB client session.
        - The 'reserved_attrs' variable is assumed to be defined and contains a list of reserved attribute names.
        - The function creates a copy of each source dictionary to avoid modifying the original dictionaries.
        - The function returns True if the update operation was successful (HTTP status code 200), False otherwise.

    Example:
        sources = [
            {'id': '1', 'name': 'Source 1', 'description': 'Description 1'},
            {'id': '2', 'name': 'Source 2', 'description': 'Description 2'}
        ]
        success = await batch_update_sources('presentation123', sources)
        if success:
            print("Sources updated successfully.")
        else:
            print("Failed to update sources.")
    """

    table_name = await get_table()

    async with get_session().create_client('dynamodb', region_name=AWS_REGION) as client:
        update_requests = []
        current_timestamp = int(time.time())

        for source in sources:
            source_copy = source.copy()  # Create a copy of the source dictionary
            source_id = source_copy.pop('id')

            update_expression = 'SET '
            expression_attribute_values = {}
            expression_attribute_names = {}

            for key, value in source_copy.items():
                if key == 'web_source':
                    update_expression += '#web_source = :web_source, '
                    expression_attribute_names['#web_source'] = 'web_source'
                    expression_attribute_values[':web_source'] = {
                        'S': json.dumps(value)}
                else:
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
                        expression_attribute_values[f':{key}'] = {
                            'N': str(value)}
                    elif isinstance(value, bool):
                        expression_attribute_values[f':{key}'] = {
                            'BOOL': value}

            # Set the time_updated attribute to the current Unix timestamp
            update_expression += '#time_updated = :time_updated'
            expression_attribute_names['#time_updated'] = 'time_updated'
            expression_attribute_values[':time_updated'] = {
                'N': str(current_timestamp)}

            # Remove the trailing comma and space from the update expression
            update_expression = update_expression.rstrip(', ')

            # print("Update Expression:", update_expression)
            # print("Expression Attribute Values:", expression_attribute_values)
            # print("Expression Attribute Names:", expression_attribute_names)

            update_request = {
                "Update": {
                    "TableName": table_name,
                    "Key": {
                        'PK': {'S': f'PRESENTATION#{presentation_id}'},
                        'SK': {'S': f'SOURCE#{source_id}'}
                    },
                    "UpdateExpression": update_expression,
                    "ExpressionAttributeValues": expression_attribute_values,
                    "ExpressionAttributeNames": expression_attribute_names
                }
            }
            update_requests.append(update_request)

        response = await client.transact_write_items(TransactItems=update_requests)

        if response['ResponseMetadata']['HTTPStatusCode'] == 200:
            return True
        else:
            return False


async def update_slide(presentation_id, slide_id, **kwargs):
    """
   Update a single slide in a presentation.

   Args:
       presentation_id (str): The ID of the presentation.
       slide_id (str): The ID of the slide to update.
       **kwargs: Keyword arguments representing the attributes to update.

   Returns:
       dict: The updated slide attributes.
   """
    table_name = await get_table()
    async with get_session().create_client('dynamodb', region_name=AWS_REGION) as client:
        update_expression = 'SET '
        expression_attribute_values = {}
        expression_attribute_names = {}

        def set_default(obj):
            if isinstance(obj, set):
                return list(obj)
            raise TypeError(
                f'Object of type {obj.__class__.__name__} is not JSON serializable')

        for key, value in kwargs.items():
            if isinstance(value, (list, dict, set)):
                value = json.dumps(value, default=set_default)

            # Use reserved keyword handling for known attributes
            if key in reserved_attrs:
                attr_name_key = f'#{key}'
                update_expression += f'{attr_name_key} = :{key}, '
                expression_attribute_names[attr_name_key] = key
            else:
                update_expression += f'{key} = :{key}, '

            # Set the value type based on Python type
            if type(value) == str:
                expression_attribute_values[f':{key}'] = {'S': value}
            elif type(value) == int:
                expression_attribute_values[f':{key}'] = {'N': str(value)}
            elif type(value) == bool:
                expression_attribute_values[f':{key}'] = {'BOOL': value}
            else:
                expression_attribute_values[f':{key}'] = {'S': str(value)}

        # Set the time_updated attribute to the current Unix timestamp
        current_timestamp = int(time.time())
        update_expression += '#time_updated = :time_updated, '
        expression_attribute_names['#time_updated'] = 'time_updated'
        expression_attribute_values[':time_updated'] = {
            'N': str(current_timestamp)}

        # Remove the trailing comma and space from the update expression
        update_expression = update_expression.rstrip(', ')

        update_params = {
            "TableName": table_name,
            "Key": {
                'PK': {'S': f'PRESENTATION#{presentation_id}'},
                'SK': {'S': f'SLIDE#{slide_id}'}
            },
            "UpdateExpression": update_expression,
            "ExpressionAttributeValues": expression_attribute_values,
            "ExpressionAttributeNames": expression_attribute_names,
            "ReturnValues": 'ALL_NEW'
        }

        response = await client.update_item(**update_params)
        return response['Attributes']


async def batch_update_slides(presentation_id: str, slides: List[Dict[str, Any]]) -> bool:
    """
    Update multiple slides in a presentation in a batch operation.

    Args:
        presentation_id (str): The ID of the presentation.
        slides (List[Dict[str, Any]]): A list of dictionaries representing the slides to update.

    Returns:
        bool: True if the batch update was successful, False otherwise.
    """
    table_name = await get_table()
    async with get_session().create_client('dynamodb', region_name=AWS_REGION) as client:
        update_requests = []
        current_timestamp = int(time.time())

        for slide in slides:
            slide_copy = slide.copy()  # Create a copy of the slide dictionary
            slide_id = slide_copy.pop('id')

            update_expression = 'SET '
            expression_attribute_values = {}
            expression_attribute_names = {}

            for key, value in slide_copy.items():
                if isinstance(value, (list, dict)):
                    value = json.dumps(value)

                # Use reserved keyword handling for known attributes
                if key in reserved_attrs:
                    attr_name_key = f'#{key}'
                    update_expression += f'{attr_name_key} = :{key}, '
                    expression_attribute_names[attr_name_key] = key
                else:
                    update_expression += f'{key} = :{key}, '

                value_type = type(value)
                if value_type == str:
                    expression_attribute_values[f':{key}'] = {'S': value}
                elif value_type == int:
                    expression_attribute_values[f':{key}'] = {'N': str(value)}
                elif value_type == bool:
                    expression_attribute_values[f':{key}'] = {'BOOL': value}

            # Remove the trailing comma and space from the update expression
            update_expression = update_expression.rstrip(', ')

            # Set the time_updated attribute to the current Unix timestamp
            update_expression += ', #time_updated = :time_updated'
            expression_attribute_names['#time_updated'] = 'time_updated'
            expression_attribute_values[':time_updated'] = {'N': str(current_timestamp)}

            update_request = {
                "Update": {
                    "TableName": table_name,
                    "Key": {
                        'PK': {'S': f'PRESENTATION#{presentation_id}'},
                        'SK': {'S': f'SLIDE#{slide_id}'}
                    },
                    "UpdateExpression": update_expression,
                    "ExpressionAttributeValues": expression_attribute_values,
                    "ExpressionAttributeNames": expression_attribute_names
                }
            }

            update_requests.append(update_request)

        response = await client.transact_write_items(TransactItems=update_requests)

        if response['ResponseMetadata']['HTTPStatusCode'] == 200:
            return True
        else:
            return False
        
async def get_slides(presentation_id, attributes=None):
    """
    Retrieve all slides in a presentation.

    Args:
        presentation_id (str): The ID of the presentation.
        attributes (Optional[List[str]]): A list of attributes to retrieve for each slide.

    Returns:
        List[dict]: A list of dictionaries representing the slides.
    """
    table_name = await get_table()
    async with get_session().create_client('dynamodb', region_name=AWS_REGION) as client:
        key_condition_expression = 'PK = :pk AND begins_with(SK, :sk)'
        expression_attribute_values = {
            ':pk': {'S': f'PRESENTATION#{presentation_id}'},
            ':sk': {'S': 'SLIDE#'}
        }

        if attributes:
            expression_attribute_names = {}
            for attr in attributes:
                if attr in reserved_attrs:
                    expression_attribute_names[f'#{attr}'] = attr
            projection_expression = ', '.join(f'#{attr}' if attr in reserved_attrs else attr for attr in attributes)
            response = await client.query(
                TableName=table_name,
                KeyConditionExpression=key_condition_expression,
                ExpressionAttributeValues=expression_attribute_values,
                ProjectionExpression=projection_expression,
                ExpressionAttributeNames=expression_attribute_names
            )
        else:
            response = await client.query(
                TableName=table_name,
                KeyConditionExpression=key_condition_expression,
                ExpressionAttributeValues=expression_attribute_values
            )

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

async def get_slide(presentation_id, slide_id, attributes=None):
    """
    Retrieve a single slide from a presentation.

    Args:
        presentation_id (str): The ID of the presentation.
        slide_id (str): The ID of the slide to retrieve.
        attributes (Optional[List[str]]): A list of attributes to retrieve for the slide.

    Returns:
        dict: A dictionary representing the slide, or None if the slide is not found.
    """
    table_name = await get_table()
    async with get_session().create_client('dynamodb', region_name=AWS_REGION) as client:
        key = {
            'PK': {'S': f'PRESENTATION#{presentation_id}'},
            'SK': {'S': f'SLIDE#{slide_id}'}
        }

        if attributes:
            expression_attribute_names = {}
            for attr in attributes:
                if attr in reserved_attrs:
                    expression_attribute_names[f'#{attr}'] = attr
            projection_expression = ', '.join(f'#{attr}' if attr in reserved_attrs else attr for attr in attributes)
            response = await client.get_item(
                TableName=table_name,
                Key=key,
                ProjectionExpression=projection_expression,
                ExpressionAttributeNames=expression_attribute_names
            )
        else:
            response = await client.get_item(
                TableName=table_name,
                Key=key
            )

        if 'Item' in response:
            item = response['Item']
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
            return simplified_item
        else:
            return None
        
        
async def delete_slide(presentation_id: str, slide_id: str) -> bool:
    """
    Delete a single slide from a presentation.

    Args:
        presentation_id (str): The ID of the presentation.
        slide_id (str): The ID of the slide to delete.

    Returns:
        bool: True if the slide was deleted successfully, False otherwise.
    """
    table_name = await get_table()
    async with get_session().create_client('dynamodb', region_name=AWS_REGION) as client:
        key = {
            'PK': {'S': f'PRESENTATION#{presentation_id}'},
            'SK': {'S': f'SLIDE#{slide_id}'}
        }

        try:
            await client.delete_item(
                TableName=table_name,
                Key=key
            )
            return True
        except Exception as e:
            print(f"Error deleting slide: {str(e)}")
            return False

async def delete_all_slides(presentation_id: str) -> bool:
    """
    Delete all slides for a presentation.

    Args:
        presentation_id (str): The ID of the presentation.

    Returns:
        bool: True if all slides were deleted successfully, False otherwise.
    """
    table_name = await get_table()
    async with get_session().create_client('dynamodb', region_name=AWS_REGION) as client:
        key_condition_expression = 'PK = :pk AND begins_with(SK, :sk)'
        expression_attribute_values = {
            ':pk': {'S': f'PRESENTATION#{presentation_id}'},
            ':sk': {'S': 'SLIDE#'}
        }

        response = await client.query(
            TableName=table_name,
            KeyConditionExpression=key_condition_expression,
            ExpressionAttributeValues=expression_attribute_values
        )

        slide_keys = [{'PK': item['PK'], 'SK': item['SK']} for item in response['Items']]

        try:
            for key in slide_keys:
                await client.delete_item(
                    TableName=table_name,
                    Key=key
                )
            return True
        except Exception as e:
            print(f"Error deleting slides: {str(e)}")
            return False

        
async def main():
    # Test data
    presentation_id = uuid7str()
    slide_data = [
        {
            'title': 'Slide 1',
            'content': 'This is the content of slide 1.',
            'is_enabled': True,
            'complex_data': {'key1': 'value1', 'key2': [1, 2, 3]}
        },
        {
            'title': 'Slide 2',
            'content': 'This is the content of slide 2.',
            'is_enabled': False,
            'complex_data': {'key3': 'value3', 'key4': {'nested_key': 'nested_value', 'nested_bool': True}}
        }
    ]

    # Create slides
    created_slides = []
    for slide in slide_data:
        slide_id = uuid7str()
        await update_slide(presentation_id, slide_id, **slide)
        created_slides.append({'id': slide_id, **slide})

    print("Created slides:")
    print(created_slides)

    # Get all slides
    slides = await get_slides(presentation_id)
    print("\nAll slides:")
    print(slides)

    # Get specific slide
    slide_id = created_slides[0]['id']
    slide = await get_slide(presentation_id, slide_id)
    print("\nSpecific slide:")
    print(slide)

    # Get slides with specific attributes
    attributes = ['title', 'order']
    slides_with_attributes = await get_slides(presentation_id, attributes)
    print("\nSlides with specific attributes:")
    print(slides_with_attributes)

    # Update a slide
    slide_id = created_slides[0]['id']
    updated_slide_data = {
        'title': 'Updated Slide 1',
        'content': 'This is the updated content of slide 1.',
        'complex_data': {'key1': 'updated_value1', 'key2': [4, 5, 6]}
    }
    updated_slide = await update_slide(presentation_id, slide_id, **updated_slide_data)
    print("\nUpdated slide:")
    print(updated_slide)

    # # Batch update slides
    # batch_update_data = [
    #     {
    #         'id': uuid7str(),
    #         'title': 'Batch Updated Slide 1',
    #         'is_enabled': False
    #     },
    #     {
    #         'id': uuid7str(),
    #         'title': 'Batch Updated Slide 2',
    #         'is_enabled': True,
    #         'complex': {
    #             'key1': 'value1',
    #             'key2': True
    #         }
    #     }
    # ]
    # success = await batch_update_slides(presentation_id, batch_update_data)
    # print("\nBatch update result:")
    # print(success)

    # Get all slides after batch update
    slides_after_batch_update = await get_slides(presentation_id)
    print("\nAll slides after batch update:")
    print(slides_after_batch_update)

if __name__ == '__main__':
    asyncio.run(main())