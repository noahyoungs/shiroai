from slides.format import format_topic_xml

def get_excerpt_ids(reduced_docs):
    excerpt_ids = [doc['metadata']['document_id'] for doc in reduced_docs]
    return excerpt_ids

def get_id_from_suffix(excerpt_ids, suffix):
    return next((id for id in excerpt_ids if id.endswith(suffix)), None)

def get_presentation_xml(presentation_topic, presentation_audience, presentation_goal):
    return f"""<presentation>
    <topic>{presentation_topic}</topic>
    <audience>{presentation_audience}</audience>
    <goal>{presentation_goal}</goal>
</presentation>"""

def get_subtopic_xml(subtopic_name):
    return f"""<subtopic>{subtopic_name}</subtopic>"""

def get_research_xml(reduced_docs):
    return f"<research>\n{format_topic_xml(reduced_docs, show_sources=False, show_excerpt_ids=True)}\n</research>"