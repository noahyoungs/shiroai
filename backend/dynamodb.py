import os
import time
from dotenv import load_dotenv
from aiobotocore.session import get_session
import json
from typing import List, Dict, Any, Union
import asyncio
from uuid_extensions import uuid7str
from slides.slide_models import *

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


async def update_slides(presentation_id: str, slides: Union[Slide, Dict, List[Union[Slide, Dict]]]) -> bool:
    """
    Update one or multiple slides in a presentation.

    Args:
        presentation_id (str): The ID of the presentation.
        slides (Union[Slide, Dict, List[Union[Slide, Dict]]]): A single Slide model, a partial slide dictionary, or a list of these to update.

    Returns:
        bool: True if the update was successful, False otherwise.
    """
    table_name = await get_table()
    async with get_session().create_client('dynamodb', region_name=AWS_REGION) as client:
        current_timestamp = int(time.time())
        update_requests = []

        if isinstance(slides, (Slide, dict)):
            slides = [slides]

        for slide in slides:
            if isinstance(slide, Slide):
                slide_dict = slide.dict(exclude_unset=True)
            elif isinstance(slide, dict):
                slide_dict = slide

            slide_id = slide_dict.pop('id', None)
            if not slide_id:
                continue  # Skip if no id is provided

            update_expression = 'SET '
            expression_attribute_values = {}
            expression_attribute_names = {}

            for key, value in slide_dict.items():
                if value is None or value == '':  # Skip null or empty values
                    continue

                if isinstance(value, (list, dict)):
                    value = json.dumps(value)
                    # print(f"Converted {key} to JSON string: {value}")
                elif isinstance(value, str):
                    try:
                        # Check if the string is already a JSON-formatted string
                        json.loads(value)
                        # print(f"{key} is already a JSON string: {value}")
                    except json.JSONDecodeError:
                        # If it's not JSON, proceed with conversion
                        pass

                attr_name_key = f'#{key}'
                update_expression += f'{attr_name_key} = :{key}, '
                expression_attribute_names[attr_name_key] = key

                value_type = type(value)
                if value_type == str:
                    expression_attribute_values[f':{key}'] = {'S': value}
                elif value_type == int:
                    expression_attribute_values[f':{key}'] = {'N': str(value)}
                elif value_type == bool:
                    expression_attribute_values[f':{key}'] = {'BOOL': value}
                # print(f"Prepared value for {key}: {expression_attribute_values[f':{key}']}")

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
            # print(f"Update request prepared for slide {slide_id}: {update_request}")

        if len(update_requests) == 1:
            response = await client.update_item(**update_requests[0]["Update"])
            # print(f"Update response for single item: {response}")
            return response['ResponseMetadata']['HTTPStatusCode'] == 200
        else:
            response = await client.transact_write_items(TransactItems=update_requests)
            # print(f"Transact write response: {response}")
            return response['ResponseMetadata']['HTTPStatusCode'] == 200


