import json
import asyncio

interface = "slides"

from dynamodb_service import update_items_with_user


# interface_data is not used in slides
async def save_progress(presentation_id, messages, interface_data, memory):
    attributes = {}
    attributes["status"] = interface
    
    if messages:
        attributes["messages"] = json.dumps(messages)
    
    if memory:
        # omit "slide_list" and "creating_slides_this_session" from memory
        temp_memory = memory.copy()
        temp_memory.pop("slide_list", None)
        temp_memory.pop("creating_slides_this_session", None)
        
        attributes["memory"] = json.dumps(temp_memory)
        
    if interface_data.get("current_slide_id"):
        attributes["current_slide_id"] = interface_data["current_slide_id"]
    
    # await update_presentation(presentation_id, **attributes)
    await update_items_with_user('presentation', [{**attributes, 'presentation_id': presentation_id}])
    
    # print(f"Saving progress, presentation attributes: {attributes}
    
    return