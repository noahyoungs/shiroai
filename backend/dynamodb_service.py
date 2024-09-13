# backend/dynamodb_service.py
from typing import Union, Dict, List, Optional, Literal
from pydantic import BaseModel
from session_log_config import get_child_logger, current_user_id
from dynamodb_interface import get_items, update_items, delete_items, get_all_items_for_presentation, delete_all_items_for_presentation
import os
import logging

logger = get_child_logger(os.path.abspath(__file__), level=logging.WARNING)

item_types_literal = Literal['user', 'presentation', 'slide', 'topic', 'source']

async def get_items_with_user(
    item_type: item_types_literal,
    identifiers: Union[Dict[str, str], List[Dict[str, str]]],
    attributes: Optional[List[str]] = None,
    return_type: Optional[Literal['dict', 'model']] = 'dict',
    consistent_read: bool = False
) -> Union[Dict, BaseModel, None, List[Union[Dict, None]], List[Union[BaseModel, None]]]:
    """
    Fetch one or multiple items of a specified type from the DynamoDB table, using the user ID from the current context.

    Args:
        item_type (item_types_literal): The type of item to fetch ('user', 'presentation', 'slide', 'topic', or 'source').
        identifiers (Union[Dict[str, str], List[Dict[str, str]]]): A dictionary or list of dictionaries containing identifiers for the item(s) to fetch.
        attributes (Optional[List[str]], optional): A list of specific attributes to retrieve. If None, all attributes are retrieved. Defaults to None.
        return_type (Optional[Literal['dict', 'model']], optional): The desired return type, either 'dict' or 'model'. Defaults to 'dict'.
        consistent_read (bool, optional): Whether to use strongly consistent reads. Defaults to False.

    Returns:
        Union[Dict, BaseModel, None, List[Union[Dict, None]], List[Union[BaseModel, None]]]: If one item is fetched, a dictionary or model instance is returned. If multiple items are fetched, a list of dictionaries or model instances is returned. If no items match a provided identifier, None is returned in its place.

    Raises:
        ValueError: If the user ID is not available in the current context.
    """
    user_id = current_user_id.get()
    if not user_id:
        logger.error("User ID not available in the current context")
        raise ValueError("User ID not available in the current context")

    logger.info(f"Fetching {item_type} items with user ID: {user_id}")
    logger.debug(f"Identifiers: {identifiers}, Attributes: {attributes}, Return type: {return_type}, Consistent read: {consistent_read}")

    if isinstance(identifiers, dict):
        identifiers['user_id'] = user_id
    elif isinstance(identifiers, list):
        for identifier in identifiers:
            identifier['user_id'] = user_id

    result = await get_items(item_type, identifiers, attributes, return_type, consistent_read=consistent_read)
    logger.info(f"Fetched {len(result) if isinstance(result, list) else 1} {item_type} item(s)")
    return result

async def update_items_with_user(
    item_type: item_types_literal,
    items: Union[List[Dict], List[BaseModel]]
) -> None:
    """
    Update one or multiple items of a specified type in the DynamoDB table, using the user ID from the current context.

    Args:
        item_type (item_types_literal): The type of item to update ('user', 'presentation', 'slide', 'topic', or 'source').
        items (Union[List[Dict], List[BaseModel]]): A list of dictionaries or BaseModel instances representing the items to update.

    Raises:
        ValueError: If the user ID is not available in the current context or if a provided user ID doesn't match the context user ID.
    """
    context_user_id = current_user_id.get()
    if not context_user_id:
        logger.error("User ID not available in the current context")
        raise ValueError("User ID not available in the current context")

    logger.info(f"Updating {len(items)} {item_type} item(s) with user ID: {context_user_id}")
    logger.debug(f"Items to update: {items}")

    for item in items:
        if isinstance(item, dict):
            if 'user_id' in item and item['user_id'] is not None and item['user_id'] != context_user_id:
                logger.error(f"Provided user ID {item['user_id']} doesn't match the context user ID {context_user_id}")
                raise ValueError(f"Provided user ID {item['user_id']} doesn't match the context user ID {context_user_id}")
            item['user_id'] = context_user_id
        elif isinstance(item, BaseModel):
            if hasattr(item, 'user_id') and item.user_id is not None and item.user_id != context_user_id:
                logger.error(f"Provided user ID {item.user_id} doesn't match the context user ID {context_user_id}")
                raise ValueError(f"Provided user ID {item.user_id} doesn't match the context user ID {context_user_id}")
            setattr(item, 'user_id', context_user_id)

    await update_items(item_type, items)
    logger.info(f"Updated {len(items)} {item_type} item(s)")

