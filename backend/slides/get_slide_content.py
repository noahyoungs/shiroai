from dotenv import load_dotenv
from langchain.docstore.document import Document
from s3 import download_model_list_from_s3
from dynamodb import get_presentation, batch_update_slides, delete_all_slides, update_presentation
import json
import asyncio
import re
from portkey_ai import AsyncPortkey
from uuid_extensions import uuid7str
from slides.format import format_topic_xml
from slides.reduce_topic_research import reduce_docs
from dotenv import load_dotenv
import os
import sys
from slides.generate_image import generate_image

load_dotenv()

bedrock_client = AsyncPortkey(
    virtual_key="aldeo-portkey-b-5cf75f",
    config={"cache": {"mode": "simple"}},
)


def get_excerpt_ids(reduced_docs):
    excerpt_ids = [doc['metadata']['id'] for doc in reduced_docs]
    return excerpt_ids


def get_id_from_suffix(excerpt_ids, suffix):
    return next((id for id in excerpt_ids if id.endswith(suffix)), None)


def get_presentation_xml(presentation_topic, presentation_audience, presentation_goal):
    return f"""<presentation>
    <topic>{presentation_topic}</topic>
    <audience>{presentation_audience}</audience>
    <goal>{presentation_goal}</goal>
</presentation>"""


async def get_slide_ideas(presentation_topic, presentation_audience, presentation_goal, subtopic_name, reduced_docs):
    slide_ideas_prompt = f"""
I'm creating the presentation described below:
{get_presentation_xml(presentation_topic, presentation_audience, presentation_goal)}

I'm working on a section about <subtopic>{subtopic_name}</subtopic> and I need some ideas for slides. Here's the research I've done for the section:
<research>
{format_topic_xml(reduced_docs, show_sources=False, show_excerpt_ids=False)}
</research>

Carefully read my research and devise a plan to create 1-4 powerpoint slides for the <subtopic></subtopic>. Here are the allowed slide types:

short_bullets_slide: 2-4 short unnested bullet points (max ~10 words per bullet)
long_bullets_slide: allows for more bullet points, longer bullet points, and nesting bullet points
markdown_table_slide: any table that can be written in markdown and fits reasonably on a slide
simple_mermaid_slide: a simple flow chart or diagram that can be expressed in mermaid, maximum 6 nodes.

Don't actually create the slide content in your plan. Instead, give me a list of <slide></slide>, each with a <slide_type></slide_type>, <slide_title></slide_title> and a concise but detailed <slide_content_idea></slide_content_idea in sentences of what information could be included in the slide.
Do not create an Introduction or Conclusion slide.
Make sure you consider not just the <subtopic></subtopic>, but also the <topic></topic>, the <audience></audience> and the <goal></goal> of the <presentation></presentation> I mentioned earlier when creating the slides."""

    response = await bedrock_client.chat.completions.create(
        model="anthropic.claude-3-haiku-20240307-v1:0",
        messages=[{"role": "user", "content": slide_ideas_prompt}],
        temperature=0,
        max_tokens=1500,
    )
    response_text = response.choices[0].message.content.strip()

    def parse_slides(input_string):
        slides = []
        slide_pattern = re.compile(r'<slide>(.*?)</slide>', re.DOTALL)
        slide_matches = slide_pattern.findall(input_string)

        for slide_match in slide_matches:
            slide_dict = {}

            slide_type_pattern = re.compile(r'<slide_type>(.*?)</slide_type>')
            slide_type_match = slide_type_pattern.search(slide_match)
            if slide_type_match:
                slide_dict['slide_type'] = slide_type_match.group(1)

            slide_title_pattern = re.compile(
                r'<slide_title>(.*?)</slide_title>')
            slide_title_match = slide_title_pattern.search(slide_match)
            if slide_title_match:
                slide_dict['slide_title'] = slide_title_match.group(1)

            slide_content_idea_pattern = re.compile(
                r'<slide_content_idea>(.*?)</slide_content_idea>', re.DOTALL)
            slide_content_idea_match = slide_content_idea_pattern.search(
                slide_match)
            if slide_content_idea_match:
                content_idea = slide_content_idea_match.group(1).strip()
                slide_dict['slide_content_idea'] = content_idea

            slides.append(slide_dict)

        return slides

    return parse_slides(response_text)