async def get_all_slides(presentation_id, attributes=None) -> List[Slide]:
    """
    Retrieve all slides in a presentation.

    Args:
        presentation_id (str): The ID of the presentation.
        attributes (Optional[List[str]]): A list of attributes to retrieve for each slide.

    Returns:
        List[Slide]: A list of Slide models.
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
            projection_expression = ', '.join(
                f'#{attr}' if attr in reserved_attrs else attr for attr in attributes)
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

            slide_type = simplified_item.get('slide_type')
            if slide_type == 'short_bullets_slide':
                slides.append(ShortBulletsSlide(**simplified_item))
            elif slide_type == 'markdown_slide':
                slides.append(MarkdownSlide(**simplified_item))
            elif slide_type == 'simple_mermaid_slide':
                slides.append(SimpleMermaidSlide(**simplified_item))
            elif slide_type == 'section_header_slide':
                slides.append(SectionHeaderSlide(**simplified_item))
            elif slide_type == 'presentation_title_slide':
                slides.append(PresentationTitleSlide(**simplified_item))
            else:
                raise ValueError(f"Unknown slide type: {slide_type}")

        return slides


async def get_slides(presentation_id, slide_ids: Union[str, List[str]], attributes=None) -> Union[Slide, List[Slide]]:
    """
    Retrieve one or multiple slides from a presentation.

    Args:
        presentation_id (str): The ID of the presentation.
        slide_ids (Union[str, List[str]]): A single slide ID or a list of slide IDs to retrieve.
        attributes (Optional[List[str]]): A list of attributes to retrieve for the slide(s).

    Returns:
        Union[Slide, List[Slide]]: A Slide model or a list of Slide models.
    """
    table_name = await get_table()
    async with get_session().create_client('dynamodb', region_name=AWS_REGION) as client:
        if isinstance(slide_ids, str):
            key = {
                'PK': {'S': f'PRESENTATION#{presentation_id}'},
                'SK': {'S': f'SLIDE#{slide_ids}'}
            }

            if attributes:
                expression_attribute_names = {}
                for attr in attributes:
                    if attr in reserved_attrs:
                        expression_attribute_names[f'#{attr}'] = attr
                projection_expression = ', '.join(
                    f'#{attr}' if attr in reserved_attrs else attr for attr in attributes)
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
                        simplified_item['presentation_id'] = v['S'].split('#')[
                            1]
                    elif 'S' in v:
                        try:
                            simplified_item[k] = json.loads(v['S'])
                        except json.JSONDecodeError:
                            simplified_item[k] = v['S']
                    elif 'N' in v:
                        simplified_item[k] = int(v['N'])
                    elif 'BOOL' in v:
                        simplified_item[k] = v['BOOL']

                slide_type = simplified_item.get('slide_type')
                if slide_type == 'short_bullets_slide':
                    return ShortBulletsSlide(**simplified_item)
                elif slide_type == 'markdown_slide':
                    return MarkdownSlide(**simplified_item)
                elif slide_type == 'simple_mermaid_slide':
                    return SimpleMermaidSlide(**simplified_item)
                elif slide_type == 'section_header_slide':
                    return SectionHeaderSlide(**simplified_item)
                elif slide_type == 'presentation_title_slide':
                    return PresentationTitleSlide(**simplified_item)
                else:
                    raise ValueError(f"Unknown slide type: {slide_type}")

        else:
            keys = [{'PK': {'S': f'PRESENTATION#{presentation_id}'}, 'SK': {
                'S': f'SLIDE#{slide_id}'}} for slide_id in slide_ids]

            request_items = {
                table_name: {
                    'Keys': keys
                }
            }

            response = await client.batch_get_item(RequestItems=request_items)

            slides = []
            for item in response.get('Responses', {}).get(table_name, []):
                simplified_item = {}
                for k, v in item.items():
                    if k == 'SK':
                        simplified_item['id'] = v['S'].split('#')[1]
                    elif k == 'PK':
                        simplified_item['presentation_id'] = v['S'].split('#')[
                            1]
                    elif 'S' in v:
                        try:
                            simplified_item[k] = json.loads(v['S'])
                        except json.JSONDecodeError:
                            simplified_item[k] = v['S']
                    elif 'N' in v:
                        simplified_item[k] = int(v['N'])
                    elif 'BOOL' in v:
                        simplified_item[k] = v['BOOL']

                slide_type = simplified_item.get('slide_type')
                if slide_type == 'short_bullets_slide':
                    slides.append(ShortBulletsSlide(**simplified_item))
                elif slide_type == 'markdown_slide':
                    slides.append(MarkdownSlide(**simplified_item))
                elif slide_type == 'simple_mermaid_slide':
                    slides.append(SimpleMermaidSlide(**simplified_item))
                elif slide_type == 'section_header_slide':
                    slides.append(SectionHeaderSlide(**simplified_item))
                elif slide_type == 'presentation_title_slide':
                    slides.append(PresentationTitleSlide(**simplified_item))
                else:
                    raise ValueError(f"Unknown slide type: {slide_type}")

            return slides


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

        slide_keys = [{'PK': item['PK'], 'SK': item['SK']}
                      for item in response['Items']]

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


async def update_topics(presentation_id: str, topics: Union[Topic, Dict, List[Union[Topic, Dict]]]) -> bool:
    """
    Update one or multiple topics in a presentation.

    Args:
        presentation_id (str): The ID of the presentation.
        topics (Union[Topic, Dict, List[Union[Topic, Dict]]]): A single Topic model, a partial topic dictionary, or a list of these to update.

    Returns:
        bool: True if the update was successful, False otherwise.
    """
    table_name = await get_table()
    async with get_session().create_client('dynamodb', region_name=AWS_REGION) as client:
        current_timestamp = int(time.time())
        update_requests = []

        if isinstance(topics, (Topic, dict)):
            topics = [topics]

        for topic in topics:
            if isinstance(topic, Topic):
                topic_dict = topic.dict(exclude_unset=True)
            elif isinstance(topic, dict):
                topic_dict = topic

            topic_id = topic_dict.pop('id', None)
            if not topic_id:
                continue  # Skip if no id is provided

            update_expression = 'SET '
            expression_attribute_values = {}
            expression_attribute_names = {}

            for key, value in topic_dict.items():
                if value is None or value == '':  # Skip null or empty values
                    continue

                if isinstance(value, (list, dict)):
                    value = json.dumps(value)

                attr_name_key = f'#{key}'
                update_expression += f'{attr_name_key} = :{key}, '
                expression_attribute_names[attr_name_key] = key

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
            expression_attribute_values[':time_updated'] = {
                'N': str(current_timestamp)}

            update_request = {
                "Update": {
                    "TableName": table_name,
                    "Key": {
                        'PK': {'S': f'PRESENTATION#{presentation_id}'},
                        'SK': {'S': f'TOPIC#{topic_id}'}
                    },
                    "UpdateExpression": update_expression,
                    "ExpressionAttributeValues": expression_attribute_values,
                    "ExpressionAttributeNames": expression_attribute_names
                }
            }

            update_requests.append(update_request)

        if len(update_requests) == 1:
            response = await client.update_item(**update_requests[0]["Update"])
            return response['ResponseMetadata']['HTTPStatusCode'] == 200
        else:
            response = await client.transact_write_items(TransactItems=update_requests)
            return response['ResponseMetadata']['HTTPStatusCode'] == 200


async def get_all_topics(presentation_id, attributes=None) -> List[Topic]:
    """
    Retrieve all topics in a presentation.

    Args:
        presentation_id (str): The ID of the presentation.
        attributes (Optional[List[str]]): A list of attributes to retrieve for each topic.

    Returns:
        List[Topic]: A list of Topic models.
    """
    table_name = await get_table()
    async with get_session().create_client('dynamodb', region_name=AWS_REGION) as client:
        key_condition_expression = 'PK = :pk AND begins_with(SK, :sk)'
        expression_attribute_values = {
            ':pk': {'S': f'PRESENTATION#{presentation_id}'},
            ':sk': {'S': 'TOPIC#'}
        }

        if attributes:
            expression_attribute_names = {}
            for attr in attributes:
                if attr in reserved_attrs:
                    expression_attribute_names[f'#{attr}'] = attr
            projection_expression = ', '.join(
                f'#{attr}' if attr in reserved_attrs else attr for attr in attributes)
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

        topics = []
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

            topics.append(Topic(**simplified_item))

        return topics


async def get_topics(presentation_id, topic_ids: Union[str, List[str]], attributes=None) -> Union[Topic, List[Topic]]:
    """
    Retrieve one or multiple topics from a presentation.

    Args:
        presentation_id (str): The ID of the presentation.
        topic_ids (Union[str, List[str]]): A single topic ID or a list of topic IDs to retrieve.
        attributes (Optional[List[str]]): A list of attributes to retrieve for the topic(s).

    Returns:
        Union[Topic, List[Topic]]: A Topic model or a list of Topic models.
    """
    table_name = await get_table()
    async with get_session().create_client('dynamodb', region_name=AWS_REGION) as client:
        if isinstance(topic_ids, str):
            key = {
                'PK': {'S': f'PRESENTATION#{presentation_id}'},
                'SK': {'S': f'TOPIC#{topic_ids}'}
            }

            if attributes:
                expression_attribute_names = {}
                for attr in attributes:
                    if attr in reserved_attrs:
                        expression_attribute_names[f'#{attr}'] = attr
                projection_expression = ', '.join(
                    f'#{attr}' if attr in reserved_attrs else attr for attr in attributes)

                get_item_params = {
                    'TableName': table_name,
                    'Key': key,
                    'ProjectionExpression': projection_expression
                }

                if expression_attribute_names:
                    get_item_params['ExpressionAttributeNames'] = expression_attribute_names

                response = await client.get_item(**get_item_params)
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
                        simplified_item['presentation_id'] = v['S'].split('#')[
                            1]
                    elif 'S' in v:
                        try:
                            simplified_item[k] = json.loads(v['S'])
                        except json.JSONDecodeError:
                            simplified_item[k] = v['S']
                    elif 'N' in v:
                        simplified_item[k] = int(v['N'])
                    elif 'BOOL' in v:
                        simplified_item[k] = v['BOOL']

                return Topic(**simplified_item)

        else:
            keys = [{'PK': {'S': f'PRESENTATION#{presentation_id}'}, 'SK': {
                'S': f'TOPIC#{topic_id}'}} for topic_id in topic_ids]

            request_items = {
                table_name: {
                    'Keys': keys
                }
            }

            response = await client.batch_get_item(RequestItems=request_items)

            topics = []
            for item in response.get('Responses', {}).get(table_name, []):
                simplified_item = {}
                for k, v in item.items():
                    if k == 'SK':
                        simplified_item['id'] = v['S'].split('#')[1]
                    elif k == 'PK':
                        simplified_item['presentation_id'] = v['S'].split('#')[
                            1]
                    elif 'S' in v:
                        try:
                            simplified_item[k] = json.loads(v['S'])
                        except json.JSONDecodeError:
                            simplified_item[k] = v['S']
                    elif 'N' in v:
                        simplified_item[k] = int(v['N'])
                    elif 'BOOL' in v:
                        simplified_item[k] = v['BOOL']

                topics.append(Topic(**simplified_item))

            return topics


async def delete_all_topics(presentation_id: str) -> bool:
    """
    Delete all topics for a presentation.

    Args:
        presentation_id (str): The ID of the presentation.

    Returns:
        bool: True if all topics were deleted successfully, False otherwise.
    """
    table_name = await get_table()
    async with get_session().create_client('dynamodb', region_name=AWS_REGION) as client:
        key_condition_expression = 'PK = :pk AND begins_with(SK, :sk)'
        expression_attribute_values = {
            ':pk': {'S': f'PRESENTATION#{presentation_id}'},
            ':sk': {'S': 'TOPIC#'}
        }

        response = await client.query(
            TableName=table_name,
            KeyConditionExpression=key_condition_expression,
            ExpressionAttributeValues=expression_attribute_values
        )

        topic_keys = [{'PK': item['PK'], 'SK': item['SK']}
                      for item in response['Items']]

        try:
            for key in topic_keys:
                await client.delete_item(
                    TableName=table_name,
                    Key=key
                )
            return True
        except Exception as e:
            print(f"Error deleting topics: {str(e)}")
            return False


async def main():
    # Replace with your own data for testing
    presentation_id = uuid7str()

    slides = [
        ShortBulletsSlide(
            id=uuid7str(),
            slide_type='short_bullets_slide',
            slide_title='Slide 1',
            topic_id='Topic 1',
            hidden=False,
            slide_content=[
                ShortBulletContent(
                    content='Bullet point 1',
                    source_excerpt_id=uuid7str(),
                    excerpt=Excerpt(
                        source_id='Source 1',
                        excerpt_id=uuid7str(),
                        text='Excerpt text 1',
                    ),
                    icon=IconData(
                        name='icon-name',
                        source='icon-source',
                        detailed_name='icon-detailed-name'
                    ),
                    id=uuid7str(),
                )
            ],
            sequential=True,
            layout='list',
            generation_messages=[
                LLMMessage(role='user', content='Initial content for slide 1')
            ],
        ),
        MarkdownSlide(
            id=uuid7str(),
            slide_type='markdown_slide',
            slide_title='Slide 2',
            topic_id='Topic 2',
            hidden=False,
            slide_content={
                'content': 'Markdown content',
                'footnotes': {
                    'footnote1': Excerpt(
                        source_id='Source 2',
                        excerpt_id=uuid7str(),
                        text='Footnote text'
                    )
                }
            },
            generation_messages=[
                LLMMessage(role='assistant',
                           content='Initial content for slide 2')
            ],
        ),
        SimpleMermaidSlide(
            id=uuid7str(),
            slide_type='simple_mermaid_slide',
            slide_title='Slide 3',
            topic_id='Topic 3',
            hidden=False,
            slide_content={
                'mermaid_code': 'graph TD; A-->B;',
                'excerpts': [
                    Excerpt(
                        source_id='Source 3',
                        excerpt_id=uuid7str(),
                        text='Mermaid excerpt'
                    )
                ],
                'light_svg': '<svg>Light</svg>',
                'dark_svg': '<svg>Dark</svg>'
            },
            generation_messages=[
                LLMMessage(role='system',
                           content='Initial content for slide 3')
            ],
        ),
        SectionHeaderSlide(
            id=uuid7str(),
            slide_type='section_header_slide',
            slide_title='Slide 4',
            topic_id='Topic 4',
            hidden=False,
            image=Image(
                s3_key='image-key',
                url='https://example.com/image.jpg',
                alt='An example image',
                type='cover',
                shape='rectangle'
            ),
            image_position='left',
            generation_messages=[
                LLMMessage(role='user', content='Initial content for slide 4')
            ],
        ),
        PresentationTitleSlide(
            id=uuid7str(),
            slide_type='presentation_title_slide',
            slide_title='Slide 5',
            topic_id='Topic 5',
            hidden=False,
            image=Image(
                s3_key='title-image-key',
                url='https://example.com/title-image.jpg',
                alt='Title slide image',
                type='cover',
                shape='rectangle'
            ),
            generation_messages=[
                LLMMessage(role='assistant',
                           content='Initial content for slide 5')
            ],
        ),
    ]

    print("Updating multiple slides...")
    update_result = await update_slides(presentation_id, slides)
    print("Update result:", update_result)

    print("Retrieving all slides...")
    all_slides = await get_all_slides(presentation_id)
    print("All slides:", all_slides)

    if all_slides:
        print("Updating a single slide...")
        single_slide_update = all_slides[0]
        single_slide_update.slide_title = "Updated Slide Title"
        single_update_result = await update_slides(presentation_id, single_slide_update)
        print("Single update result:", single_update_result)

        print("Retrieving single slide...")
        single_slide = await get_slides(presentation_id, all_slides[0].id)
        print("Single slide:", single_slide)

        print("Retrieving multiple slides...")
        slide_ids = [slide.id for slide in all_slides]
        multiple_slides = await get_slides(presentation_id, slide_ids)
        print("Multiple slides:", multiple_slides)


if __name__ == '__main__':
    asyncio.run(main())
