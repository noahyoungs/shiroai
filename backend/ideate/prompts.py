from global_prompts_config import interface_keys_for_interface
###########################

ideate_confirmation_message = {"role": "system", "content": "It looks like all the fields have been filled out. If you haven't already, ask the the user if they are satisfied with the Topic, Target Audience, and Goal of the presentation. If they are satisfied, call the `proceed` function tool to proceed to the next step. If they are not satisfied, continue to use the set function tools to adjust the Topic, Target Audience, and Goal until they are satisfied. DO NOT call the `proceed` function tool until the user has confirmed they are satisfied with the presentation."}

###########################

def capitalize_first_letter(word):
    if len(word) == 0:
        return word
    return word[0].upper() + word[1:]

    
def getInterfaceUpdateSystemMessage(interface, interfaceData):
    print(f"Getting system message for interface: {interface}")
    if len(interface_keys_for_interface[interface]) != len(interfaceData):
        raise ValueError(f"Interface data does not match interface values\n Interface: {interface_keys_for_interface[interface]}\nInterface Data: {interfaceData}")
    for key in interface_keys_for_interface[interface]:
        if key not in interfaceData:
            raise ValueError(f"Interface data missing key: {key}")
    content = "Here are the current parameters displayed to the user in the configuration screen. You must keep these parameters updated as the conversation progresses. Use the set_topic, set_audience, and set_goal function tools with JSON arguments to make sure these parameters are kept up with the conversation:\n"
    for key, value in interfaceData.items():
        if value == "":
            value = "<Empty>"
        capitalized_key = capitalize_first_letter(key)
        content += f"{capitalized_key}:\n{value}\n\n"
    message = {'role': 'system', 'content': content}
    # print(f"System message: {message}")
    return message

    
def getTools(fields, complete):
    function_objects = []
    
    for field in fields:
        key = field["key"]
        title = field["title"]
        description = field["description"]
        examples = field["examples"]
        field_type = field["type"]

        function_object = {
            "type": "function",
            "function": {
                "name": f"set_{key}",
                "description": f"Set the {title} of the presentation",
                "parameters": {
                    "type": "object",
                    "properties": {
                        key: {
                            "type": field_type,
                            "title": title,
                            "description": description,
                            "examples": examples,
                        }
                    },
                    "required": [key],
                },
            },
        }
        function_objects.append(function_object)
        
    research_agent_function_object = {
        "type": "function",
        "function": {
            "name": "ask_research_agent_a_question",
            "description": "Ask the research agent a question about anything the user mentions that you aren't familiar with.",
            "parameters": {
                "type": "object",
                "properties": {
                    "question": {
                        "type": "string",
                        "description": "The question you would like to ask the research agent",
                        "examples": ["Who is the current president of El Salvador?", "What is OpenAI's Sora Model?"],
                    },
                },
                "required": ["question"],
            }
        }
    }
    
    function_objects.append(research_agent_function_object)
        
    if complete:
        function_object = {
            "type": "function",
            "function": {
                "name": "proceed",
                "description": "Continue to the next step in the presentation creation process. Should only be caled after you have determined the user is satisfied with the parameters.",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": [],
                },
            },
        }
        function_objects.append(function_object)

    return function_objects
    
