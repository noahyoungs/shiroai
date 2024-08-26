from instructor import OpenAISchema
from enum import Enum
from pydantic import BaseModel, Field
from typing import List
from typing_extensions import Literal
from init_llm import client
import tokentrim as tt
from dynamodb import get_presentation
import json
import os


async def getCurrentSubtopicListMessage(interfaceData, presentationID):
    if not isinstance(interfaceData['all_topics'], list):
        presentation = await get_presentation(presentationID, ['candidate_topics', 'topic_extraction_status'])
        if 'candidate_topics' in presentation and presentation.get('candidate_topics') is not None:
            topics = json.loads(presentation['candidate_topics'])
        if topics:
            interfaceData['all_topics'] = topics
            print("WARNING: all_topics not found in interfaceData. Fetching from dynamodb.")
        else:
            raise ValueError("all_topics must be a list")
    if not isinstance(interfaceData['outline'], list):
        raise ValueError("outline must be a list")
    
    included_topics = [(next((d for d in interfaceData['all_topics'] if d['id'] == subtopic['id']), None)) for subtopic in interfaceData['outline'] if subtopic['included']]
    excluded_topics = [(next((d for d in interfaceData['all_topics'] if d['id'] == subtopic['id']), None)) for subtopic in interfaceData['outline'] if not subtopic['included']]
    
    included_lists = []
    excluded_lists = []

    for subtopic in included_topics:
        included_lists.append({
            'id': subtopic['id'][-8:],
            'name': subtopic['name'],
            'keywords': ', '.join(subtopic['keywords']),
            'relevance_score': subtopic['relevance_rating'],
            'relevance_reasoning': subtopic['relevance_reasoning'],
            'content_quality_score': subtopic['value_rating'],
        })

    for subtopic in excluded_topics:
        excluded_lists.append({
            'id': subtopic['id'][-8:],
            'name': subtopic['name'],
            'keywords': ', '.join(subtopic['keywords']),
            'relevance_score': subtopic['relevance_rating'],
            'relevance_reasoning': subtopic['relevance_reasoning'],
            'content_quality_score': subtopic['value_rating']
        })

    included_xml = "<included_subtopics>\n"
    for included_subtopic in included_lists:
        included_xml += f"<subtopic>\n"
        included_xml += f"<id>{included_subtopic['id']}</id>\n"
        included_xml += f"<name>{included_subtopic['name']}</name>\n"
        included_xml += f"<keywords>{included_subtopic['keywords']}</keywords>\n"
        included_xml += f"<relevance_score>{included_subtopic['relevance_score']}</relevance_score>\n"
        # included_xml += f"<relevance_reasoning>{included_subtopic['relevance_reasoning']}</relevance_reasoning>\n"
        included_xml += f"<content_quality_score>{included_subtopic['content_quality_score']}</content_quality_score>\n"
        included_xml += "</subtopic>\n"
    included_xml += "</included_subtopics>\n"

    excluded_xml = "<excluded_subtopics>\n"
    for excluded_subtopic in excluded_lists:
        excluded_xml += f"<subtopic>\n"
        excluded_xml += f"<id>{excluded_subtopic['id']}</id>\n"
        excluded_xml += f"<name>{excluded_subtopic['name']}</name>\n"
        excluded_xml += f"<keywords>{excluded_subtopic['keywords']}</keywords>\n"
        excluded_xml += f"<relevance_score>{excluded_subtopic['relevance_score']}</relevance_score>\n"
        # excluded_xml += f"<relevance_reasoning>{excluded_subtopic['relevance_reasoning']}</relevance_reasoning>\n"
        excluded_xml += f"<content_quality_score>{excluded_subtopic['content_quality_score']}</content_quality_score>\n"
        excluded_xml += "</subtopic>\n"
    excluded_xml += "</excluded_subtopics>\n"
    
    begin_message = "Here are all the subtopics. Note: The <relevance_score></relevance_score> measures how relevant the subtopic is to the overall presentation topic, audience and goal. The <content_quality_score></content_quality_score> measures the content quality of the research excerpts done for the subtopic. Both scores are on a scale of 1-5, with 5 being the highest.\n\n"

    included_header = "Here are the included subtopics:\n"
    excluded_header = "Here are the excluded subtopics:\n"
    no_included_subtopics = "There are no included subtopics (None of the subtopics are included).\n"
    no_excluded_subtopics = "There are no excluded subtopics (All of the subtopics are included).\n"
    
    end_message = "DO NOT REPEAT THIS LIST BACK TO THE USER because they can already see the list next to the chat interface.\n\nRemember, your task is to make sure the <included_topics></included_topics> section contains only topics that the user wants in the presentation."
    
    included_string = included_header + included_xml if included_lists else no_included_subtopics
    excluded_string = excluded_header + excluded_xml if excluded_lists else no_excluded_subtopics
    
    string = included_string + "\n" + excluded_string + "\n" + end_message
    return {'role': 'system', 'content': string.strip()}

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
    