def get_short_bullets_slide_prompt(presentation_xml, research_xml, subtopic_name, slide_title, slide_content_idea, excerpt_ids):
    return f"""
I'm creating the presentation described below:
{presentation_xml}

Here's the subtopic for the section I'm working on right now:
<subtopic>{subtopic_name}</subtopic>

Here's the research I have for the <subtopic></subtopic>:
<research>
{research_xml}
</research>

Within the <subtopic></subtopic>, I'm working on a slide called <slide_title>{slide_title}</slide_title>.
I need you to create 1-5 short bullet points to go on this slide. Each bullet point should be less than 10 words long and the bullet points cannot be nested.

Here's an idea for the slide content, to get you started:
<slide_content_idea>{slide_content_idea}</slide_content_idea>
You don't have to follow this idea exactly, but it should give you a sense of what I'm looking for.
You may only use the research I've provided to create the bullet points. Never include your background knowledge or other research.
You must include the <source_excerpt_id></source_excerpt_id> of the excerpt from the research above that supports the bullet point.

Give me the bullet points in the following XML format:
<bullet_points>
<bullet_point>
<content>The content of the bullet point</content>
<source_excerpt_id>a1b2c3d4</source_excerpt_id>
</bullet_point>
...
</bullet_points>

Finally, tell me whether or not the bullet points have a sequential order, like steps in a process or a timeline.
If they do, provide the order in the following XML format:
<sequential_order>yes</sequential_order>
If they do not, provide the following XML format:
<sequential_order>no</sequential_order>

Make sure you consider not just the <slide_title></slide_title>, but also the <subtopic></subtopic>, and the <topic></topic>, <audience></audience> and <goal></goal> of the <presentation></presentation> I mentioned earlier when creating the bullet points.
Remember you must cite an excerpt id as a source for every bullet point, so you can only use information found in my research."""


async def get_short_bullets_slide(presentation_topic, presentation_audience, presentation_goal, subtopic_name, reduced_docs, slide_idea, excerpt_ids):
    response = await bedrock_client.chat.completions.create(
        model="anthropic.claude-3-haiku-20240307-v1:0",
        messages=[{"role": "user", "content": get_short_bullets_slide_prompt(
            get_presentation_xml(presentation_topic, presentation_audience, presentation_goal),
            format_topic_xml(reduced_docs, show_sources=False,
                             show_excerpt_ids=True),
            subtopic_name,
            slide_idea['slide_title'],
            slide_idea['slide_content_idea'],
            excerpt_ids)}],
        temperature=0,
        max_tokens=1500,
        stop=["</sequential_order>"],
    )
    response_text = response.choices[0].message.content.strip(
    ) + "</sequential_order>"

    def parse_bullet_points(input_string, excerpt_ids):
        bullet_points = []
        sequential = False

        pattern = r'<bullet_points>(.*?)</bullet_points>'
        match = re.search(pattern, input_string, re.DOTALL)

        if match:
            xml_string = match.group(1)

            bullet_point_pattern = r'<bullet_point>(.*?)</bullet_point>'
            bullet_point_matches = re.findall(
                bullet_point_pattern, xml_string, re.DOTALL)

            for bullet_point_match in bullet_point_matches:
                content_pattern = r'<content>(.*?)</content>'
                source_excerpt_id_pattern = r'<source_excerpt_id>(.*?)</source_excerpt_id>'

                content_match = re.search(
                    content_pattern, bullet_point_match, re.DOTALL)
                source_excerpt_id_match = re.search(
                    source_excerpt_id_pattern, bullet_point_match, re.DOTALL)

                if content_match and source_excerpt_id_match:
                    content = content_match.group(1).strip()
                    source_excerpt_id_suffix = source_excerpt_id_match.group(
                        1).strip()
                    
                    # get excerpt id
                    source_excerpt_id = get_id_from_suffix(
                        excerpt_ids, source_excerpt_id_suffix)
                    
                    # get excerpt text
                    source_excerpt = next((doc['page_content'] for doc in reduced_docs if doc['metadata']['id'] == source_excerpt_id), None)
                    # get source id
                    source_id = next((doc['metadata']['source']['id'] for doc in reduced_docs if doc['metadata']['id'] == source_excerpt_id), None)

                    bullet_points.append({
                        'content': content,
                        'excerpt': {
                            'source_id': source_id,
                            'excerpt_id': source_excerpt_id,
                            'text': source_excerpt
                        }
                    })

            sequential_order_pattern = r'<sequential_order>(.*?)</sequential_order>'
            sequential_order_match = re.search(
                sequential_order_pattern, input_string, re.DOTALL)

            if sequential_order_match:
                sequential_order = sequential_order_match.group(
                    1).strip().lower()
                if sequential_order == 'yes':
                    sequential = True

        return bullet_points, sequential

    bullet_points, sequential = parse_bullet_points(response_text, excerpt_ids)
    return {
        'slide_title': slide_idea['slide_title'],
        'slide_type': 'short_bullets_slide',
        'slide_content': bullet_points,
        'sequential': sequential
    }


