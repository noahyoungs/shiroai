
    
# def getTools(complete, searched):
#     function_objects = [
#         {
#             "type": "function",
#             "function": {
#                 "name": "add_source_by_url",
#                 "description": "Add a source by URL. Only use this if the user provides a URL",
#                 "parameters": {
#                     "type": "object",
#                     "properties": {
#                         "url": {
#                             "type": "string",
#                             "description": "The URL of the source",
#                             "format": "url",
#                             "examples": ["https://www.example.com"],
#                         }
#                     },
#                     "required": ["url"],
#                 },
#             },
#         },
#         {
#             "type": "function",
#             "function": {
#                 "name": "delete_source",
#                 "description": "Delete a source from the sources list. Only use this if the user wants to delete a source",
#                 "parameters": {
#                     "type": "object",
#                     "properties": {
#                         "id": {
#                             "type": "string",
#                             "description": "The ID of the source to delete",
#                             "examples": ["a1b2c3d4"],
#                         }
#                     },
#                     "required": ["id"],
#                 },
#             }
#         },
#         {
#             "type": "function",
#             "function": {
#                 "name": "web_search",
#                 "description": "Search the web for a source relevant to the presentation.",
#                 "parameters": {
#                     "type": "object",
#                     "properties": {
#                         "query": {
#                             "type": "string",
#                             "description": "An excellent search query consisting of a concise combination of specific, relevant, and important keywords closely related to the desired information while avoiding overly broad or general terms.",
#                             "examples": [
#                                 'artificial intelligence impact future work automation jobs',
#                                 'workplace mental health promotion strategies employee well-being',
#                                 'renewable energy role combating climate change sustainable future',
#                                 'effective time management techniques productivity tips strategies'
#                             ],
#                         },
#                     "required": ["query"],
#                     }
#                 },
#             },
#         },
#     ]
    
#     if searched:
#         function_objects.append({
#             "type": "function",
#             "function": {
#                 "name": "add_source_by_id",
#                 "description": "Add a source to the list of sources by ID found in the web search.",
#                 "parameters": {
#                     "type": "object",
#                     "properties": {
#                         "id": {
#                             "type": "string",
#                             "description": "The ID of the source to add",
#                             "examples": ["a1b2c3d4"],
#                         }
#                     },
#                     "required": ["id"],
#                 },
#             },
#         })
        
#     if complete:
#         function_object = {
#             "type": "function",
#             "function": {
#                 "name": "proceed_to_next_step",
#                 "description": "Continue to the next step in the presentation creation process",
#                 "parameters": {
#                     "type": "object",
#                     "properties": {},
#                     "required": [],
#                 },
#             },
#         }
#         function_objects.append(function_object)

#     return function_objects

def getCurrentSourceListMessage(interfaceData):
    if not isinstance(interfaceData['sources'], list):
        raise ValueError("Sources must be a list")

    string = "Here is the current list of sources:\nDO NOT REPEAT THIS LIST BACK TO THE USER because they can already see the list next to the chat interface.\n\n"
    if len(interfaceData.get('sources', [])) == 0:
        string += "<Empty>\n\n"
    for i, source in enumerate(interfaceData['sources']):
        
        string += f"Source {i + 1}:\n"
        string += f"ID: {str(source['id'])[:8]}\n"
        string += f"Name: {source.get('name', 'Unknown')}\n"
        if 'url' in source:
            string += f"URL: {source['url']}\n"
            
        if source['type'] == 'web':
            string += "Type: A source found on the web\n\n"
        else:
            string += f"Type: A {source['type']} file uploaded by the user\n\n"


    return {'role': 'system', 'content': string.strip()}
    
    