async def complete(presentationID, messages, interfaceData, max_turns=5, emitter=None, memory=None):
    current_turn = 0
    new_messages = []
    
    async def new_turn(presentationID, messages, interfaceData, current_turn, max_turns=5, emitter=None, memory=None):
    
        class ProceedToNextStepException(Exception):
                pass
            
        # classes for the function tools
        class ProceedToNextStep(OpenAISchema):
            """Continue to the next step in the presentation creation process. Only call this function tool after you ask the user if they are satisfied with the current list of sources and they confirm that they are."""
        
            async def run(self):
                return True
            
            async def post_run(self, output):
                raise ProceedToNextStepException()
            
        
        # class IncludeTopic(OpenAISchema):
        #     """Include a source in the presentation by moving it from the excluded sources list to the included sources list."""
        #     topic_id: str = Field (
        #         ...,
        #         description="The ID of the source to include. This ID must be in the excluded sources list.",
        #         examples=["a1b2c3d4"],
        #     )
            
        #     # errors raised here are considered the model's mistake
        #     async def run(self):
        #         nonlocal memory, interfaceData
        #         source = next((s for s in interfaceData.get('excluded_topics', None) if s.get("id", "").endswith(self.topic_id)), None)
        #         if not source:
        #             raise ValueError(f"Topic with ID {id} is not in the exlcuded topics list. You can only include topics that are in the excluded topics list.")
        #         return source["id"] # the whole id
            
        #     # errors raised here are not caught
        #     # second param is the output of the run function
        #     async def post_run(self, id):
        #         nonlocal memory, interfaceData
        #         # move the topic to the included topics list
        #         topic_to_move = next((d for d in interfaceData['excluded_topics'] if d['id'] == id), None)
        #         if topic_to_move:
        #             interfaceData['included_topics'].append(topic_to_move)
        #             interfaceData['excluded_topics'].remove(topic_to_move)             
        #         else:
        #             raise ValueError(f"Topic with ID {id} not found in the excluded topics list even though it was validated in the run function.")   
        #         # post_messages = [getCurrentTopicListMessage(interfaceData)]
        #         return f"Success: Successfully moved topic {self.topic_id} to included topics"
            
        # class ExcludeTopic(OpenAISchema):
        #     """Exclude a source from the presentation by moving it from the included sources list to the excluded sources list."""
        #     topic_id: str = Field(
        #         ...,
        #         description="The ID of the source to exclude. This ID must be in the included sources list.",
        #         examples=["a1b2c3d4"],
        #     )
            
        #     # errors raised here are considered the model's mistake
        #     async def run(self):
        #         source = next((s for s in interfaceData.get('included_topics', None) if s.get("id", "").endswith(self.topic_id)), None)
        #         if not source:
        #             raise ValueError(f"Topic with ID {id} is not in the included topics list. You can only exclude topics that are in the included topics list.")
        #         return source["id"]
            
        #     # errors raised here are not caught
        #     # second param is the output of the run function
        #     async def post_run(self, id):
        #         nonlocal memory, interfaceData
        #         # move the topic to the excluded topics list
        #         topic_to_move = next((d for d in interfaceData['included_topics'] if d['id'] == id), None)
        #         if topic_to_move:
        #             interfaceData['excluded_topics'].append(topic_to_move)
        #             interfaceData['included_topics'].remove(topic_to_move)
        #         else:
        #             raise ValueError(f"Topic with ID {id} not found in the included topics list even though it was validated in the run function.")
        #         # post_messages = [getCurrentTopicListMessage(interfaceData)]
        #         return f"Success: Successfully moved topic {self.topic_id} to excluded topics"
            
        class SetIncludedSubtopics(OpenAISchema):
            """Set the list of topics included in the presentation"""
            ids_in_new_order: List[str] = Field(
            ...,
            description="The IDs of the subtopics you want included, in the order they should appear in the presentation.",
            examples=[["a1b2c3d4", "e5f6g7h8", "i9j0k1l2", "m3n4o5p6", "q7r8s9t0"]],
        )
            
            # errors raised here are considered the model's mistake
            async def run(self):
                nonlocal memory, interfaceData
                # Check that all the id prefixes match an id in the outline
                unmatched_prefixes = [prefix for prefix in self.ids_in_new_order
                      if not any(prefix == subtopic['id'][-8:] for subtopic in interfaceData['outline'])]

                if unmatched_prefixes:
                    raise ValueError(f"Error: The following ID prefixes do not match any subtopic in the outline: {', '.join(unmatched_prefixes)}")
                
                return self.ids_in_new_order
            
            # errors raised here are not caught
            # second param is the output of the run function
            async def post_run(self, new_order):
                nonlocal memory, interfaceData

                new_outline = []

                # Create a dictionary to map id prefixes to their corresponding subtopics
                subtopic_dict = {subtopic['id'][-8:]: subtopic for subtopic in interfaceData['outline']}

                # Iterate over the id prefixes in new_order and add the corresponding topics to new_included_topics
                for prefix in new_order:
                    if prefix in subtopic_dict:
                        new_outline.append(dict(subtopic_dict[prefix], included=True))
                    else:
                        print(f"Warning: ID prefix '{prefix}' not found in subtopics.")

                # Add the remaining subtopics
                for subtopic in interfaceData['outline']:
                    if subtopic['id'][-8:] not in new_order:
                        new_outline.append(dict(subtopic, included=False))
                
                print(f"New Outline kength: {len(new_outline)}")
                interfaceData['outline'] = new_outline
                print(f"Interfacedata new outline length: {len(interfaceData['outline'])}")

                await emitter('interface_update', interfaceData)


                return "Success: Successfully set the included subtopics list."
        
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
                func = next(iter([func for func in funcs if func.__name__ == tool_call.function.name]))
            except StopIteration:
                available_funcs = [func.__name__ for func in funcs]
                error_message = f"Error: Function '{tool_call.function.name}' not found. Available functions: {available_funcs}"
                return error_message, None

            output = None
            try:
                # func becomes instance of class created with arguments from model
                func = func(**eval(tool_call.function.arguments))
                # get outputs from the run function
                output = await func.run()
            except Exception as e:
                # model error
                return f"Error: {str(e)}", None

            # Run post_run() method after the try block
            if func is not None and hasattr(func, 'post_run'):
                tool_result = await func.post_run(output)

            return tool_result
        
        # Update the model on the current source list
        messages.append( await getCurrentSubtopicListMessage(interfaceData, presentationID))
        
        completion = await client.chat.completions.create(
            model=os.getenv("CHAT_MODEL_OPENAI_ID"),
            # filter out any messages with roles that start with meta
            messages=tt.trim(
                messages=[message for message in messages if not message["role"].startswith("meta")],
                model="gpt-3.5-turbo-16k",
            ),
            tools=[
                    # {
                    #     "type": "function",
                    #     "function": dict(IncludeTopic.openai_schema),
                    # },
                    # {
                    #     "type": "function",
                    #     "function": dict(ExcludeTopic.openai_schema),
                    # },
                    {
                        "type": "function",
                        "function": dict(SetIncludedSubtopics.openai_schema),
                    },
                    {
                        "type": "function",
                        "function": dict(ProceedToNextStep.openai_schema),
                    }
                ],
            tool_choice=("auto" if current_turn < max_turns else "none"),
        )
        
        if completion.choices[0].message.tool_calls:
            
            # if theres a message content add to new messages
            if completion.choices[0].message.content:
                new_messages.append({'role':'assistant', 'content': completion.choices[0].message.content})
            
            # Append the message as a dict to prevent serialization issues
            messages_dict = pydantic_to_dict(completion.choices[0].message)
            messages.append(messages_dict)
            
            for tool_call in completion.choices[0].message.tool_calls:
                try: 
                    # tool_result = await execute_tool(tool_call, [IncludeTopic, ExcludeTopic, ReorderIncludedTopics, ProceedToNextStep])
                    tool_result = await execute_tool(tool_call, [SetIncludedSubtopics, ProceedToNextStep])
                    print(f"Line 344 Interface Data all_topics length: {len(interfaceData['all_topics'])}")
                    print(f"Tool Result: {tool_result}")
                except ProceedToNextStepException:
                    return messages, [{"role": "system", "content": "Proceeding to the next step..."}], True

                # Append the tool result
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": tool_call.function.name,
                    "content": tool_result
                    })
            
            # recursively call complete until no tool calls
            return await new_turn(presentationID, messages, interfaceData, current_turn + 1, max_turns, emitter=emitter, memory=memory)
        else:
            assert completion.choices[0].message.content
            responseMessage = {'role':'assistant', 'content': completion.choices[0].message.content}
            new_messages.append(responseMessage)
            messages.append(responseMessage)
            return messages, new_messages, False
        
    return await new_turn(presentationID, messages, interfaceData, current_turn, max_turns, emitter=emitter, memory=memory)
        
        
                    
                    
