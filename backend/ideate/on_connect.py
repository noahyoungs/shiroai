import global_prompts_config
from dynamodb import get_presentation
import json
from global_prompts_config import interface_keys_for_interface

interface = "ideate"

async def initialize(presentationID):
    # get interface keys
    interface_keys = global_prompts_config.interface_keys_for_interface[interface]
    
    memory = {}
    
    presentation = await get_presentation(presentationID, ['messages', 'status', 'memory'] + interface_keys)

    # Check if 'messages' exists in the presentation and is not None
    if 'messages' in presentation and presentation['messages'] is not None:
        # If so, parse it from JSON
        print(f"Loading existing messages for presentation {presentationID}")
        messages = json.loads(presentation['messages'])
    else:
        # Otherwise, use the default list directly
        print(f"No existing messages for presentation {presentationID}")
        messages = global_prompts_config.initial_messages.copy()
    
    if 'memory' in presentation and presentation['memory'] is not None:
        memory = json.loads(presentation['memory'])
        
    # Messages that enter right after interface change
    if presentation['status'] != interface:
        messages += global_prompts_config.get_interface_changed_messages(interface)

    interfaceData = {}
    for key in interface_keys:
        interfaceData[key] = presentation.get(key, "")
    
    # print(f"Interface keys: {interface_keys}")
    # print(f"Interface data: {interfaceData}")
    return messages, interfaceData, memory