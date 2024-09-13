from dynamodb_service import get_all_items_for_presentation_with_user, delete_items_with_user
from s3 import delete_file
import asyncio
from copy import deepcopy
from session_log_config import get_child_logger
import os 
import logging 
# Create a logger for this file
logger = get_child_logger(os.path.abspath(__file__), level=logging.INFO)


def merge_lists(list1, list2):
    """
    Merges two lists of dictionaries based on the 'id' key and removes duplicates.

    Args:
        list1 (list): The first list of dictionaries.
        list2 (list): The second list of dictionaries.

    Returns:
        list: A new list containing all the dictionaries from both input lists,
              with duplicates removed based on the 'id' key.

    Assumes:
        - Each dictionary in the input lists has an 'id' or a 'source_id' key.
        - If two dictionaries have the same id, they are considered duplicates,
          and it is safe to assume that the rest of their key-value pairs are the same.
    """
    # rename 'id' to 'source_id' for clarity
    dicts_with_no_ids = []
    for d in list1 + list2:
        if d.get('source_id') is None:
            if d.get('id') is None:
                logger.error(f"Merging lists: Dictionary in list 1 has no 'id' or 'source_id' key: {d}")
                dicts_with_no_ids.append(d)
            else:
                d['source_id'] = d.pop('id')


    merged_dict = {d['source_id']: d for d in list1 + list2}
    merged_list = list(merged_dict.values()) + dicts_with_no_ids

    logger.info(f"Merging lists: List 1 length: {len(list1)}, List 2 length: {len(list2)}, Merged list length: {len(merged_list)}")
    return merged_list


async def interface_update(presentation_id, interface_data, data):
    # make a deepcopy of interface_data
    interface_data = deepcopy(interface_data)
    oldsources = interface_data.get('sources', [])
    if data['action'] == 'refresh' or data['action'] == 'refresh_upload':
        sources = await get_all_items_for_presentation_with_user('source', presentation_id)
        # Assert that every source coming out of here has a source_id
        for source in sources:
            assert source.get('source_id', None) is not None
        sources = merge_lists(oldsources, sources)
    elif data['action'] == 'delete':
        sources = await get_all_items_for_presentation_with_user('source', presentation_id)
        # Assert that every source coming out of here has a source_id
        for source in sources:
            assert source.get('source_id', None) is not None
        sources = merge_lists(oldsources, sources)
        source_to_delete = next((s for s in sources if s['source_id'] == data['id']), None)
        if source_to_delete.get('type', 'file') != 'web':
            await asyncio.gather(
                delete_file(presentation_id, source_to_delete.get('s3_filepath', '')), # s3
                delete_file(presentation_id, source_to_delete.get('whole_document_path', '')), # s3
                delete_items_with_user('source', [{'presentation_id': presentation_id, 'source_id': source_to_delete['source_id']}]) # dynamodb
            )
            # sources = await get_sources(presentation_id)
            sources = await get_all_items_for_presentation_with_user('source', presentation_id)
        else:
            await delete_items_with_user('source', [{'presentation_id': presentation_id, 'source_id': source_to_delete['source_id']}]) # dynamodb
            sources = await get_all_items_for_presentation_with_user('source', presentation_id)
            if not sources:
                pass
    else:
        raise ValueError("Action not found")
    
    if not sources:
        pass

    return {'sources': sources or []}