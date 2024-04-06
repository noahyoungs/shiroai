import os
import time
from dotenv import load_dotenv
from aiobotocore.session import get_session
import json

load_dotenv()

AWS_REGION = os.getenv('AWS_REGION')

reserved_attrs = ['status', 'type', 'order', 'content', 'user', 'name', 'url']

async def get_table():
    session = get_session()
    async with session.create_client('dynamodb', region_name=AWS_REGION) as client:
        response = await client.describe_table(TableName='AiPresenter2')
        return response['Table']['TableName']

async def get_presentation(presentation_id, attributes=None):
    table_name = await get_table()
    async with get_session().create_client('dynamodb', region_name=AWS_REGION) as client:
        key = {
            'PK': {'S': f'PRESENTATION#{presentation_id}'},
            'SK': {'S': f'PRESENTATION#{presentation_id}'}
        }
        if attributes:
            projection_expression = ', '.join(f'#{attr}' if attr in reserved_attrs else attr for attr in attributes)
            expression_attribute_names = {f'#{attr}': attr for attr in attributes if attr in reserved_attrs}
            if expression_attribute_names:
                response = await client.get_item(TableName=table_name, Key=key, ProjectionExpression=projection_expression, ExpressionAttributeNames=expression_attribute_names)
            else:
                response = await client.get_item(TableName=table_name, Key=key, ProjectionExpression=projection_expression)
        else:
            response = await client.get_item(TableName=table_name, Key=key)
        if 'Item' in response:
            item = response['Item']
            simplified_item = {'id': presentation_id}  # Add the original presentation ID as "id" in the returned dict
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
        response = await client.update_item(**update_params)
        return response['Attributes']
    
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
                expression_attribute_values[f':{key}'] = {'S': json.dumps(value)}
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
        expression_attribute_values[':time_updated'] = {'N': str(current_timestamp)}

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
        
        
async def batch_update_sources(presentation_id, sources):
    # print("Updating sources, presentation_id: ", presentation_id)
    # print("Sources: ", sources)

    table_name = await get_table()
    async with get_session().create_client('dynamodb', region_name=AWS_REGION) as client:
        update_requests = []
        current_timestamp = int(time.time())

        for source in sources:
            source_id = source.pop('id')
            update_expression = 'SET '
            expression_attribute_values = {}
            expression_attribute_names = {}

            for key, value in source.items():
                if key == 'web_source':
                    update_expression += '#web_source = :web_source, '
                    expression_attribute_names['#web_source'] = 'web_source'
                    expression_attribute_values[':web_source'] = {'S': json.dumps(value)}
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
                        expression_attribute_values[f':{key}'] = {'N': str(value)}
                    elif isinstance(value, bool):
                        expression_attribute_values[f':{key}'] = {'BOOL': value}

            # Set the time_updated attribute to the current Unix timestamp
            update_expression += '#time_updated = :time_updated'
            expression_attribute_names['#time_updated'] = 'time_updated'
            expression_attribute_values[':time_updated'] = {'N': str(current_timestamp)}

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

async def main():
    # # Example usage of updatePresentation
    # await updatePresentation("123", status="In Progress", topic="Machine Learning", presenter="Alex Doe", viewss=100)

    # # Example usage of getPresentation
    # presentation = await getPresentation("123", ["status", "topic", "presenter", "viewss"])
    # print(presentation)
    # await update_presentation("64332c6a-1645-4c4f-b06a-502b6fbc2004", messages="""[{"role": "assistant", "content": "Hi! How can I help you?"}]""")
    # presentation = await get_presentation("64332c6a-1645-4c4f-b06a-502b6fbc2004", ["time_updated"])
    # print(presentation)
    
    presentation_id = "83cb6cd4-2ba6-4bf2-91e6-e72a4b4283bd"
    sources_to_update = [
        {
            'id': '17c3f42a-5f51-4bf8-8d04-fe12d538b5ca',
            'presentation_id': '83cb6cd4-2ba6-4bf2-91e6-e72a4b4283bd',
            'name': 'WorldPopulation2023.csv',
            's3_filepath': 'WorldPopulation2023.csv',
            'type': 'csv'
        }
    ]

    response = await batch_update_sources(presentation_id, sources_to_update)
    print(response)


# if __name__ == "__main__":
#     import asyncio
#     asyncio.run(main())
    