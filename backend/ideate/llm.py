import os
import asyncio
import json
import ideate.prompts as ideate_prompts
from ideate.config import interface_fields, get_interface_keys
from init_llm import client, groq_client, perplexity_client
from portkey_ai import AsyncPortkey
import traceback
import tokentrim as tt
# from dotenv import load_dotenv
import os

# load_dotenv()

async def ask_perplexity(question):
    response = await perplexity_client.chat.completions.create(
                            messages= [{ "role": 'user', "content": f"{question} Keep your answer short. No longer than a short paragraph."}],
                            model= 'llama-3.1-sonar-small-128k-online',
                            
                        )
    # print(f"Perplexity Response: {response.choices[0].message.content}")
    answer = response.choices[0].message.content
    return answer
                        
                        
async def get_completion(
    messages,
    interface,
    interfaceData,
    updateInterface,
    user=None,
    presentationID=None,
    memory=None,
    newMessages=[],
    ):
    newMessages=newMessages.copy()
    
    # print(f"User: {user}")
    metadata = {
        "interface": interface,
        "feature": "chat",
    }
    if presentationID is not None:
        metadata["presentationID"] = presentationID
    
    # Check if all interface fields are truthy
    complete = all(interfaceData.values())

    messages.append(ideate_prompts.getInterfaceUpdateSystemMessage(interface, interfaceData))
    
    if complete:
        if not memory.get("ideate_confirmation_message_sent", False):
            messages.append(ideate_prompts.ideate_confirmation_message)
            memory["ideate_confirmation_message_sent"] = True
    else:
        attributes_not_set = [key for key, value in interfaceData.items() if not value]
        messages.append({"role":"system", "content": f"You still need to set the following attributes: {', '.join(attributes_not_set)}"})
        
    # openai
    completion = await client.chat.completions.create(
        # filter out messages where role starts with "meta"
        messages=tt.trim(
            messages=[message for message in messages if not message["role"].startswith("meta")],
            model="gpt-3.5-turbo-16k",
            ),
        model=os.getenv("CHAT_MODEL_OPENAI_ID"),
        tools=ideate_prompts.getTools(interface_fields[interface], complete),
        tool_choice='auto',
        user=user,
    )
    
    # # llama 3 8b 
    # completion = await groq_client.chat.completions.create(
    #     # filter out messages where role starts with "meta"
    #     messages=tt.trim(
    #         messages=[message for message in messages if not message["role"].startswith("meta")],
    #         model="gpt-4",
    #         ),
    #     model="llama3-8b-8192",
    #     tools=ideate_prompts.getTools(interface_fields[interface], complete),
    #     user=user,
    # )
    
    # Tool Call Case
    key = None
    
    if completion.choices[0].message.tool_calls:
        for tool_call in completion.choices[0].message.tool_calls:
            tool_call_name = tool_call.function.name
            if tool_call_name.startswith("set_"):
                key = tool_call_name[4:]
            elif tool_call_name == "proceed":
                proceed_message = {"role": "assistant", "content": "Proceeding to the next step..."}
                messages.append(proceed_message)
                return messages, [proceed_message], True
            elif tool_call_name == "ask_research_agent_a_question":
                try:
                    question = json.loads(tool_call.function.arguments).get("question", None)
                    try:
                        answer = await ask_perplexity(question)
                        result = f"Research Agent Answer: {answer}"
                        
                    except Exception as e:
                        result = f"Error communicating with Research Agent: {e}"
                        # print stack trace
                        traceback.print_exc()
                    if not question:
                        raise ValueError("No question provided")
                except Exception as e:
                    result = f"Error: {e}"
                messages.append({"role": "meta_research_agent", "content": answer})
                newMessages.append({"role": "meta_research_agent", "content": answer})
                messages.append({"role": "function", "tool_call_id": tool_call.id, "name": tool_call.function.name, "content": result})
            else:
                raise ValueError(f"Invalid tool call: {tool_call_name}")
            
            if key:
                if key not in get_interface_keys(interface):
                    raise ValueError(f"Invalid key: {key}")
                value = json.loads(tool_call.function.arguments).get(key, "")
                interfaceData[key] = value
                await updateInterface(interfaceData)

                result = f"Success: Set {key} to `{value}`"
                messages.append({"role": "function", "tool_call_id": completion.choices[0].message.tool_calls[0].id, "name": completion.choices[0].message.tool_calls[0].function.name, "content": result})

            # Recursively call get_completion to get the next message
            messages, newMessages, complete = await get_completion(
                messages,
                interface,
                interfaceData,
                updateInterface,
                user=user,
                presentationID=presentationID,
                memory=memory,
                newMessages=newMessages,
            )
            
        return messages, newMessages, complete

    # Message Content Case
    elif completion.choices[0].message.content:
        simple_message = {"role": "assistant", "content": completion.choices[0].message.content}
        messages.append(simple_message)
        newMessages.append(simple_message)
        print("New Messages: ", newMessages)
        return messages, newMessages, False

    else:
        raise ValueError("No tools, no message content")

# async def test():
#     print(await ask_perplexity("What is the capital of France?"))
    
# if __name__ == "__main__":
#     asyncio.run(test())