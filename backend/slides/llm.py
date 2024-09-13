from instructor import OpenAISchema
from pydantic import BaseModel
from llm_clients import chat_client
import tokentrim as tt
from slides.edit_slide_content import edit_slide_content
from slides.images.edit_slide_image import edit_slide_image
from database_models import Slide
from slides.persistent_slide_list import PersistentSlideList
import copy
import traceback
import os


slide_type_descriptions = {
    'short_bullets_slide': 'Icon Node Slide (This slide type has a title and 2-5 nodes, each with an icon and a short text description (<=80 chars). The nodes can be arranged in a list or a grid, and arrows can be displayed between the nodes to indicate sequentiality. The layout and arrangement of the title and nodes are determined by the content and number of nodes.)',
    'markdown_slide': 'Markdown Slide (A slide with a title and markdown content. The title is displayed above the markdown content. The markdown content typically includes either headings and bullet points or a table. Images are not supported. Icons are not supported, but emojis can be used.)',
    'section_header_slide': 'Section Header Slide (A slide with a section title and an image. The image can be positioned on the left or right side of the slide.)',
    'presentation_title_slide': 'Presentation Title Slide (A slide with the presentation title and an image. The image is displayed as the background of the entire slide, and the title is overlaid on top of it.)',
    'simple_mermaid_slide': 'Mermaid Diagram Slide (A slide with a title and a mermaid diagram. The title is displayed right above the mermaid diagram.)',
}

def slide_to_text(current_slide: Slide):
    slide_content_string = ""
    
    if current_slide.slide_type == 'short_bullets_slide':
        slide_content_string = "\n".join([f"Icon: {item.icon.name if item.icon and item.icon.name else 'Icon'}, Text: {item.content}" for item in current_slide.slide_content])
        slide_content_string = f"Slide Content:\n{slide_content_string}"
    elif current_slide.slide_type == 'markdown_slide':
        slide_content_string = current_slide.slide_content['content']
        slide_content_string = f"Slide Content:\n{slide_content_string}"
    elif current_slide.slide_type == 'simple_mermaid_slide':
        slide_content_string = current_slide.slide_content['mermaid_code']
        slide_content_string = f"Slide Content:\nA mermaid diagram with the following code is rendered for the user:\n{slide_content_string}"
    elif current_slide.slide_type in ['section_header_slide', 'presentation_title_slide']:
        slide_content_string = f"Slide Image: An image containing `{current_slide.image.prompt}` is displayed on the slide."
    
    prompt = f"""\
Slide Type: {slide_type_descriptions.get(current_slide.slide_type, 'Unknown Slide Type')}
Slide Title: {current_slide.slide_title}
{slide_content_string}

IMPORTANT NOTE: You never should read this information back to the user because the user can already see the current slide on their screen. This information is only for your reference.
"""
    return prompt

async def get_current_slide_message(current_slide: Slide):
    if current_slide.hidden:
        return {'role': 'system', 'content': f"The slide the user was looking at was deleted."}
    return {'role': 'system', 'content': f"Here's the slide the user is currently looking at:\n{slide_to_text(current_slide)}"}


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
    

