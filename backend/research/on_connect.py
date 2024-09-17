import global_prompts_config
from dynamodb_service import get_items_with_user, get_all_items_for_presentation_with_user
import json
import asyncio
from session_log_config import get_child_logger
import os

logger = get_child_logger(os.path.abspath(__file__))
interface = "research"

async def initialize(user_id, presentation_id):
    logger.info(f"Initializing research interface for user {user_id}, presentation {presentation_id}")
    memory = {}
    sources_task = get_all_items_for_presentation_with_user('source', presentation_id)
    
    async def get_presentation():
        return await get_items_with_user('presentation', {'presentation_id': presentation_id}, ['messages', 'status', 'topic', 'audience', 'goal', 'memory'], consistent_read=True)

    logger.debug("Fetching presentation and sources")
    presentation, sources = await asyncio.gather(get_presentation(), sources_task)
    
    logger.info(f"Loaded presentation {presentation_id} for user {user_id}")
    logger.debug(f"Presentation data: {presentation}")

    if not presentation:
        logger.error(f"Presentation {presentation_id} not found for user {user_id}")
        raise RuntimeError(f'The presentation you\'re trying to edit was not found, please try creating a new presentation. (user_id: {user_id} presentation_id: {presentation_id})')

    # Poll for topic, audience, and goal
    start_time = asyncio.get_event_loop().time()
    while asyncio.get_event_loop().time() - start_time < 30:
        if presentation.get('topic') and presentation.get('audience') and presentation.get('goal'):
            break
        logger.info(f"Waiting for topic, audience, and goal. Retrying in 3 seconds...")
        await asyncio.sleep(3)
        presentation = await get_presentation()
    
    if not presentation.get('topic'):
        raise RuntimeError(f'The presentation you\'re trying to edit is missing a topic. Please start from the beginning and try again. (presentation_id: {presentation_id})')
    if not presentation.get('audience'):
        raise RuntimeError(f'The presentation you\'re trying to edit is missing a target audience. Please start from the beginning and try again. (presentation_id: {presentation_id})')
    if not presentation.get('goal'):
        raise RuntimeError(f'The presentation you\'re trying to edit is missing a goal. Please start from the beginning and try again. (presentation_id: {presentation_id})')

    if 'messages' in presentation and presentation['messages'] is not None:
        messages = json.loads(presentation['messages'])
        logger.info(f"Loaded {len(messages)} existing messages for presentation {presentation_id}")
    else:
        logger.info(f"No existing messages for presentation {presentation_id}")
        messages = global_prompts_config.initial_messages.copy()

    if 'memory' in presentation and presentation['memory'] is not None:
        memory = json.loads(presentation['memory'])
        logger.debug(f"Loaded memory for presentation {presentation_id}: {memory}")

    if presentation['status'] != interface:
        logger.info(f"Interface changed to {interface} for presentation {presentation_id}")
        summary_message = {
            'role': 'system', 
            'content': f"In the previous steps, you and the user have agreed on the following:\n\nPresentation Topic:\n{presentation['topic']}\n\nTarget Audience:\n{presentation['audience']}\n\nPresentation Goal:\n{presentation['goal']}"
        }
        messages.append(summary_message)
        messages += global_prompts_config.get_interface_changed_messages(interface)
    
    interface_data = {
        'sources': sources or [],
    }
    logger.info(f"Initialization complete for presentation {presentation_id}")
    logger.debug(f"Interface data: {interface_data}")
    return messages, interface_data, memory