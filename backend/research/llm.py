import asyncio
import json
from pydantic import BaseModel
from instructor import OpenAISchema
from research.brave_search import search_brave
from typing import List
from pydantic import Field
from research.prompts import getCurrentSourceListMessage
from uuid_extensions import uuid7str
from dynamodb import batch_update_sources
from init_llm import client
from research.read import read_and_summarize_source
from copy import deepcopy
import tokentrim as tt
from research.interface_update import interface_update
import os


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

# %%


async def complete(presentation_id, messages, interface_data, emit, max_turns=15, memory=None):

    # helper functions for emitting messages
    async def emit_interface_update(updateOnly=False):
        nonlocal interface_data, presentation_id
        interface_data = await interface_update(presentation_id, interface_data, {'action': 'refresh'})
        if not updateOnly:
            await emit('interface_update', interface_data)
        return interface_data

    async def emit_delete_interface_update(ids):
        nonlocal interface_data, presentation_id
        for id in ids:
            interface_data = await interface_update(presentation_id, interface_data, {'action': 'delete', 'id': id})
        await emit('interface_update', interface_data)
        return interface_data

    async def emit_web_search(message):
        print("Emitting web search results")
        await emit('message', message)

    async def emit_message(message):
        print("Emitting message that came with tool result")
        await emit('message', message)

    class ProceedToNextStepException(Exception):
        pass

    # classes for the function tools
    class ProceedToNextStep(OpenAISchema):
        """Continue to the next step in the presentation creation process. Only call this function tool after you ask the user if they are satisfied with the current list of sources and they confirm that they are."""

        async def run(self):
            return True

        async def post_run(self, output):
            raise ProceedToNextStepException()

    class WebSearch(OpenAISchema):
        """Search the web for a source relevant to the presentation."""

        query: str = Field(
            ...,
            description="An excellent search query consisting of a concise combination of specific, relevant, and important keywords closely related to the desired information while avoiding overly broad or general terms.",
            examples=[
                        'artificial intelligence impact future work automation jobs',
                        'workplace mental health promotion strategies employee well-being',
                        'renewable energy role combating climate change sustainable future',
                        'effective time management techniques productivity tips strategies'
            ]
        )

        # errors raised here are considered the model's mistake
        async def run(self):
            nonlocal interface_data
            results = await search_brave(self.query, 15)
            if not results:
                raise ValueError(
                    "No relevant sources found. Please try a different search query.")
            # filter out sources that are already in the source list, limit to 8 results
            results = [result for result in results if result['url'] not in [
                source.get('url') for source in interface_data.get('sources', [])]][:8]
            if not results:
                raise ValueError(
                    "Every search result from this query is already in the source list. Please try a different search query.")
            return results

        # errors raised here are not caght
        # second param is the output of the run function
        async def post_run(self, search_results):
            nonlocal memory, interface_data, presentation_id
            post_messages = [{'role': 'system', 'content': "You must now use the `AddSourcesByID` function to pick only the best web sources from the web search results. Pick the best sources that are most relevant to the presentation. If the user provided any guidance on what sources you should or shouldn't include, make sure to follow that guidance."}]
            # add id to each search result
            search_results = [{**result, 'id': uuid7str()}
                              for result in search_results]

            # web search meta message
            web_search_message = {'role': 'meta_web_search', 'content': {
                'sources': search_results, 'query': self.query}}
            # append to messages
            messages.append(web_search_message)
            # fire and forget web search emission
            asyncio.create_task(emit_web_search(web_search_message))

            # format results before sending to llm
            tool_results = format_search_results(search_results)
            # push search results to memory
            memory['search_results'] = memory.get(
                'search_results', []) + search_results

            # set web_searched to True in memory so add source function included
            memory['web_searched'] = True

            return tool_results, post_messages

    class RemoveSourcesFromListByID(OpenAISchema):
        """Remove sources from the list of sources by IDs"""

        ids: List[str] = Field(
            ...,
            description="The IDs of the sources to remove.",
            examples=[["a1b2c3d4", "e5f6g7h8"]],
        )

        # errors raised here are considered the model's mistake
        async def run(self):
            nonlocal memory, interface_data
            full_length_ids = []
            for id in self.ids:
                source = next((s for s in interface_data.get(
                    'sources', None) if s.get("id", "").endswith(id)), None)
                if source:
                    full_length_ids.append(source.get("id"))
                    pass
                else:
                    raise ValueError(
                        f"Source with ID {id} is not in the source list. Please provide a valid source ID. Make sure are not confusing the source list and the web search result list.")
            return full_length_ids

        # errors raised here are not caught
        # second param is the output of the run function
        async def post_run(self, full_length_ids):
            nonlocal memory, interface_data
            # await interface updata to get latest source list for next completiom
            await emit_delete_interface_update(full_length_ids)
            post_messages = [getCurrentSourceListMessage(interface_data)]
            return f"Success: Successfully removed sources with IDs {', '.join(self.ids)} from the list of sources.", post_messages

    class AddSourcesByID(OpenAISchema):
        """Add sources to the list of sources by IDs found in the web search"""
        ids: List[str] = Field(
            ...,
            description="The IDs of the sources to add. These IDs should be obtained from the web search results.",
            examples=[["a1b2c3d4", "e5f6g7h8"]],
        )

        # errors raised here are considered the model's mistake
        async def run(self):
            nonlocal memory, interface_data
            source_dicts = []
            for id in self.ids:
                source_dict = next(
                    (d for d in memory['search_results'] if d.get("id", "").endswith(id)), None)
                if source_dict:
                    if source_dict.get('url') in [source.get('url') for source in interface_data.get('sources', [])]:
                        raise ValueError(
                            f"Source with ID {id} is already in the source list (possibly under a differend ID). Please provide a different source.")
                    source_dicts.append(source_dict)
                else:
                    raise ValueError(
                        f"Source with ID {id} not found. Please provide a valid source ID.")
            if len(source_dicts) == 0:
                raise ValueError("No sources found with the provided IDs.")
            return source_dicts

        # errors raised here are not caught
        # second param is the output of the run function
        async def post_run(self, web_sources):
            nonlocal memory, interface_data

            additional_sources = []
            if len(web_sources) == 0:
                return "Error: No sources found with the provided IDs."

            # print("DEBUG: web_sources array:")
            # print(web_sources)

            added_source_ids = [source['id'][-8:]
                                for source in web_sources if 'id' in source]

            for web_source in web_sources:
                source_id = web_source.get('id', None)
                if source_id is None:
                    print("DEBUG: 'id' key not found in web_source")
                    continue  # Skip processing if 'id' is missing

                additional_sources.append({
                    "type": "web",
                    "url": web_source['url'],
                    "id": source_id,
                    "web_source": {key: value for key, value in web_source.items() if key != 'id'},
                    "name": f"{web_source['profile']['name']} | {web_source['title']}",
                })

            # HERE
            # Remove duplicate sources based on the 'id' field
            seen_ids = set()
            unique_additional_sources = []
            for source in additional_sources:
                if source['id'] not in seen_ids:
                    seen_ids.add(source['id'])
                    unique_additional_sources.append(source)

            # Update additional_sources with the unique sources
            additional_sources = unique_additional_sources

            # for some reason this call is popping ids off of additional sources so im making a copy because im too lazy to fix issue
            additional_sources_copy = deepcopy(additional_sources)
            await batch_update_sources(presentation_id, additional_sources_copy)

            # await interface updata to get latest source list for next completiom
            await emit_interface_update()

            # create a list to store the reading tasks
            reading_tasks = []

            for source in additional_sources:
                # create a task for reading and add it to the list
                reading_task = asyncio.create_task(read_and_summarize_source(
                    source, presentation_id, emit_interface_update))
                reading_tasks.append(reading_task)

            # wait for all reading tasks to complete
            await asyncio.gather(*reading_tasks)

            # here the interface should already be updated by the callbacks but we need to update interface_data here to get the character count
            await emit_interface_update(updateOnly=True)

            # get new source list message after adding sources
            post_messages = [getCurrentSourceListMessage(interface_data)]

            # System messages that go after each time model adds sources
            char_count = 0
            for source in interface_data.get('sources', []):
                char_count += source.get('char_count', 0)
            percentage = round((char_count/50000)*100)

            char_count_status_message = {
                "role": "system", "content": f"You have gathered {percentage}% of the required amount of research. Keep doing more research."}
            # message about proceeding to the next step if we have 5 or more sources
            proceed_message = {"role": "system", "content": "You have met the minimum amout of research needed. If you haven't already, ask the user if they are satisfied with the current list of sources. If they are, proceed to the next step. If not, do as the user says. DO NOT call the `ProceedToNextStep` function tool until the user has confirmed they are satisfied with the sources."}
            user_files_only_proceed_message = {
                "role": "system", "content": "The user has uploaded file(s) with enough text that you can base the entire presentation around the file(s) that the user uploaded. Ask the user if they want you to find additional sources on the web (Say 'Would you like me to search for additional sources on the web?`). If they do, use the `WebSearch` function tool to find additional sources. If they don't, proceed to the next step. DO NOT call the `ProceedToNextStep` function tool until the user has confirmed they are satisfied with the sources."}

            if percentage > 100:
                print("Percentage of research completed 241: ", percentage)
                if all(source.get('type', '') != 'web' for source in interface_data.get('sources', [])):
                    post_messages.append(user_files_only_proceed_message)
                else:
                    post_messages.append(proceed_message)
            else:
                if not len(interface_data.get('sources', [])) == 0:
                    post_messages.append(char_count_status_message)

            return f"Success: Successfully added source(s) {added_source_ids} to the list of sources.", post_messages

    # function to execute the tool function
    async def execute_tool(tool_call, funcs):
        """
        Executes a tool function based on the provided tool call and a list of available functions.

        Args:
            tool_call (ToolCall): The tool call object containing the function name and arguments.
            funcs (list): A list of available function objects.

        Returns:
            tool_result (str): The result of the tool function execution.

        Raises:
            ValueError: If the specified function is not found in the list of available functions.
            Exception: If an error occurs during the execution of the tool function.
        """
        # func is first match in funcs where the name of the function is the same as the name of the function in the tool call
        try:
            func = next(
                iter([func for func in funcs if func.__name__ == tool_call.function.name]))
        except StopIteration:
            available_funcs = [func.__name__ for func in funcs]
            error_message = f"Error: Function '{tool_call.function.name}' not found. Available functions: {available_funcs}"
            return error_message, None

        output = None
        try:
            # func becomes instance of class created with arguments from model
            func = func(**eval(tool_call.function.arguments))
            # get outputs from the tool
            output = await func.run()
        except Exception as e:
            return f"Error: {str(e)}", None

        # Run post_run() method after the try block
        if func is not None and hasattr(func, 'post_run'):
            tool_result, post_messages = await func.post_run(output)

        return tool_result, post_messages

    interface_data = await emit_interface_update(updateOnly=True)

    # Update the model on sources in case user added sources
    char_count = 0
    for source in interface_data.get('sources', []):
        char_count += source.get('char_count', 0)
    percentage = round((char_count/50000)*100)
    print("Percentage of research completed 294: ", percentage)

    char_count_status_message = {
        "role": "system", "content": f"You have {percentage}% of the required amount of research. Keep going."}
    # message about proceeding to the next step if we have 5 or more sources
    proceed_message = {"role": "system", "content": "The minimum amout of research needed has been reached. If you haven't already, ask the user if they are satisfied with the current list of sources. If they are, proceed to the next step. If not, do as the user says. DO NOT call the `ProceedToNextStep` function tool until the user has confirmed they are satisfied with the sources."}

    if percentage > 100:
        messages.append(proceed_message)
    else:
        if not len(interface_data.get('sources', [])) == 0:
            messages.append(char_count_status_message)

    # update LLM on current sources because the user may have added sources
    messages.append(getCurrentSourceListMessage(interface_data))

    # print(messages)
    async def turn(messages, max_turns, turns=0, memory=None):
        # print(f"Turn {turns}, Sources: {interface_data['sources']}, Memory: {memory}")
        char_count = 0
        for source in interface_data.get('sources', []):
            char_count += source.get('char_count', 0)

        # with open('messages.json', 'w') as f:
        #     json.dump(messages, f)

        completion = await client.chat.completions.create(
            model=os.getenv("CHAT_MODEL_OPENAI_ID"),
            # filter out any messages with roles that start with meta
            messages=tt.trim(
                messages=[
                    message for message in messages if not message["role"].startswith("meta")],
                model="gpt-3.5-turbo-16k",
            ),
            tools=[
                {
                    "type": "function",
                            "function": dict(WebSearch.openai_schema),
                },
            ] + (
                [{
                    "type": "function",
                    "function": dict(AddSourcesByID.openai_schema),
                }] if memory.get('web_searched', False) else []
            ) + (
                [{
                    "type": "function",
                    "function": dict(ProceedToNextStep.openai_schema),
                }] if round((char_count/50000)*100) >= 100 else []
            ) + (
                [{
                    "type": "function",
                    "function": dict(RemoveSourcesFromListByID.openai_schema),
                }] if interface_data.get('sources', []) else []
            ),
            tool_choice=("auto" if turns < max_turns else "none"),
        )

        if completion.choices[0].message.tool_calls:

            # if theres a message content emit it
            if completion.choices[0].message.content:
                emit_message(
                    {'role': 'assistant', 'content': completion.choices[0].message.content})

            # if there are multiple tool calls with name WebSearch, remove all but the first
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

            # Append the message as a dict to prevent serialization issues
            messages_dict = pydantic_to_dict(completion.choices[0].message)
            messages.append(messages_dict)

            all_post_messages = []
            for tool_call in completion.choices[0].message.tool_calls:
                try:
                    tool_result, post_messages = await execute_tool(tool_call, [WebSearch, AddSourcesByID, ProceedToNextStep, RemoveSourcesFromListByID])
                    if post_messages:
                        all_post_messages += post_messages
                    print(f"Tool Result: {tool_result[:100]}")
                except ProceedToNextStepException:
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": tool_call.function.name,
                        "content": "Succcess: Proceeding to the next step..."
                    })
                    return messages, [{"role": "assistant", "content": "Proceeding to the next step..."}], True

                # Append the tool result
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": tool_call.function.name,
                    "content": tool_result
                })

            # Append the post messages
            if all_post_messages not in (None, []):
                messages += all_post_messages

            # recursively call complete until no tool calls
            # save messages to json
            # with open('messages.json', 'w') as f:
            #     json.dump(messages, f)
            return await turn(messages, max_turns, turns + 1, memory=memory)

        else:
            assert completion.choices[0].message.content
            responseMessage = {'role': 'assistant',
                               'content': completion.choices[0].message.content}
            messages.append(responseMessage)
            return messages, [responseMessage], False

    return await turn(messages, max_turns, turns=0, memory=memory)


def format_search_results(results):
    # Initialize an empty string to store the human-readable content
    human_readable = "WEB SEARCH RESULTS BELOW (The user already sees this so you don't need to repeat this information back to the user.)\n\n"

    # Iterate over each item in the parsed data
    for index, item in enumerate(results, start=1):
        # Extract relevant information from each item
        id = item['id'][-8:]
        title = item['title']
        url = item['url']
        description = item['description']
        page_age = item['page_age']
        source = item['profile']['name']

        # Append the information to the human-readable string
        human_readable += f"   ID: {id}\n"
        human_readable += f"   Title: {title}\n"
        human_readable += f"   URL: {url}\n"
        human_readable += f"   Description: {description}\n"
        if page_age:
            human_readable += f"   Page Age: {page_age}\n"
        human_readable += f"   Profile Name/Publisher: {source}\n"
        human_readable += "\n"

    return human_readable


# %%
