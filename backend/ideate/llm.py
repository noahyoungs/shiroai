import os
import asyncio
import json
import ideate.prompts as ideate_prompts
from ideate.config import interface_fields, get_interface_keys
from init_llm import client

async def get_completion(
    messages,
    interface,
    interfaceData,
    updateInterface,
    user=None,
    presentationID=None,
    memory=None,
    ):
    
    
    # print(f"User: {user}")
    metadata = {
        "interface": interface,
        "feature": "chat",
    }
    if presentationID is not None:
        metadata["presentationID"] = presentationID
    
    # Check if all interface fields are truthy
    complete = all(interfaceData.values())
    
    if complete:
        if not memory.get("ideate_confirmation_message_sent", False):
            messages.append(ideate_prompts.ideate_confirmation_message)
            memory["ideate_confirmation_message_sent"] = True
    
    messages.append(ideate_prompts.getInterfaceUpdateSystemMessage(interface, interfaceData))
        
    completion = await client.chat.completions.create(
        messages=messages,
        model="gpt-3.5-turbo",
        tools=ideate_prompts.getTools(interface_fields[interface], complete),
        user=user,
    )
    # Tool Call Case
    if completion.choices[0].message.tool_calls:
        for tool_call in completion.choices[0].message.tool_calls:
            tool_call_name = tool_call.function.name
            if tool_call_name.startswith("set_"):
                key = tool_call_name[4:]
            elif tool_call_name == "proceed":
                proceed_message = {"role": "assistant", "content": "Proceeding to the next step..."}
                messages.append(proceed_message)
                return messages, proceed_message, True
            else:
                raise ValueError(f"Invalid tool call: {tool_call_name}")
            if key not in get_interface_keys(interface):
                raise ValueError(f"Invalid key: {key}")
            value = json.loads(tool_call.function.arguments).get(key, "")
            interfaceData[key] = value
            await updateInterface(interfaceData)

            result = f"Success: Set {key} to `{value}`"
            messages.append({"role": "function", "tool_call_id": completion.choices[0].message.tool_calls[0].id, "name": completion.choices[0].message.tool_calls[0].function.name, "content": result})

            # Recursively call get_completion to get the next message
            return await get_completion(
                messages,
                interface,
                interfaceData,
                updateInterface,
                user=user,
                presentationID=presentationID,
                memory=memory,
                )

    # Message Content Case
    elif completion.choices[0].message.content:
        simple_message = {"role": "assistant", "content": completion.choices[0].message.content}
        messages.append(simple_message)
        return messages, simple_message, False

    else:
        raise ValueError("No tools, no message content")