def get_long_bullet_points_slide_prompt(presentation_xml, research_xml, subtopic_name, slide_title, slide_content_idea, excerpt_ids):
    return f"""
I'm creating the presentation described below:
{presentation_xml}

Here's the subtopic for the section I'm working on right now:
<subtopic>{subtopic_name}</subtopic>

Here's the research I have for the <subtopic></subtopic>:
<research>
{research_xml}
</research>

Within the <subtopic></subtopic>, I'm working on a slide called <slide_title>{slide_title}</slide_title>.
I need you to create the bullet point content for this slide. 

Here's an idea for the slide content, to get you started:
<slide_content_idea>{slide_content_idea}</slide_content_idea>
You don't have to follow this idea exactly, but it should give you a sense of what I'm looking for.
You may only use the research I've provided to create the bullet points. Never include your background knowledge or other research.
For each bullet point you include, you must use a footnote to cite the <excerpt_id></excerpt_id> of the excerpt from the research above that supports the bullet point.

Use markdown to format the bullet points. You can use numbered and unnumbered lists, and you should nest lists whenever possible. You should also use other markdown conventions like bold and italics when appropriate. Separate the bullet points and the footnotes with a horizontal rule (---).

Give me the bullet point content in markdown, with footnotes enclosed in a <content></content> tag, like this:
<content>
- The content of the bullet point[^1]
    - The content of another bullet point[^2]

---
[^1]: <excerpt_id>a1b2c3d4</excerpt_id>
[^2]: <excerpt_id>e5f6g7h8</excerpt_id>
</content>

Make sure you consider not just the <slide_title></slide_title>, but also the <subtopic></subtopic>, and the <topic></topic>, <audience></audience> and <goal></goal> of the <presentation></presentation> I mentioned earlier when creating the bullet points.
Remember you must cite an excerpt id as a source for every bullet point, so you can only use information found in my research."""


async def get_long_bullets_slide(presentation_topic, presentation_audience, presentation_goal, subtopic_name, reduced_docs, slide_idea, excerpt_ids):
    response = await bedrock_client.chat.completions.create(
        model="anthropic.claude-3-haiku-20240307-v1:0",
        messages=[{"role": "user", "content": get_long_bullet_points_slide_prompt(
            get_presentation_xml(presentation_topic, presentation_audience, presentation_goal),
            format_topic_xml(reduced_docs, show_sources=False,
                             show_excerpt_ids=True),
            subtopic_name,
            slide_idea['slide_title'],
            slide_idea['slide_content_idea'],
            excerpt_ids)}],
        temperature=0,
        max_tokens=1500,
        stop=["</content>"],
    )
    response_text = response.choices[0].message.content.strip(
    ) + "\n</content>"

    def parse_content_and_footnotes(input_string, excerpt_ids):
        content_pattern = r'<content>\s*(.*?)(?:---|\*\*\*|\+\+\+|===|___)\s*'
        content_match = re.search(content_pattern, input_string, re.DOTALL)
        content = content_match.group(1).strip() if content_match else ''

        footnote_pattern = r'\[\^(\d+)\]:\s*<excerpt_id>(\w+)</excerpt_id>'
        footnote_matches = re.findall(footnote_pattern, input_string)

        footnote_excerpt_ids = {num: get_id_from_suffix(
            excerpt_ids, excerpt_id) for num, excerpt_id in footnote_matches}
        
        footnotes = {}
        for num, excerpt_id in footnote_excerpt_ids.items():
            # get excerpt text
            source_excerpt = next((doc['page_content'] for doc in reduced_docs if doc['metadata']['id'] == excerpt_id), None)
            # get source id
            source_id = next((doc['metadata']['source']['id'] for doc in reduced_docs if doc['metadata']['id'] == excerpt_id), None)
            footnotes[num] = {
                'excerpt_id': excerpt_id,
                'source_id': source_id,
                'text': source_excerpt
            }
            
        return {
            'content': content,
            'footnotes': footnotes
        }

    parsed_content_and_footnotes = parse_content_and_footnotes(
        response_text, excerpt_ids)
    return {
        'slide_title': slide_idea['slide_title'],
        'slide_type': 'long_bullets_slide',
        'slide_content': parsed_content_and_footnotes
    }


