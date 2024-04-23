import json
import asyncio

interface = "outline"

from dynamodb import update_presentation


async def save_progress(presentationID, messages, interfaceData, memory):
    attributes = {}
    attributes["status"] = interface
    
    if messages:
        attributes["messages"] = json.dumps(messages)
    
    if memory:
        attributes["memory"] = json.dumps(memory)
        
    # print(f"Interface data: {interfaceData}")
    if interfaceData:
        if interfaceData.get('outline') is not None:
            print(f"saving outline {interfaceData.get('outline')}")
            
            outline = interfaceData.get('outline')
            attributes['outline'] = json.dumps(outline)
        else:
            print("No topics to save")
    
    await update_presentation(presentationID, **attributes)
        
    return