async def complete(presentation_id, messages, emitter, memory, interface_data, max_turns=5):
    print(f"Completing slides interface message, slide id: {interface_data['current_slide_id']}")
    
    slide_list: PersistentSlideList = memory['slide_list']
    current_slide_id = interface_data['current_slide_id']
    current_slide: Slide = await slide_list.get_slide(current_slide_id)
    
    print(f"Current Slide Title: {current_slide.slide_title}")
    
    current_turn = 0
    new_messages = []
    
    async def new_turn(presentation_id, messages, interface_data, current_turn, max_turns=5, emitter=None, memory=None):
    
        class ProceedToNextStepException(Exception):
            pass
            
        # classes for the function tools
        class ProceedToNextStep(OpenAISchema):
            """Continue to the next step in the presentation creation process. Only call this function tool after you ask the user if they are satisfied with the current list of sources and they confirm that they are."""
        
            async def run(self):
                return True
            
            async def post_run(self, output):
                raise ProceedToNextStepException()
            
        class EditCurrentSlideTitle(OpenAISchema):
            """Directly edit only the title of the current slide."""
            new_slide_title: str
            
            async def run(self):
                nonlocal current_slide
                await slide_list.update_slides([{'id': current_slide_id, 'slide_title': self.new_slide_title}], wait_for_db=True)
                return f"Success, New Slide Title: {self.new_slide_title}"
            
            
        class InvokeContentEditorAgent(OpenAISchema):
            """Send an instruction to the Content Editor Agent to edit the current slide content."""
            edit_instructions: str
            
            async def run(self):
                nonlocal current_slide
                try:
                    # edit the current slide
                    current_slide, message = await edit_slide_content(presentation_id, copy.deepcopy(current_slide), slide_list.update_slides, self.edit_instructions)
                    # add agent message to messages
                    messages.append({'role': 'meta_content_editor', 'content': message})
                    # emit agent message
                    await emitter('message', {'role': 'meta_content_editor', 'content': message})
                    return f"Success! Message from Content Editor Agent: {message}"
                except Exception as e:
                    traceback.print_exc()
                    return f"Error with Content Editor Agent: {str(e)}"
            
                
        class InvokeImageEditorAgent(OpenAISchema):
            """Send an instruction to the Image Editor Agent to edit the current slide image."""
            edit_instructions: str
            
            async def run(self):
                nonlocal current_slide
                try:
                    # edit the current slide
                    current_slide, message = await edit_slide_image(presentation_id, copy.deepcopy(current_slide), slide_list.update_slides, self.edit_instructions)
                    # add agent message to messages
                    messages.append({'role': 'meta_image_editor', 'content': message})
                    # emit agent message
                    await emitter('message', {'role': 'meta_image_editor', 'content': message})
                    return f"Success! Message from Image Editor Agent: {message}"
                except Exception as e:
                    traceback.print_exc()
                    return f"Error with Image Editor Agent: {str(e)}"
            
                        
        class DeleteEntireSlide(OpenAISchema):
            """Deletes the ENTIRE current slide."""
            
            async def run(self):
                nonlocal current_slide
                old_title = current_slide.slide_title
                await slide_list.hide_slide(current_slide_id, True)
                interface_data['current_slide_id'] = current_slide.previous
                await emitter('interface_update', {'current_slide_id': current_slide.previous})
                return f"Success, the slide titled `{old_title}` was deleted."
            
        
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
                return error_message

            output = None
            try:
                # func becomes instance of class created with arguments from model
                func = func(**eval(tool_call.function.arguments))
                # get outputs from the run function
                output = await func.run()
            except Exception as e:
                # model error
                 # Print the stack trace
                traceback.print_exc()
                
                return f"Error: {str(e)}"

            # Run post_run() method after the try block
            if func is not None and hasattr(func, 'post_run'):
                output = await func.post_run(output)

            return output # tool result
        
        # Update the model on the current slide
        messages.append( await get_current_slide_message(current_slide))
        
        base_tools = [
                    {
                        "type": "function",
                        "function": dict(EditCurrentSlideTitle.openai_schema),
                    },
                    {
                        "type": "function",
                        "function": dict(DeleteEntireSlide.openai_schema),
                    }
                ]
        
        image_tools = [
                    {
                        "type": "function",
                        "function": dict(InvokeImageEditorAgent.openai_schema),
                    },
                ]
        
        content_tools = [
                    {
                        "type": "function",
                        "function": dict(InvokeContentEditorAgent.openai_schema),
                    },
                ]
        
        tools = base_tools + (image_tools if current_slide.slide_type in ['section_header_slide', 'presentation_title_slide'] else content_tools)
        
        completion = await chat_client.chat.completions.create(
            model=os.getenv("SLIDES_CHAT_MODEL_OPENAI_ID"),
            # filter out any messages with roles that start with meta
            # reduce messages to 16k tokens
            messages=tt.trim(
                messages=[message for message in messages if not message["role"].startswith("meta")],
                model="gpt-3.5-turbo-16k",
            ),
            tools=tools,
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
                    tool_result = await execute_tool(tool_call, [EditCurrentSlideTitle, InvokeContentEditorAgent, InvokeImageEditorAgent, DeleteEntireSlide, ProceedToNextStep])
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
            return await new_turn(presentation_id, messages, interface_data, current_turn + 1, max_turns, emitter=emitter, memory=memory)
        else:
            if not completion.choices[0].message.content:
                raise Exception("No message content found in completion and no tool calls either.")
            responseMessage = {'role':'assistant', 'content': completion.choices[0].message.content}
            new_messages.append(responseMessage)
            messages.append(responseMessage)
            return messages, new_messages, False
        
    return await new_turn(presentation_id, messages, interface_data, current_turn, max_turns, emitter=emitter, memory=memory)
        
        
                    
                    