def get_markdown_table_slide_prompt(presentation_xml, research_xml, subtopic_name, slide_title, slide_content_idea, excerpt_ids):
    return f"""
I'm creating the presentation described below:
{presentation_xml}

Here's the subtopic for the section I'm working on right now:
<subtopic>{subtopic_name}</subtopic>

Here's the research I have for the <subtopic></subtopic>:
<research>
{research_xml}
</research>

Within the <subtopic></subtopic>, I'm working on a slide called <slide_title>{slide_title}</slide_title>.
I need you to create a markdown table for this slide.

Here's an idea for the slide content, to get you started:
<slide_content_idea>{slide_content_idea}</slide_content_idea>

You don't have to follow this idea exactly, but it should give you a sense of what I'm looking for.

You may only use the research I've provided to create the table. Never include your background knowledge or other research.
IMPORTANT: For every fact you include in the table, you must use a footnote to cite the <excerpt_id></excerpt_id> of the excerpt from the research above that supports the fact.

Use markdown to format the table and the footnotes. You should use other markdown conventions like lists, bold and italics within the table cells. Separate the table and the footnotes with a horizontal rule (---).

Give me the markdown table content in markdown, with footnotes all enclosed in a <content></content> tag, like this:
<content>
| Header 1 | Header 2 | Header 3 |
|----------|----------|----------|
| Content 1[^2] | Content 2[^1] | Content 3[^3] |
| Content 4[^4] | Content 5[^3] | - Content 6[^5]\n-Content 7[^5] |

---
[^1]: <excerpt_id>a1b2c3d4</excerpt_id>
[^2]: <excerpt_id>e5f6g7h8</excerpt_id>
[^3]: <excerpt_id>i9j0k1l2</excerpt_id>
[^4]: <excerpt_id>q7r8s9t0</excerpt_id>
[^5]: <excerpt_id>u1v2w3x4</excerpt_id>
</content>

Make sure you consider not just the <slide_title></slide_title>, but also the <subtopic></subtopic>, and the <topic></topic>, <audience></audience> and <goal></goal> of the <presentation></presentation> I mentioned earlier when creating the table.
Remember you must cite an excerpt id as a source for every fact in the table, so you can only use information found in my research."""


