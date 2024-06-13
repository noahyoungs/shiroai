from instructor import OpenAISchema
from enum import Enum
from pydantic import BaseModel, Field
from typing import List
from typing_extensions import Literal
from init_llm import client
import tokentrim as tt
from dynamodb import get_presentation
from edit_slide import edit_slide
import json



async def getCurrentSlideMessage(interfaceData, presentationID):
    pass

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
            
        class EditCurrentSlide(OpenAISchema):
            """Call this function to have the Slide Editor Agent edit the current slide in the presentation."""
            edit_instructions: str
            
            async def run(self):
                return True
            
            async def post_run(self, output):
                try:
                    # edit the current slide
                    slide, message = await edit_slide(presentationID, interfaceData, self.edit_instructions)
                    return "Success! Slide Editor Agent: " + message
                except Exception as e:
                    return f"Error: {str(e)}"
                    
        
        class DeleteCurrentSlide(OpenAISchema):
            pass
        
        class AddSlideHere(OpenAISchema):
            pass
        
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
        
        # Update the model on the current slide
        messages.append( await getCurrentSlideMessage(interfaceData, presentationID))
        
        completion = await client.chat.completions.create(
            model="gpt-3.5-turbo-0125",
            # filter out any messages with roles that start with meta
            messages=tt.trim(
                messages=[message for message in messages if not message["role"].startswith("meta")],
                model="gpt-3.5-turbo-16k",
            ),
            tools=[
                    {
                        "type": "function",
                        "function": dict(ProceedToNextStep.openai_schema),
                    },
                    {
                        "type": "function",
                        "function": dict(EditCurrentSlide.openai_schema),
                    },
                    {
                        "type": "function",
                        "function": dict(DeleteCurrentSlide.openai_schema),
                    },
                    {
                        "type": "function",
                        "function": dict(AddSlideHere.openai_schema),
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
                    tool_result = await execute_tool(tool_call, [ProceedToNextStep, EditCurrentSlide, DeleteCurrentSlide, AddSlideHere])
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
        
        
                    
                    
