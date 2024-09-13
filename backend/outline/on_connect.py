import global_prompts_config
import json
from dynamodb_service import get_items_with_user

interface = "outline"

async def initialize(user_id, presentation_id):
    # get interface keys
    memory = {}

    presentation = await get_items_with_user('presentation', {'presentation_id': presentation_id}, ['messages', 'status', 'topic', 'outline', 'audience', 'goal', 'candidate_topics'])

    # If the presentation does not exist, disconnect with an error message
    if not presentation:
        raise RuntimeError('The presentation you\'re trying to edit was not found, please try creating a new presentation.')
        return

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
    
    interface_data = {
        'all_topics': all_topics,
        'outline': outline,
        # 'included_topics': [{'id': 'id1', 'name': 'Topic 1', 'randomattr':'foo'}, {'id': 'id2', 'name': 'Topic 2'}, {'id': 'id3', 'name': 'Topic 3'}],
        # 'excluded_topics': [{'id': 'id4', 'name': 'Topic 4'}, {'id': 'id5', 'name': 'Topic 5'}, {'id': 'id6', 'name': 'Topic 6'}]
    }

    

    # print(f"Interface keys: {interface_keys}")
    # print(f"onconnect Interface data: {interface_data}")
    

    return messages, interface_data, memory