import json 

def remove_overlaps(strings):
    result = []
    prev_string = ""

    for string in strings:
        if not prev_string:
            result.append(string)
        else:
            overlap = find_overlap(prev_string, string)
            if overlap:
                result.append(string[overlap:])
            else:
                result.append(string)
        prev_string = string

    return result

def find_overlap(str1, str2):
    for i in range(min(len(str1), len(str2)), 0, -1):
        if str1.endswith(str2[:i]):
            return i
    return 0

def format_documents(documents, paragraph_delimiter="\n\n", remove_overlap=False):
    output = ""
    sources = {}

    for doc in documents:
        if type(doc) is not dict:
            doc = dict(doc)
        source_title = doc['metadata']['source']['title']
        source_url = doc['metadata']['source']['url']
        if source_title not in sources:
            sources[source_title] = {
                'url': source_url,
                'paragraphs': []
            }
        paragraph = {
            'headings': doc['metadata']['headers'],
            'content': doc['page_content']
        }
        sources[source_title]['paragraphs'].append(paragraph)

    for source_title, source_data in sources.items():
        output += f"#### Source: {source_title}\n"
        output += f"URL: {source_data['url']}\n\n"
        current_headings = ""

        if remove_overlap:
            # Remove overlapping parts from the page_content
            content_list = [p['content'] for p in source_data['paragraphs']]
            content_list = remove_overlaps(content_list)

            for i, paragraph in enumerate(source_data['paragraphs']):
                headings = " > ".join([h for _, h in sorted(paragraph['headings'].items())])
                if headings != current_headings:
                    current_headings = headings
                    if current_headings:
                        output += f"###### Section: {current_headings}\n\n"
                output += content_list[i].strip() + paragraph_delimiter
        else:
            # Print the page contents as is
            for paragraph in source_data['paragraphs']:
                headings = " > ".join([h for _, h in sorted(paragraph['headings'].items())])
                if headings != current_headings:
                    current_headings = headings
                    if current_headings:
                        output += f"###### Section: {current_headings}\n\n"
                output += paragraph['content'].strip() + paragraph_delimiter

    return output.strip()


def format_topic(documents, paragraph_delimiter="\n\n", print_probability=False):
    output = ""
    sources = {}

    for document in documents:
        if type(document) is not dict:
            # print(type(document))
            doc = dict(document)
        else:
            doc = document
        doc_topic = doc['metadata'].get('topic')
        if doc_topic:
            topic_probability = doc_topic.get('probability')
        else:
            topic_probability = None
        
        source_title = doc['metadata']['source']['title']
        source_url = doc['metadata']['source']['url']
        if source_title not in sources:
            sources[source_title] = {
                'url': source_url,
                'paragraphs': []
            }
        
        paragraph = {
            'headings': doc['metadata']['headers'],
            'content': doc['page_content'],
            'probability': topic_probability
        }
        sources[source_title]['paragraphs'].append(paragraph)

    for source_title, source_data in sources.items():
        output += f"#### Source: {source_title}\n"
        output += f"URL: {source_data['url']}\n\n"
        current_headings = None
        
        # Remove overlapping parts from the page_content
        content_list = [p['content'] for p in source_data['paragraphs']]
        content_list = remove_overlaps(content_list)
        
        for i, paragraph in enumerate(source_data['paragraphs']):
            headings = " > ".join([h for _, h in sorted(paragraph['headings'].items()) if h is not None])
            
            if headings != current_headings:
                current_headings = headings
                if current_headings:
                    output += f"_from: {current_headings}_\n" # Headings
                else:
                    output += "_from: top level_\n" # Top level
            
            if print_probability and paragraph['probability'] is not None:
                if paragraph['probability'] < 0.7:
                    output += f"_Possibly tangential:_ "
                
            output += content_list[i].strip() + paragraph_delimiter

    return output.strip()


def format_topic(documents, paragraph_delimiter="\n\n"):
    output = ""
    sources = {}

    for document in documents:
        if type(document) is not dict:
            # print(type(document))
            doc = dict(document)
        else:
            doc = document
        
        source_title = doc['metadata']['source']['title']
        source_url = doc['metadata']['source']['url']
        if source_title not in sources:
            sources[source_title] = {
                'url': source_url,
                'paragraphs': []
            }
        
        paragraph = {
            'headings': doc['metadata']['headers'],
            'content': doc['page_content'],
        }
        sources[source_title]['paragraphs'].append(paragraph)

    for source_title, source_data in sources.items():
        output += f"#### Source: {source_title}\n"
        output += f"URL: {source_data['url']}\n\n"
        current_headings = None
        
        # Remove overlapping parts from the page_content
        content_list = [p['content'] for p in source_data['paragraphs']]
        content_list = remove_overlaps(content_list)
        
        for i, paragraph in enumerate(source_data['paragraphs']):
            headings = " > ".join([h for _, h in sorted(paragraph['headings'].items()) if h is not None])
            
            if headings != current_headings:
                current_headings = headings
                if current_headings:
                    output += f"_from: {current_headings}_\n" # Headings
                else:
                    output += "_from: top level_\n" # Top level
                
            output += content_list[i].strip() + paragraph_delimiter

    return output.strip()


def format_topic_xml(documents, show_sources=True, show_excerpt_ids=True):
    output = ""
    sources = {}
    
    if not documents:
        raise ValueError("No documents provided.")

    for document in documents:
        if type(document) is not dict:
            # print(type(document))
            doc = dict(document)
        else:
            doc = document
        
        source_title = doc['metadata']['source']['title']
        source_url = doc['metadata']['source']['url']
        if source_title not in sources:
            sources[source_title] = {
                'url': source_url,
                'paragraphs': []
            }
        
        paragraph = {
            'headings': doc['metadata']['headers'],
            'content': doc['page_content'],
            'id': doc['metadata']['document_id']
        }
        sources[source_title]['paragraphs'].append(paragraph)

    for source_title, source_data in sources.items():
        if show_sources:
            output += "<source>\n"
            output += f"<source_title>{source_title}</source_title>\n"
            # output += f"<source_url>{source_data['url']}</source_url>\n"
        
        # Remove overlapping parts from the page_content
        content_list = [p['content'] for p in source_data['paragraphs']]
        content_list = remove_overlaps(content_list)
        
        for i, paragraph in enumerate(source_data['paragraphs']):
            output += "\n<excerpt>"
            if show_excerpt_ids:
                output += f"\n<excerpt_id>{paragraph['id'][-8:]}</excerpt_id>"
            headings = " > ".join([h for _, h in sorted(paragraph['headings'].items()) if h is not None])
            if headings:
                output += f"\n<excerpt_headings>{headings}</excerpt_headings>" # Headings
            output += "\n<excerpt_content>\n"
            output += content_list[i].strip()
            output += "\n</excerpt_content>"
            output += "\n</excerpt>\n"
        if show_sources:
            output += "\n</source>\n\n"

    return output.strip()
    
        