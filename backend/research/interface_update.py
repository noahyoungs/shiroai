from dynamodb import get_sources, delete_source
from s3 import delete_file
import asyncio
from copy import deepcopy

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
        - Each dictionary in the input lists has an 'id' key.
        - If two dictionaries have the same 'id', they are considered duplicates,
          and it is safe to assume that the rest of their key-value pairs are the same.
    """
    merged_dict = {d['id']: d for d in list1 + list2}
    merged_list = list(merged_dict.values())
    return merged_list


async def interface_update(presentationID, interfaceData, data):
    # make a deepcopy of interfaceData
    interfaceData = deepcopy(interfaceData)
    # print(f"Updating interface for presentation {presentationID} with interface data: {interfaceData} and data: {data}")
    oldsources = interfaceData.get('sources', [])
    if data['action'] == 'refresh' or data['action'] == 'refresh_upload':
        sources = await get_sources(presentationID)
        sources = merge_lists(oldsources, sources)
    elif data['action'] == 'delete':
        sources = await get_sources(presentationID)
        sources = merge_lists(oldsources, sources)
        source_to_delete = next((s for s in sources if s['id'] == data['id']), None)
        if source_to_delete.get('type', 'file') != 'web':
            await asyncio.gather(
                delete_file(presentationID, source_to_delete.get('s3_filepath', '')),
                delete_file(presentationID, source_to_delete.get('whole_document_path', '')),
                delete_source(presentationID, source_to_delete['id'])
            )
            sources = await get_sources(presentationID)
            # print("EMPTY SOURCES INTERFACE UPDATE AFTER DELETE FILE")
        else:
            await delete_source(presentationID, source_to_delete['id'])
            sources = await get_sources(presentationID)
            if not sources:
                pass
                # print("EMPTY SOURCES INTERFACE UPDATE AFTER DELETE WEB")
    else:
        raise ValueError("Action not found")
    
    if not sources:
        pass
        # print(f"EMPTY SOURCES INTERFACE UPDATE ACTION: {data['action']}")

    return {'sources': sources or []}