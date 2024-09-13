# /ideate/on_connect.py
import global_prompts_config
# from dynamodb_interface import get_items
from dynamodb_service import get_items_with_user
import json
from global_prompts_config import interface_keys_for_interface

interface = "ideate"

async def initialize(user_id, presentation_id):
    # get interface keys
    interface_keys = global_prompts_config.interface_keys_for_interface[interface]
    
    memory = {}
    
    presentation = await get_items_with_user('presentation', {'presentation_id': presentation_id}, ['messages', 'status', 'memory'] + interface_keys, consistent_read=True)

    # If the presentation does not exist, return an error message
    if not presentation:
        raise RuntimeError('The presentation you\'re trying to edit was not found, please try creating a new presentation.')

    # Check if 'messages' exists in the presentation and is not None
    if 'messages' in presentation and presentation['messages'] is not None:
        # If so, parse it from JSON
        print(f"Loading existing messages for presentation {presentation_id}")
        messages = json.loads(presentation['messages'])
    else:
        # Otherwise, use the default list directly
        print(f"No existing messages for presentation {presentation_id}")
        messages = global_prompts_config.initial_messages.copy()
    
    if 'memory' in presentation and presentation['memory'] is not None:
        memory = json.loads(presentation['memory'])
        
    # Messages that enter right after interface change
    if presentation['status'] != interface:
        messages += global_prompts_config.get_interface_changed_messages(interface)

    interface_data = {}
    for key in interface_keys:
        interface_data[key] = presentation.get(key, "")
    
    # print(f"Interface keys: {interface_keys}")
    # print(f"Interface data: {interface_data}")
    return messages, interface_data, memory