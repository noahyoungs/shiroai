import json
import asyncio

interface = "research"

from dynamodb import update_presentation, batch_update_sources

# Constant to control whether to update sources or not
UPDATE_SOURCES = False

async def save_progress(presentation_id, messages, interface_data, memory):
    attributes = {}
    attributes["status"] = interface
    
    if messages:
        attributes["messages"] = json.dumps(messages)
    
    if memory:
        attributes["memory"] = json.dumps(memory)
    
    update_presentation_task = asyncio.create_task(update_presentation(presentation_id, **attributes))
    
    tasks = [update_presentation_task]
    
    if UPDATE_SOURCES and interface_data and interface_data['sources']:
        # all sources where type is 'web'
        web_sources = [source for source in interface_data['sources'] if source['type'] == 'web']
        
        if web_sources:
            batch_update_sources_task = asyncio.create_task(batch_update_sources(presentation_id, web_sources))
            tasks.append(batch_update_sources_task)
    
    # print(f"Saving progress, presentation attributes: {attributes}, web sources: {web_sources}")
    
    await asyncio.gather(*tasks)
    return