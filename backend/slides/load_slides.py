import global_prompts_config
from dynamodb import get_presentation, update_presentation
import json
import asyncio
from slides.get_slide_content import make_presentation_slides

async def load_slides(presentationID, messages, interfaceData, memory, emitter):
    print("RELOADING SLIDES")
    newMessages = []
    
    # first check if candidate topics are already in dynamodb
    presentation = await get_presentation(presentationID, ['slide_generation_status'])
    
    if presentation.get('topic_extraction_status') == 'invoked':
        # keep polling until the topic extraction is done
        while 'slide_generation_status' not in presentation or presentation.get('slide_generation_status') != 'complete':
            await asyncio.sleep(5)
            presentation = await get_presentation(presentationID, ['slide_generation_status'])
    else:
        # get the list of topics from the topic extraction pipeline
        await update_presentation(presentationID, slide_generation_status='invoked')
        await make_presentation_slides(presentationID)
    
    
    interfaceData = {
        'slides_created': True,
        'push': 'all_slides'
        }
    
    newMessages += [message for message in global_prompts_config.get_interface_changed_messages("slides") if message['role'] == 'assistant']
    messages += global_prompts_config.get_interface_changed_messages("slides")
        
    await emitter('interface_update', interfaceData)
    for message in newMessages:
        await emitter('message', message)
            
    return
