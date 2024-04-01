import json
interface = "ideate"
from dynamodb import update_presentation

async def save_progress(presentationID, messages, interfaceData, memory):
    attributes = {}
    if messages:
        attributes["messages"] = json.dumps(messages)
    if interfaceData:
        attributes.update(interfaceData)
    if memory:
        attributes["memory"] = json.dumps(memory)
        
    attributes["status"] = interface
    await update_presentation(presentationID, **attributes)
    return