import global_prompts_config
from dynamodb import get_presentation, get_sources
import json
from global_prompts_config import interface_keys_for_interface
import asyncio

interface = "research"

async def initialize(presentationID):
    # get interface keys
    interface_keys = global_prompts_config.interface_keys_for_interface[interface]
    memory = {}

    presentation_task = get_presentation(presentationID, ['messages', 'status', 'topic', 'audience', 'goal', 'memory'])
    sources_task = get_sources(presentationID)

    presentation, sources = await asyncio.gather(presentation_task, sources_task)

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
        # Summary of previoius steps
        summary_message = { 'role':'system', 'content':f"In the previous steps, you and the user have agreed on the following:\n\nPresentation Topic:\n{presentation['topic']}\n\nTarget Audience:\n{presentation['audience']}\n\nPresentation Goal:\n{presentation['goal']}"}
        messages.append(summary_message)
        # Preset system and assistant message for interface change
        messages += global_prompts_config.get_interface_changed_messages(interface)

    interfaceData = {
        'sources': sources or [],
    }

    # print(f"Interface keys: {interface_keys}")
    # print(f"Interface data: {interfaceData}")

    return messages, interfaceData, memory