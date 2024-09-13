import json
interface = "ideate"
from dynamodb_service import update_items_with_user

async def save_progress(presentation_id, messages, interface_data, memory):
    attributes = {}
    if messages:
        attributes["messages"] = json.dumps(messages)
    if interface_data:
        attributes.update(interface_data)
    if memory:
        attributes["memory"] = json.dumps(memory)
        
    attributes["status"] = interface
    await update_items_with_user('presentation', [{**attributes, 'presentation_id': presentation_id}])
    return