import asyncio
import json
from pydantic import BaseModel
from instructor import OpenAISchema
from research.brave_search import search_brave
from typing import List
from pydantic import Field
from research.prompts import getCurrentSourceListMessage
from uuid_extensions import uuid7str
from dynamodb_service import update_items_with_user
from llm_clients import chat_client
from research.read import read_and_summarize_source
from copy import deepcopy
import tokentrim as tt
from research.interface_update import interface_update
import os
from session_log_config import get_child_logger
import decimal

logger = get_child_logger(os.path.abspath(__file__))


def pydantic_to_dict(obj):
    if isinstance(obj, BaseModel):
        return {
            k: pydantic_to_dict(v)
            for k, v in obj.__dict__.items()
            if v is not None
        }
    elif isinstance(obj, list):
        return [pydantic_to_dict(item) for item in obj if item is not None]
    elif isinstance(obj, dict):
        return {
            k: pydantic_to_dict(v)
            for k, v in obj.items()
            if v is not None
        }
    else:
        return obj
    
def convert_decimal_to_float(data):
    if isinstance(data, dict):
        return {k: convert_decimal_to_float(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [convert_decimal_to_float(i) for i in data]
    elif isinstance(data, decimal.Decimal):
        return float(data)
    else:
        return data


async def complete(presentation_id, messages, interface_data, emit, max_turns=15, memory=None):


    logger.info(f"Starting complete function for presentation_id: {
                presentation_id}")

    async def emit_interface_update(updateOnly=False):
        nonlocal interface_data, presentation_id
        logger.debug(f"Updating interface for presentation_id: {
                     presentation_id}")
        interface_data = await interface_update(presentation_id, interface_data, {'action': 'refresh'})
        if not updateOnly:
            await emit('interface_update', convert_decimal_to_float(interface_data))

        return interface_data

    async def emit_delete_interface_update(ids):
        nonlocal interface_data, presentation_id
        logger.debug(f"Deleting items from interface for presentation_id: {
                     presentation_id}, ids: {ids}")
        for id in ids:
            interface_data = await interface_update(presentation_id, interface_data, {'action': 'delete', 'id': id})
        await emit('interface_update', convert_decimal_to_float(interface_data))
        return interface_data

    async def emit_web_search(message):
        logger.debug("Emitting web search results")
        await emit('message', message)

    async def emit_message(message):
        logger.debug("Emitting message that came with tool result")
        await emit('message', message)

    class ProceedToNextStepException(Exception):
        pass

    class ProceedToNextStep(OpenAISchema):
        async def run(self):
            logger.info("Proceeding to next step")
            return True

        async def post_run(self, output):
            raise ProceedToNextStepException()

    class WebSearch(OpenAISchema):
        query: str = Field(...)

        async def run(self):
            nonlocal interface_data
            logger.info(f"Performing web search with query: {self.query}")
            results = await search_brave(self.query, 15)
            if not results:
                logger.warning("No relevant sources found in web search")
                raise ValueError(
                    "No relevant sources found. Please try a different search query.")
            results = [result for result in results if result['url'] not in [
                source.get('url') for source in interface_data.get('sources', [])]][:8]
            if not results:
                logger.warning("All search results already in source list")
                raise ValueError(
                    "Every search result from this query is already in the source list. Please try a different search query.")
            return results

        async def post_run(self, search_results):
            nonlocal memory, interface_data, presentation_id
            logger.debug(f"Processing web search results for presentation_id: {
                         presentation_id}")
            post_messages = [{'role': 'system', 'content': "You must now use the `AddSourcesByID` function to pick only the best web sources from the web search results. Pick the best sources that are most relevant to the presentation. If the user provided any guidance on what sources you should or shouldn't include, make sure to follow that guidance."}]
            search_results = [{**result, 'id': uuid7str()}
                              for result in search_results]
            web_search_message = {'role': 'meta_web_search', 'content': {
                'sources': search_results, 'query': self.query}}
            messages.append(web_search_message)
            asyncio.create_task(emit_web_search(web_search_message))
            tool_results = format_search_results(search_results)
            memory['search_results'] = memory.get(
                'search_results', []) + search_results
            memory['web_searched'] = True
            return tool_results, post_messages

    class RemoveSourcesFromListByID(OpenAISchema):
        ids: List[str] = Field(...)

        async def run(self):
            nonlocal memory, interface_data
            logger.info(f"Removing sources with IDs: {self.ids}")
            full_length_ids = []
            for id in self.ids:
                source = next((s for s in interface_data.get(
                    'sources', None) if s.get("id", "").endswith(id)), None)
                if source:
                    full_length_ids.append(source.get("id"))
                else:
                    logger.warning(f"Source with ID {
                                   id} not found in source list")
                    raise ValueError(f"Source with ID {
                                     id} is not in the source list. Please provide a valid source ID. Make sure are not confusing the source list and the web search result list.")
            return full_length_ids

        async def post_run(self, full_length_ids):
            nonlocal memory, interface_data
            await emit_delete_interface_update(full_length_ids)
            post_messages = [getCurrentSourceListMessage(interface_data)]
            logger.info(f"Successfully removed sources with IDs: {self.ids}")
            return f"Success: Successfully removed sources with IDs {', '.join(self.ids)} from the list of sources.", post_messages

    class AddSourcesByID(OpenAISchema):
        ids: List[str] = Field(...)

        async def run(self):
            nonlocal memory, interface_data
            logger.info(f"Adding sources with IDs: {self.ids}")
            source_dicts = []
            for id in self.ids:
                source_dict = next(
                    (d for d in memory['search_results'] if d.get("id", "").endswith(id)), None)
                if source_dict:
                    if source_dict.get('url') in [source.get('url') for source in interface_data.get('sources', [])]:
                        logger.warning(f"LLM tried to add source with ID {id} - already in source list")
                        raise ValueError(f"Source with ID {id} is already in the source list (possibly under a differend ID). Please provide a different source.")
                    source_dicts.append(source_dict)
                else:
                    logger.warning(f"LLM tried to add source with ID {id} - not found in search results")
                    raise ValueError(f"Source with ID {id} not found. Please provide a valid source ID.")
            if len(source_dicts) == 0:
                raise ValueError("No sources found with the provided IDs.")
            return source_dicts

        async def post_run(self, web_sources):
            nonlocal memory, interface_data
            logger.debug(f"Processing added sources for presentation_id: {presentation_id}")
            sources_to_add_to_db = []
            if len(web_sources) == 0:
                logger.warning("No sources found with the provided IDs")
                return "Error: No sources found with the provided IDs."

            added_source_ids = [source['id'][-8:]
                                for source in web_sources if 'id' in source]

            for web_source in web_sources:
                source_id = web_source.get('id', None)
                if source_id is None:
                    logger.warning("'id' key not found in web_source")
                    continue

                sources_to_add_to_db.append({
                    "type": "web",
                    "url": web_source['url'],
                    "source_id": source_id,
                    "web_source": {key: value for key, value in web_source.items() if key != 'id'},
                    "name": f"{web_source['profile']['name']} | {web_source['title']}",
                })

            seen_ids = set()
            unique_additional_sources = []
            for source in sources_to_add_to_db:
                if source['source_id'] not in seen_ids:
                    seen_ids.add(source['source_id'])
                    unique_additional_sources.append(source)

            sources_to_add_to_db = unique_additional_sources

            sources_to_add_to_db_copy = deepcopy(sources_to_add_to_db)
            
            # add presentation_id to each source
            for source in sources_to_add_to_db_copy:
                source['presentation_id'] = presentation_id

            await update_items_with_user('source', sources_to_add_to_db_copy)

            await emit_interface_update()

            reading_tasks = []

            for source in sources_to_add_to_db:
                reading_task = asyncio.create_task(read_and_summarize_source(
                    source, presentation_id, emit_interface_update))
                reading_tasks.append(reading_task)

            await asyncio.gather(*reading_tasks)

            await emit_interface_update(updateOnly=True)

            post_messages = [getCurrentSourceListMessage(interface_data)]

            char_count = sum(source.get('char_count', 0)
                             for source in interface_data.get('sources', []))
            percentage = round((char_count/50000)*100)

            char_count_status_message = {
                "role": "system", "content": f"You have gathered {percentage}% of the required amount of research. Keep doing more research."}
            proceed_message = {"role": "system", "content": "You have met the minimum amout of research needed. If you haven't already, ask the user if they are satisfied with the current list of sources. If they are, proceed to the next step. If not, do as the user says. DO NOT call the `ProceedToNextStep` function tool until the user has confirmed they are satisfied with the sources."}
            user_files_only_proceed_message = {
                "role": "system", "content": "The user has uploaded file(s) with enough text that you can base the entire presentation around the file(s) that the user uploaded. Ask the user if they want you to find additional sources on the web (Say 'Would you like me to search for additional sources on the web?`). If they do, use the `WebSearch` function tool to find additional sources. If they don't, proceed to the next step. DO NOT call the `ProceedToNextStep` function tool until the user has confirmed they are satisfied with the sources."}

            if percentage > 100:
                logger.info(f"Research completed: {percentage}%")
                if all(source.get('type', '') != 'web' for source in interface_data.get('sources', [])):
                    post_messages.append(user_files_only_proceed_message)
                else:
                    post_messages.append(proceed_message)
            else:
                if interface_data.get('sources', []):
                    post_messages.append(char_count_status_message)

            logger.info(f"Successfully added source(s) {added_source_ids} to the list of sources")
            return f"Success: Successfully added source(s) {added_source_ids} to the list of sources.", post_messages

    async def execute_tool(tool_call, funcs):
        logger.debug(f"Executing tool: {tool_call.function.name}")
        try:
            func = next(
                iter([func for func in funcs if func.__name__ == tool_call.function.name]))
        except StopIteration:
            available_funcs = [func.__name__ for func in funcs]
            error_message = f"Error: Function '{
                tool_call.function.name}' not found. Available functions: {available_funcs}"
            logger.error(error_message)
            return error_message, None

        output = None
        try:
            func = func(**eval(tool_call.function.arguments))
            output = await func.run()
        except Exception as e:
            logger.error(f"Error executing tool {
                         tool_call.function.name}: {str(e)}")
            return f"Error: {str(e)}", None

        if func is not None and hasattr(func, 'post_run'):
            tool_result, post_messages = await func.post_run(output)

        return tool_result, post_messages

    interface_data = await emit_interface_update(updateOnly=True)

    char_count = sum(source.get('char_count', 0)
                     for source in interface_data.get('sources', []))
    percentage = round((char_count/50000)*100)
    logger.info(f"Current research progress: {percentage}%")

    char_count_status_message = {
        "role": "system", "content": f"You have {percentage}% of the required amount of research. Keep going."}
    proceed_message = {"role": "system", "content": "The minimum amout of research needed has been reached. If you haven't already, ask the user if they are satisfied with the current list of sources. If they are, proceed to the next step. If not, do as the user says. DO NOT call the `ProceedToNextStep` function tool until the user has confirmed they are satisfied with the sources."}

    if percentage > 100:
        messages.append(proceed_message)
    else:
        if interface_data.get('sources', []):
            messages.append(char_count_status_message)

    messages.append(getCurrentSourceListMessage(interface_data))

    async def turn(messages, max_turns, turns=0, memory=None):
        logger.debug(f"Starting turn {turns} for presentation_id: {
                     presentation_id}")
        char_count = sum(source.get('char_count', 0)
                         for source in interface_data.get('sources', []))

        completion = await chat_client.chat.completions.create(
            model=os.getenv("CHAT_MODEL_OPENAI_ID"),
            messages=tt.trim(
                messages=[
                    message for message in messages if not message["role"].startswith("meta")],
                model="gpt-3.5-turbo-16k",
            ),
            tools=[
                {"type": "function", "function": dict(
                    WebSearch.openai_schema)},
            ] + (
                [{"type": "function", "function": dict(AddSourcesByID.openai_schema)}] if memory.get(
                    'web_searched', False) else []
            ) + (
                [{"type": "function", "function": dict(ProceedToNextStep.openai_schema)}] if round(
                    (char_count/50000)*100) >= 100 else []
            ) + (
                [{"type": "function", "function": dict(
                    RemoveSourcesFromListByID.openai_schema)}] if interface_data.get('sources', []) else []
            ),
            tool_choice=("auto" if turns < max_turns else "none"),
        )

        if completion.choices[0].message.tool_calls:
            logger.debug(f"Tool calls detected in turn {turns}")
            if completion.choices[0].message.content:
                emit_message(
                    {'role': 'assistant', 'content': completion.choices[0].message.content})

            seen_websearch = False
            filtered_tool_calls = []
            for tool_call in completion.choices[0].message.tool_calls:
                if tool_call.function.name == "WebSearch":
                    if not seen_websearch:
                        filtered_tool_calls.append(tool_call)
                        seen_websearch = True
                else:
                    filtered_tool_calls.append(tool_call)

            completion.choices[0].message.tool_calls = filtered_tool_calls

            messages_dict = pydantic_to_dict(completion.choices[0].message)
            messages.append(messages_dict)

            all_post_messages = []
            for tool_call in completion.choices[0].message.tool_calls:
                try:
                    tool_result, post_messages = await execute_tool(tool_call, [WebSearch, AddSourcesByID, ProceedToNextStep, RemoveSourcesFromListByID])
                    if post_messages:
                        all_post_messages += post_messages
                    logger.info(f"Tool Result: {tool_result[:100]}")
                except ProceedToNextStepException:
                    logger.info("Proceeding to next step")
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": tool_call.function.name,
                        "content": "Success: Proceeding to the next step..."
                    })
                    return messages, [{"role": "assistant", "content": "Proceeding to the next step..."}], True

                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": tool_call.function.name,
                    "content": tool_result
                })

            if all_post_messages:
                messages += all_post_messages

            logger.debug(f"Recursively calling turn {turns + 1}")
            return await turn(messages, max_turns, turns + 1, memory=memory)

        else:
            assert completion.choices[0].message.content
            responseMessage = {'role': 'assistant',
                               'content': completion.choices[0].message.content}
            messages.append(responseMessage)
            logger.info(f"Turn {turns} completed without tool calls")
            return messages, [responseMessage], False

    logger.info(f"Starting turns for presentation_id: {presentation_id}")
    return await turn(messages, max_turns, turns=0, memory=memory)


def format_search_results(results):
    logger.debug("Formatting search results")
    human_readable = "WEB SEARCH RESULTS BELOW (The user already sees this so you don't need to repeat this information back to the user.)\n\n"

    for index, item in enumerate(results, start=1):
        id = item['id'][-8:]
        title = item['title']
        url = item['url']
        description = item['description']
        page_age = item['page_age']
        source = item['profile']['name']

        human_readable += f"   ID: {id}\n"
        human_readable += f"   Title: {title}\n"
        human_readable += f"   URL: {url}\n"
        human_readable += f"   Description: {description}\n"
        if page_age:
            human_readable += f"   Page Age: {page_age}\n"
        human_readable += f"   Profile Name/Publisher: {source}\n"
        human_readable += "\n"

    return human_readable
