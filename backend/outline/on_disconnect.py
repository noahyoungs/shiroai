import json
import asyncio

interface = "outline"

from dynamodb_service import update_items_with_user

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
    
    await update_items_with_user('presentation', [{**attributes, 'presentation_id': presentation_id}])
        
    return