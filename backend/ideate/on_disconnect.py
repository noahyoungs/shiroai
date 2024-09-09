import json
interface = "ideate"
from dynamodb import update_presentation

async def save_progress(presentation_id, messages, interface_data, memory):
    attributes = {}
    if messages:
        attributes["messages"] = json.dumps(messages)
    if interface_data:
        attributes.update(interface_data)
    if memory:
        attributes["memory"] = json.dumps(memory)
        
    attributes["status"] = interface
    await update_presentation(presentation_id, **attributes)
    return