async def delete_items_with_user(
    item_type: Literal['user', 'presentation', 'slide', 'topic', 'source'],
    identifiers: List[Dict[str, str]]
) -> None:
    """
    Delete one or multiple items of a specified type from the DynamoDB table, using the user ID from the current context.

    Args:
        item_type (Literal['user', 'presentation', 'slide', 'topic', 'source']): The type of item to delete.
        identifiers (List[Dict[str, str]]): A list of dictionaries containing identifiers for the items to delete.

    Raises:
        ValueError: If the user ID is not available in the current context.
    """
    user_id = current_user_id.get()
    if not user_id:
        logger.error("User ID not available in the current context")
        raise ValueError("User ID not available in the current context")

    logger.info(f"Deleting {len(identifiers)} {item_type} item(s) with user ID: {user_id}")
    logger.debug(f"Identifiers for deletion: {identifiers}")

    for identifier in identifiers:
        identifier['user_id'] = user_id

    await delete_items(item_type, identifiers)
    logger.info(f"Deleted {len(identifiers)} {item_type} item(s)")

async def get_all_items_for_presentation_with_user(
    item_type: Literal['slide', 'topic', 'source'],
    presentation_id: str,
    attributes: Optional[List[str]] = None,
    return_type: Optional[Literal['model', 'dict']] = 'dict',
    consistent_read: bool = False
) -> Union[List[Dict], List[BaseModel]]:
    """
    Fetch all items of a specified type for a given presentation, using the user ID from the current context.

    Args:
        item_type (Literal['slide', 'topic', 'source']): The type of items to fetch.
        presentation_id (str): The ID of the presentation.
        attributes (Optional[List[str]], optional): A list of specific attributes to retrieve. If None, all attributes are retrieved. Defaults to None.
        return_type (Optional[Literal['model', 'dict']], optional): The desired return type, either 'dict' or 'model'. Defaults to 'dict'.
        consistent_read (bool, optional): Whether to use strongly consistent reads. Defaults to False.

    Returns:
        Union[List[Dict], List[BaseModel]]: A list of fetched items in the specified return type.

    Raises:
        ValueError: If the user ID is not available in the current context.
    """
    user_id = current_user_id.get()
    if not user_id:
        logger.error("User ID not available in the current context")
        raise ValueError("User ID not available in the current context")

    logger.info(f"Fetching all {item_type} items for presentation {presentation_id} with user ID: {user_id}")
    logger.debug(f"Attributes: {attributes}, Return type: {return_type}, Consistent read: {consistent_read}")

    result = await get_all_items_for_presentation(item_type, user_id, presentation_id, attributes, return_type, consistent_read=consistent_read)
    logger.info(f"Fetched {len(result)} {item_type} item(s) for presentation {presentation_id}")
    return result

async def delete_all_items_for_presentation_with_user(
    item_type: Literal['slide', 'topic', 'source'],
    presentation_id: str,
) -> None:
    """
    Delete all items of a specified type for a given presentation, using the user ID from the current context.

    Args:
        item_type (Literal['slide', 'topic', 'source']): The type of items to delete.
        presentation_id (str): The ID of the presentation.

    Raises:
        ValueError: If the user ID is not available in the current context.
    """
    user_id = current_user_id.get()
    if not user_id:
        logger.error("User ID not available in the current context")
        raise ValueError("User ID not available in the current context")

    logger.info(f"Deleting all {item_type} items for presentation {presentation_id} with user ID: {user_id}")
    
    await delete_all_items_for_presentation(item_type, user_id, presentation_id)
    logger.info(f"Deleted all {item_type} items for presentation {presentation_id}")