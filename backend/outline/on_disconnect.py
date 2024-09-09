import json
import asyncio

interface = "outline"

from dynamodb import update_presentation


async def save_progress(presentation_id, messages, interface_data, memory):
    attributes = {}
    attributes["status"] = interface
    
    if messages:
        attributes["messages"] = json.dumps(messages)
    
    if memory:
        attributes["memory"] = json.dumps(memory)
        
    # print(f"Interface data: {interface_data}")
    if interface_data:
        if interface_data.get('outline') is not None:
            print(f"saving outline {interface_data.get('outline')}")
            
            outline = interface_data.get('outline')
            attributes['outline'] = json.dumps(outline)
        else:
            print("No topics to save")
    
    await update_presentation(presentation_id, **attributes)
        
    return