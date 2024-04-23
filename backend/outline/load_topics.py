from outline.label_documents_and_extract_topics import label_documents_extract_topics
from uuid_extensions import uuid7str
import global_prompts_config
from dynamodb import get_presentation, update_presentation
import json
import asyncio

async def load_topics(presentationID, messages, interfaceData, memory, emitter):
    print("RELOADING")
    newMessages = []
    
    # first check if candidate topics are already in dynamodb
    presentation = await get_presentation(presentationID, ['candidate_topics', 'topic_extraction_status'])
    
    if 'candidate_topics' in presentation and presentation.get('candidate_topics') is not None:
        topics = json.loads(presentation['candidate_topics'])

    elif presentation.get('topic_extraction_status') == 'invoked':
        # keep polling until the topic extraction is done
        while 'candidate_topics' not in presentation or presentation.get('candidate_topics') is None:
            await asyncio.sleep(5)
            presentation = await get_presentation(presentationID, ['candidate_topics', 'topic_extraction_status'])
    else:
        # get the list of topics from the topic extraction pipeline
        await update_presentation(presentationID, topic_extraction_status='invoked')
        topics = await label_documents_extract_topics(presentationID)
    
    # raise error if topics is anything but a list with length > 0
    if not isinstance(topics, list) or len(topics) == 0:
        raise ValueError("No topics found")

            
    def parse_rating(rating):
        try:
            return int(rating)
        except (ValueError, TypeError):
            return float('inf')  # Default to a high value to include the topic

    # included_topics = [topic for topic in topics if parse_rating(topic.get('relevance_rating', '0')) > 2]
    # excluded_topics = [topic for topic in topics if parse_rating(topic.get('relevance_rating', '0')) <= 2]
    
    for topic in topics:
        if parse_rating(topic.get('relevance_rating', '0')) > 2 and parse_rating(topic.get('value_rating', '0')) > 2:
            topic['included'] = True
        else:
            topic['included'] = False
    
    # outline is a list containing topic ids and included only
    outline = [{'id': topic['id'], 'included': topic['included']} for topic in topics]
    
    # error if either all topics or outline is None or empty
    if topics is None or outline is None:
        raise ValueError("No topics found")
    if len(topics) == 0 or len(outline) == 0:
        raise ValueError("No topics found")
    
    interfaceData = {
        'all_topics': topics,
        'outline': outline,
    }
    newMessages += [message for message in global_prompts_config.get_interface_changed_messages("outline") if message['role'] == 'assistant']
    messages += global_prompts_config.get_interface_changed_messages("outline")
        
    await emitter('interface_update', interfaceData)
    for message in newMessages:
        await emitter('message', message)
            
    return