async def get_markdown_table_slide(presentation_topic, presentation_audience, presentation_goal, subtopic_name, reduced_docs, slide_idea, excerpt_ids):
    response = await bedrock_client.chat.completions.create(
        model="anthropic.claude-3-haiku-20240307-v1:0",
        messages=[{"role": "user", "content": get_markdown_table_slide_prompt(
            get_presentation_xml(presentation_topic, presentation_audience, presentation_goal),
            format_topic_xml(reduced_docs, show_sources=False,
                             show_excerpt_ids=True),
            subtopic_name,
            slide_idea['slide_title'],
            slide_idea['slide_content_idea'],
            excerpt_ids)}],
        temperature=0,
        max_tokens=1500,
        stop=["</content>"],
    )
    response_text = response.choices[0].message.content.strip(
    ) + "\n</content>"

    def parse_table_and_footnotes(input_string, excerpt_ids):
        content_pattern = r'<content>\s*(.*?)(?:\n---|\n\*\*\*|\n\+\+\+|\n===|\n___)\s*'
        content_match = re.search(content_pattern, input_string, re.DOTALL)
        table = content_match.group(1).strip() if content_match else ''

        footnote_pattern = r'\[\^(\d+)\]:\s*<excerpt_id>(\w+)</excerpt_id>'
        footnote_matches = re.findall(footnote_pattern, input_string)

        footnote_excerpt_ids = {num: get_id_from_suffix(excerpt_ids, excerpt_id) for num, excerpt_id in footnote_matches}
        
        footnotes = {}
        for num, excerpt_id in footnote_excerpt_ids.items():
            # get excerpt text
            source_excerpt = next((doc['page_content'] for doc in reduced_docs if doc['metadata']['id'] == excerpt_id), None)
            # get source id
            source_id = next((doc['metadata']['source']['id'] for doc in reduced_docs if doc['metadata']['id'] == excerpt_id), None)
            footnotes[num] = {
                'excerpt_id': excerpt_id,
                'source_id': source_id,
                'text': source_excerpt
            }
            
        return {
            'table': table,
            'footnotes': footnotes
        }

    parsed_content_and_footnotes = parse_table_and_footnotes(
        response_text, excerpt_ids)
    return {
        'slide_title': slide_idea['slide_title'],
        'slide_type': 'markdown_table_slide',
        'slide_content': parsed_content_and_footnotes
    }


def get_simple_mermaid_slide_prompt(presentation_xml, research_xml, subtopic_name, slide_title, slide_content_idea, excerpt_ids):
    return f"""
I'm creating the presentation described below:
{presentation_xml}

Here's the subtopic for the section I'm working on right now:
<subtopic>{subtopic_name}</subtopic>

Here's the research I have for the <subtopic></subtopic>:
<research>
{research_xml}
</research>

Within the <subtopic></subtopic>, I'm working on a slide called <slide_title>{slide_title}</slide_title>.
I need you to create a mermaid diagram for this slide.

You may only use the research I've provided to create the diagram. Never include your background knowledge or other research.
After you create the diagram, you must create a list of <excerpt_id></excerpt_id> to cite every excerpt from the research that supports the facts and information you included in the diagram.

Give me the mermaid diagram content, as well as the list of excerpt ids in the following xml format:
<mermaid_diagram>
graph LR
    A["Square Rect"] -- "Link text" --> B(("Circle"))
    A --> C("Round Rect")
    B --> D{{"Rhombus"}}
    C --> D
</mermaid_diagram>
<sources>
<excerpt_id>a1b2c3d4</excerpt_id>
<excerpt_id>e5f6g7h8</excerpt_id>
<excerpt_id>i9j0k1l2</excerpt_id>
</sources>

It's absolutely imperative that you use correct mermaid syntax so that the diagram is rendered correctly without any errors.
Follow this rule to ensure the diagram is rendered correctly:
***Always put double quotes around the the node texts and link texts in the diagram. Do not use double quotes in other contexts, use single quotes instead.***
For example: A["Square Rect"] -- "Link text" --> B(("Circle says 'Hi'"))
Keep the diagram simple, about 6 nodes or less.

Remember to cite an excerpt id as a source for every fact in the diagram, and only use information found in my research."""


