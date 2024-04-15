import os
import asyncio
import json
import ideate.prompts as ideate_prompts
from openai import AsyncOpenAI
from ideate.config import interface_fields, get_interface_keys

client = AsyncOpenAI()

async def get_completion(messages, interface, interfaceData, updateInterface):
    messages.append(ideate_prompts.getCompletionSystemMessage(interface, interfaceData))
    completion = await client.chat.completions.create(
        messages=messages,
        model="gpt-3.5-turbo",
        tools=ideate_prompts.getTools(interface_fields[interface]),
    )

    # Tool Call Case
    if completion.choices[0].message.tool_calls:
        for tool_call in completion.choices[0].message.tool_calls:
            set_key = tool_call.function.name
            if set_key.startswith("set_"):
                key = set_key[4:]
            else:
                raise ValueError(f"Invalid tool call: {set_key}")
            if key not in get_interface_keys(interface):
                raise ValueError(f"Invalid key: {key}")
            value = json.loads(tool_call.function.arguments).get(key, "")
            interfaceData[key] = value
            await updateInterface(interfaceData)

            result = f"Success: Set {key} to {value}"
            messages.append({"role": "function", "tool_call_id": completion.choices[0].message.tool_calls[0].id, "name": completion.choices[0].message.tool_calls[0].function.name, "content": result})

            # Recursively call get_completion to get the next message
            return await get_completion(messages, interface, interfaceData, updateInterface)

    # Message Content Case
    elif completion.choices[0].message.content:
        simple_message = {"role": "assistant", "content": completion.choices[0].message.content}
        messages.append(simple_message)
        return messages, simple_message

    else:
        raise ValueError("No tools, no message content")