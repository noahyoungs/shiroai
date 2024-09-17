
import global_prompts_config
import json
from typing import List
from slides.persistent_slide_list import PersistentSlideList
from dynamodb_service import get_items_with_user, update_items_with_user


interface = "slides"
interface_data_keys = ['current_slide_id']

async def initialize(user_id, presentation_id, emit):
    # get interface keys
    memory = {}
    all_docs = []

    # presentation = await get_presentation(presentation_id, ['messages', 'status', 'topic', 'outline', 'audience', 'goal', 'slide_generation_status']+ interface_data_keys)
    attributes =  ['messages', 'status', 'topic', 'outline', 'audience', 'goal', 'slide_generation_status']+ interface_data_keys
    presentation = await get_items_with_user('presentation', {'user_id': user_id, 'presentation_id': presentation_id}, attributes)

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
        
    # check if slides are created
    if presentation.get('slide_generation_status') == 'complete':
        slides_created = True
        
        # get all the slides, put them in a PersistentSlideList and set as memory
        slide_list = PersistentSlideList(presentation_id, emitter=emit)
        await slide_list.fetch_all_slides()
        memory['slide_list'] = slide_list
    else:
        slides_created = False

    # Messages that enter right after interface change
    if presentation['status'] != interface:
        # Please wait message
        messages.append({'role': 'assistant', 'content': "Please allow me a moment while I create your slides. This can take up to a minute. Thank you for your patience."})

        # background about previous steps
        summary_message = {'role': 'system', 'content': f"Remember, you are working on a presentation with these parameters:\n\nPresentation Topic:\n{presentation['topic']}\n\nTarget Audience:\n{presentation['audience']}\n\nPresentation Goal:\n{presentation['goal']}"}
        messages.append(summary_message)

        # update the presentation status with the new interface
        update_items_with_user('presentation', {'presentation_id': presentation_id, 'status': interface})

    interface_data = {
        'slides_created': slides_created
    }
    
    if presentation.get('current_slide_id'):
        interface_data['current_slide_id'] = presentation['current_slide_id']
        
    print(f"Initalized slides interface with interface data: {interface_data}")

    return messages, interface_data, memory