import global_prompts_config
from dynamodb import get_presentation, get_sources
import json
import asyncio


interface = "outline"

async def initialize(presentationID):
    # get interface keys
    memory = {}

    presentation = await get_presentation(presentationID, ['messages', 'status', 'topic', 'outline', 'audience', 'goal', 'candidate_topics'])

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
        
    # check if we have topics in the database
    if 'outline' in presentation and presentation['outline'] is not None:
        # print(f"Outline: {presentation['outline']}")
        outline = json.loads(presentation.get('outline'))
        print(f"Loading existing outline for presentation")
        all_topics = json.loads(presentation.get('candidate_topics'))
        if len(all_topics) != len(outline):
            print(f"Length of all_topics: {len(all_topics)}")
            print(f"Length of outline: {len(outline)}")
            raise ValueError("Length of all_topics and outline do not match")
            all_topics = None
            outline = None
    else:
        all_topics = None
        outline = None
        
    # Messages that enter right after interface change
    if presentation['status'] != interface:
        # Please wait message
        messages.append({ 'role':'assistant', 'content':"Please allow me a moment while I analyze the sources for potential subtopics to include in your presentation. This can take up to a minute. Thank you for your patience."})
        
        # background about previous steps
        summary_message = { 'role':'system', 'content':f"Remember, you are working on a presentation with these parameters:\n\nPresentation Topic:\n{presentation['topic']}\n\nTarget Audience:\n{presentation['audience']}\n\nPresentation Goal:\n{presentation['goal']}"}
        messages.append(summary_message)
    
    interfaceData = {
        'all_topics': all_topics,
        'outline': outline,
        # 'included_topics': [{'id': 'id1', 'name': 'Topic 1', 'randomattr':'foo'}, {'id': 'id2', 'name': 'Topic 2'}, {'id': 'id3', 'name': 'Topic 3'}],
        # 'excluded_topics': [{'id': 'id4', 'name': 'Topic 4'}, {'id': 'id5', 'name': 'Topic 5'}, {'id': 'id6', 'name': 'Topic 6'}]
    }

    

    # print(f"Interface keys: {interface_keys}")
    # print(f"onconnect Interface data: {interfaceData}")
    

    return messages, interfaceData, memory