import json
import asyncio

interface = "slides"

from dynamodb import update_presentation


# interfaceData is not used in slides
async def save_progress(presentationID, messages, interface_data, memory):
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
    
    await update_presentation(presentationID, **attributes)
    
    # print(f"Saving progress, presentation attributes: {attributes}
    
    return