async def get_simple_mermaid_slide(presentation_topic, presentation_audience, presentation_goal, subtopic_name, reduced_docs, slide_idea, excerpt_ids):
    response = await bedrock_client.chat.completions.create(
        model="anthropic.claude-3-haiku-20240307-v1:0",
        messages=[{"role": "user", "content": get_simple_mermaid_slide_prompt(
            get_presentation_xml(presentation_topic, presentation_audience, presentation_goal),
            format_topic_xml(reduced_docs, show_sources=False,
                             show_excerpt_ids=True),
            subtopic_name,
            slide_idea['slide_title'],
            slide_idea['slide_content_idea'],
            excerpt_ids)}],
        temperature=0,
        max_tokens=1500,
        stop=["</sources>"],
    )
    response_text = response.choices[0].message.content.strip() + "</sources>"

    def clean_mermaid_code(code):
        code = re.sub(
            r'(\w+\[|{|\()([^"\]]+)"([^"\]]+)"(?=\])', r'\1\2\'\3\'', code)
        code = re.sub(
            r'(\w+\[)([^"\[\]\(\)\{\}]+(?:\([^)]*\))*[^"\[\]\(\)\{\}]*)(\])', r'\1"\2"\3', code)
        return code

    def parse_mermaid_and_sources(input_string, excerpt_ids):
        mermaid_pattern = r'<mermaid_diagram>\s*(.*?)\s*</mermaid_diagram>'
        mermaid_match = re.search(mermaid_pattern, input_string, re.DOTALL)
        mermaid_code = mermaid_match.group(1).strip() if mermaid_match else ''
        # mermaid_code_cleaned = clean_mermaid_code(mermaid_code)
        mermaid_code_cleaned = mermaid_code

        excerpt_pattern = r'<excerpt_id>(.*?)</excerpt_id>'
        excerpt_id_suffixes = re.findall(excerpt_pattern, input_string)
        match_excerpt_ids = [get_id_from_suffix(excerpt_ids, suffix) for suffix in excerpt_id_suffixes]
        
        diagram_excerpts = []
        for excerpt_id in match_excerpt_ids:
            # get excerpt text
            source_excerpt = next((doc['page_content'] for doc in reduced_docs if doc['metadata']['id'] == excerpt_id), None)
            # get source id
            source_id = next((doc['metadata']['source']['id'] for doc in reduced_docs if doc['metadata']['id'] == excerpt_id), None)
            diagram_excerpts.append({
                'excerpt_id': excerpt_id,
                'source_id': source_id,
                'text': source_excerpt
            })

        return {
            'mermaid_code': mermaid_code_cleaned,
            'excerpts': diagram_excerpts
        }

    parsed_mermaid_and_sources = parse_mermaid_and_sources(
        response_text, excerpt_ids)
    return {
        'slide_title': slide_idea['slide_title'],
        'slide_type': 'simple_mermaid_slide',
        'slide_content': parsed_mermaid_and_sources
    }


async def get_slide_content(presentation_topic, presentation_audience, presentation_goal, subtopic_name, reduced_docs, slide_idea, excerpt_ids):
    slide_type = slide_idea['slide_type']
    if slide_type == 'short_bullets_slide':
        return await get_short_bullets_slide(presentation_topic, presentation_audience, presentation_goal, subtopic_name, reduced_docs, slide_idea, excerpt_ids)
    elif slide_type == 'long_bullets_slide':
        return await get_long_bullets_slide(presentation_topic, presentation_audience, presentation_goal, subtopic_name, reduced_docs, slide_idea, excerpt_ids)
    elif slide_type == 'markdown_table_slide':
        return await get_markdown_table_slide(presentation_topic, presentation_audience, presentation_goal, subtopic_name, reduced_docs, slide_idea, excerpt_ids)
    elif slide_type == 'simple_mermaid_slide':
        return await get_simple_mermaid_slide(presentation_topic, presentation_audience, presentation_goal, subtopic_name, reduced_docs, slide_idea, excerpt_ids)
    else:
        raise ValueError(f"Unknown slide type: {slide_type}")


async def get_topic_slides(presentation_id, presentation_topic, presentation_audience, presentation_goal, subtopic_name, subtopic_id, all_docs):

    reduced_docs = await reduce_docs(presentation_id, all_docs, 4000, subtopic_name, subtopic_id)
    excerpt_ids = get_excerpt_ids(reduced_docs)
    
    slide_ideas = await get_slide_ideas(
        presentation_topic,
        presentation_audience,
        presentation_goal,
        subtopic_name,
        reduced_docs
        )

    slide_content_tasks = [
        asyncio.create_task(get_section_header_slide(
            presentation_id=presentation_id,
            presentation_topic=presentation_topic,
            presentation_audience=presentation_audience,
            presentation_goal=presentation_goal,
            subtopic_name=subtopic_name
        ))
    ] + [
        asyncio.create_task(get_slide_content(
            presentation_topic,
            presentation_audience,
            presentation_goal,
            subtopic_name,
            reduced_docs,
            slide_idea,
            excerpt_ids
            ))
        for slide_idea in slide_ideas
    ]

    slides = await asyncio.gather(*slide_content_tasks)

    return slides

