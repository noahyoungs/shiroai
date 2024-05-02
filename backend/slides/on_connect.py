import global_prompts_config
from dynamodb import get_presentation, get_sources
import json
import asyncio


interface = "slides"

async def initialize(presentationID):
    # get interface keys
    memory = {}

    presentation = await get_presentation(presentationID, ['messages', 'status', 'topic', 'outline', 'audience', 'goal', 'slide_generation_status'])

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
        
    # check if slides are created
    if presentation.get('slide_generation_status') == 'complete':
        slides_created = True
    else:
        slides_created = False
    
    # Messages that enter right after interface change
    if presentation['status'] != interface:
        # Please wait message
        messages.append({ 'role':'assistant', 'content':"Please allow me a moment while I create your slides. This can take up to a minute. Thank you for your patience."})
        
        # background about previous steps
        summary_message = { 'role':'system', 'content':f"Remember, you are working on a presentation with these parameters:\n\nPresentation Topic:\n{presentation['topic']}\n\nTarget Audience:\n{presentation['audience']}\n\nPresentation Goal:\n{presentation['goal']}"}
        messages.append(summary_message)
    
    interfaceData = {
        'slides_created': slides_created
    }

    return messages, interfaceData, memory