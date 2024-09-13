import json
import asyncio

interface = "research"

from dynamodb_service import update_items_with_user

# Constant to control whether to update sources or not
UPDATE_SOURCES = False

async def save_progress(presentation_id, messages, interface_data, memory):
    attributes = {}
    attributes["status"] = interface
    
    if messages:
        attributes["messages"] = json.dumps(messages)
    
    if memory:
        attributes["memory"] = json.dumps(memory)
    
    update_presentation_task = asyncio.create_task(update_items_with_user('presentation', [{**attributes, 'presentation_id': presentation_id}]))
    
    tasks = [update_presentation_task]
    
    if UPDATE_SOURCES and interface_data and interface_data['sources']:
        # all sources where type is 'web'
        web_sources = [source for source in interface_data['sources'] if source['type'] == 'web']
        
        if web_sources:
            # update_sources_task = asyncio.create_task(update_items_with_user('source', web_sources))
            update_sources_task = asyncio.create_task(update_items_with_user('source', [{**source, 'presentation_id': presentation_id} for source in web_sources])) # add presentation_id to each source just in case its not in there

            tasks.append(update_sources_task)
    
    # print(f"Saving progress, presentation attributes: {attributes}, web sources: {web_sources}")
    
    await asyncio.gather(*tasks)
    return