async def get_section_header_slide(presentation_id, presentation_topic, presentation_audience, presentation_goal, subtopic_name):
    response = await generate_image(presentation_id, presentation_topic, presentation_audience, presentation_goal, slide_type="section_header_slide", subtopic=subtopic_name)
    
    if response.get('statusCode') != 200:
        raise ValueError(f"Error generating image: {response['body']}")
    else:
        image_data = response['body']
        
    return {
        'slide_title': subtopic_name,
        'slide_type': 'section_header_slide',
        'image': image_data
    }
    
async def get_presentation_title_slide(presentation_id, presentation_topic, presentation_audience, presentation_goal):
    response = await generate_image(presentation_id, presentation_topic, presentation_audience, presentation_goal, slide_type="presentation_title_slide")
    
    if response['statusCode'] != 200:
        raise ValueError(f"Error generating image: {response['body']}")
    else:
        image_data = response['body']
        
    return [{
        'slide_title': presentation_topic,
        'slide_type': 'presentation_title_slide',
        'image': image_data
    }]

async def make_presentation_slides(presentation_id):
    # Get presentation data: topics, audience, goal
    presentation = await get_presentation(presentation_id, ["candidate_topics", "outline", "audience", "goal", "topic"])

    if not all(key in presentation for key in ["candidate_topics", "outline", "audience", "goal", "topic"]):
        raise ValueError("Missing required keys in presentation data")
    
    candidate_topics = json.loads(presentation["candidate_topics"])
    outline = json.loads(presentation["outline"])
    
    if candidate_topics is None or outline is None:
        raise ValueError("Missing candidate_topics or outline")

    final_topics = [(next((candidate_topic for candidate_topic in candidate_topics if candidate_topic['id'] == outline_topic['id']), None)) for outline_topic in outline if outline_topic['included']]

    if not final_topics:
        raise ValueError("No final topics found")

    # Get chunked and labeled documents from S3 for whole presentation
    all_docs = await download_model_list_from_s3(Document, f"{presentation_id}/all_sources_chunked_docs_with_topics.json")

    # Use asyncio.gather to await get_topic_slides for each topic concurrently
    slide_tasks = [
        get_presentation_title_slide(
            presentation_id=presentation_id,
            presentation_topic=presentation['topic'],
            presentation_audience=presentation['audience'],
            presentation_goal=presentation['goal']
        )
    ] + [
        get_topic_slides(
            presentation_id=presentation_id,
            presentation_topic=presentation['topic'],
            presentation_audience=presentation['audience'],
            presentation_goal=presentation['goal'],
            subtopic_name=topic['name'],
            subtopic_id=topic['id'],
            all_docs=all_docs
        )
        for topic in final_topics
    ]

    # list of slides with presentation title slide, section header slides, and topic slides
    slides_list = await asyncio.gather(*slide_tasks)
    
    # add topic ids to slides
    # first list in slides list is the presentation title slide
    for topic, topic_slides in zip(final_topics, slides_list[1:]):
        topic_id = topic['id']
        for slide in topic_slides:
            slide['topic_id'] = topic_id
    
    # flatten
    flat_slides = [slide for topic_slides in slides_list for slide in topic_slides]
    
    # add slide ids
    for i, slide in enumerate(flat_slides):
        slide['id'] = uuid7str()
        slide['slide_order'] = (i + 1) * 1000
        
    # delete all existing slides from dynamodb
    await delete_all_slides(presentation_id)
    # upload slides to dynamodb
    
    
    await asyncio.gather(
        batch_update_slides(presentation_id, flat_slides),
        update_presentation(presentation_id, slide_generation_status="complete")
    )
    
    return flat_slides
    

async def test():
    presentation_id = "018f0e4c-3988-7f1f-97c6-c316a92540f6"
    slides = await make_presentation_slides(presentation_id)
    print(slides)

if __name__ == "__main__":
    asyncio.run(test())
