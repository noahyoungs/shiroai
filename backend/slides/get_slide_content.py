# get_slide_content.py
from dotenv import load_dotenv
from dynamodb import get_presentation, delete_all_slides, update_presentation
import json
import asyncio
from portkey_ai import AsyncPortkey
from uuid_extensions import uuid7str
from slides.format import format_topic_xml
from slides.reduce_topic_research import reduce_docs
from dotenv import load_dotenv
from slides.images.generate_image import generate_and_upload_image
from slides.icons.icon_similarity_search import hybrid_icon_assignment
from typing import List, Literal
from pydantic import BaseModel, Field
from slides.xml_instructor import generate_variable_input_xml, get_basemodel_instance_from_llm, create_dynamic_enum_validator
from slides.mermaid.validate_mermaid import validate_mermaid_diagram
from slides.clean_markdown import clean_markdown
from pydantic_async_validation import async_field_validator, AsyncValidationModelMixin
from typing import List
from slides.mermaid.validate_mermaid import validate_mermaid_diagram
import xml.etree.ElementTree as ET
from slides.mermaid.mermaid_to_svg import process_diagram_to_svgs
from slides.mermaid.mermaid_prompt import get_messages
from slides.slide_models import *
from slides.persistent_slide_list import PersistentSlideList

load_dotenv()

bedrock_client = AsyncPortkey(
    virtual_key="aldeo-portkey-b-5cf75f",
    config={"cache": {"mode": "simple"},
                "retry": {
            "attempts": 3,
            "on_status_codes": [429, 500, 502, 503, 504, 424],
            }},
)

llama_client = AsyncPortkey(
    config={
        'strategy': {
            'mode': "fallback",
            'on_status_codes': [429]
        },
        'targets': [
            {
                'virtual_key': "groqcloud-c9a2c3",
                "override_params": {
                    "model": "llama3-8b-8192"
                }
            },
            {
                'virtual_key': "together-36056e",
                "override_params": {
                    "model": "meta-llama/Llama-3-8b-chat-hf"
                }
            }
        ],
    },
)

llama3_8b = "llama3-8b-8192"
claude_haiku = "anthropic.claude-3-haiku-20240307-v1:0"


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


def get_subtopic_xml(subtopic_name):
    return f"""<subtopic>{subtopic_name}</subtopic>"""


def get_research_xml(reduced_docs):
    return f"<research>\n{format_topic_xml(reduced_docs, show_sources=False, show_excerpt_ids=True)}\n</research>"


async def get_slide_ideas(presentation_xml, subtopic_xml, research_xml):

    # Define the response schema
    class CompletionSlide(BaseModel):
        slide_type: Literal["short_bullets_slide", "long_bullets_slide",
                            "markdown_table_slide", "simple_mermaid_slide"]
        slide_title: str = Field(..., min_length=5, max_length=75)
        slide_content_idea: str = Field(..., min_length=20, max_length=600)

    class CompletionSlideList(BaseModel):
        slides: List[CompletionSlide] = Field(..., min_items=1, max_items=4)

        class Config:
            json_schema_extra = {
                "example": {
                    "slides": [
                        {
                            "slide_type": "short_bullets_slide",
                            "slide_title": "This is the slide title",
                            "slide_content_idea": "This slide will talk about Lorem Ipsum dolor sit amet, consectetur adipiscing elit.",
                        },
                        {
                            "slide_type": "longer_bullets_slide",
                            "slide_title": "This is the slide title",
                            "slide_content_idea": "This slide will talk about Lorem Ipsum dolor sit amet, consectetur adipiscing elit.",
                        }
                    ],
                }
            }

    prompt = prompt = f"""
We're creating the presentation described below:
{presentation_xml}

We're working on a section about {subtopic_xml} and we need some ideas for slides. Here's the research we've done for the section:
{research_xml}

Carefully read our research and devise a plan to create 1-4 powerpoint slides for the <subtopic></subtopic>. Here are the allowed slide types:

short_bullets_slide: 2-4 short unnested bullet points
long_bullets_slide: allows for more bullet points, longer bullet points, and nesting bullet points
markdown_table_slide: a slide with a markdown table
simple_mermaid_slide: a simple flow chart or diagram that can be expressed in mermaid

Don't actually create the slide content in your plan. Instead, give us a list of <slide></slide> XML tags.
In each <slide></slide> tag include a  <slide_type></slide_type>, <slide_title></slide_title> and a concise but detailed <slide_content_idea></slide_content_idea> written in sentences of what information could be included in the slide. The <slide_content_idea></slide_content_idea> should be written in complete sentences and should describe in plain English what the slide could contain, and it must be less than 100 words long.
Do not create an Introduction or Conclusion slide.

You must respond in the following format:
{generate_variable_input_xml(CompletionSlideList)}

Make sure you consider not just the <subtopic></subtopic>, but also the <topic></topic>, the <audience></audience> and the <goal></goal> of the <presentation></presentation> we mentioned earlier when creating the slides.
Remember, the <slide_content_idea></slide_content_idea> is not the actual content of the slide, but a description of what the slide could contain. It should be written in plain English and be less than 100 words long."""

    messages = [{'role': 'user', 'content': prompt}]

    slide_list, messages = await get_basemodel_instance_from_llm(
        client=bedrock_client,
        pydantic_model_class=CompletionSlideList,
        max_iterations=5,
        model=claude_haiku,
        max_tokens=2000,
        messages=messages,
    )

    # return slide_list as list of dict
    return slide_list.model_dump()['slides']


async def get_short_bullets_slide(presentation_xml, subtopic_xml, reduced_docs, slide_idea, excerpt_ids):
    id_suffixes = [id[-8:] for id in excerpt_ids]
    research_xml = get_research_xml(reduced_docs)

    class CompletionBulletPoint(BaseModel):
        content: str = Field(..., min_length=1, max_length=80)
        excerpt_id: str = Field(..., min_length=8, max_length=8)

        validate_excerpt_id = create_dynamic_enum_validator(
            'valid_ids', 'excerpt_id')

    class CompletionShortBulletsSlide(BaseModel):
        bullet_points: List[CompletionBulletPoint] = Field(
            ..., min_items=2, max_items=5)
        sequential_order: Literal["yes", "no"]

    prompt = prompt = f"""\
We're creating the presentation described below:
{presentation_xml}

Here's the subtopic for the section we're working on right now:
{subtopic_xml}

Here's the research we have for the <subtopic></subtopic>:
{research_xml}

Within the <subtopic></subtopic>, we're working on a slide called <slide_title>{slide_idea['slide_title']}</slide_title>.
We need you to create 2-5 short bullet points to go on this slide. Each bullet point should be 10 words or less and the bullet points cannot be nested.
Do not include `* `, `- `, or leading numbers in your bullet point, just the text.
Here's an idea for what you might talk about in your bullet points, to get you started:
<slide_content_idea>{slide_idea['slide_content_idea']}</slide_content_idea>
You don't have to follow this idea exactly, but it should give you a sense of what we're looking for.

In a <bullet_points></bullet_points> XML tag, please give us 2-5 <bullet_point></bullet_point> tags. In each <bullet_point></bullet_point> tag, include a <content></content> and a <excerpt_id></excerpt_id>.
You must back up every single bullet point you write with one of the excerpts in the <research></research> above. Never include your background knowledge or other research.
You must include the <excerpt_id></excerpt_id> of the <excerpt></excerpt> from the <research></research> above that supports the bullet point.

Then, after the <bullet_points></bullet_points> tag, include a <sequential></sequential> tag with either "yes" or "no" to indicate whether the bullet points should have a sequential order. Some examples of sequential bullet points are steps in a process, chronologies or timelines, and hierarchies. If the bullet points are not sequential, they are likely a list of related items or ideas.

Please respond in the following XML format:
{generate_variable_input_xml(CompletionShortBulletsSlide)}

Make sure you consider not just the <slide_title></slide_title>, but also the <subtopic></subtopic>, and the <topic></topic>, <audience></audience> and <goal></goal> of the <presentation></presentation> we mentioned earlier when creating the bullet points.
Remember you must cite an <excerpt_id></excerpt_id> as a source for every bullet point, so you can only use information found in our research."""

    messages = [{'role': 'user', 'content': prompt}]

    short_bullets_slide, messages = await get_basemodel_instance_from_llm(
        client=bedrock_client,
        pydantic_model_class=CompletionShortBulletsSlide,
        max_iterations=5,
        dynamic_val_params={"valid_ids": id_suffixes},
        model=claude_haiku,
        max_tokens=2000,
        messages=messages,
        temperature=0.5,
    )

    bullet_points_list = []
    # replace excerpt_id which contains a prefix with the actual excerpt_id
    for bullet_point in short_bullets_slide.dict()['bullet_points']:
        source_excerpt_id = get_id_from_suffix(
            excerpt_ids, bullet_point['excerpt_id'])
        # get excerpt text
        source_excerpt = next(
            (doc['page_content'] for doc in reduced_docs if doc['metadata']['id'] == source_excerpt_id), None)
        # get source id
        source_id = next((doc['metadata']['source']['id']
                         for doc in reduced_docs if doc['metadata']['id'] == source_excerpt_id), None)

        bullet_points_list.append({
            'content': bullet_point['content'],
            'excerpt': {
                'source_id': source_id,
                'excerpt_id': source_excerpt_id,
                'text': source_excerpt
            },
            'id': uuid7str()
        })

    icon_data = await hybrid_icon_assignment([bullet_point['content'] for bullet_point in bullet_points_list])

    for dict in bullet_points_list:
        dict['icon'] = {'name': icon_data[dict['content']][0],
                        'source': icon_data[dict['content']][1]}

    # Inside get_short_bullets_slide
    return ShortBulletsSlide(
        slide_title=slide_idea['slide_title'],
        id=uuid7str(),
        generation_messages=messages,
        generation_excerpt_ids=excerpt_ids,
        slide_type='short_bullets_slide',
        slide_content=bullet_points_list,
        sequential=short_bullets_slide.sequential_order == 'yes',
    )



async def get_long_bullets_slide(presentation_xml, subtopic_xml, reduced_docs, slide_idea, excerpt_ids):
    id_suffixes = [id[-8:] for id in excerpt_ids]
    research_xml = get_research_xml(reduced_docs)

    class CompletionFootnote(BaseModel):
        marker: int = Field(..., ge=1)
        excerpt_id: str = Field(..., min_length=8, max_length=8)

        validate_excerpt_id = create_dynamic_enum_validator(
            'valid_ids', 'excerpt_id')

    class CompletionLongBulletsSlide(BaseModel):
        markdown_content: str = Field(..., min_length=1, max_length=2000)
        footnotes: List[CompletionFootnote]

    prompt = prompt = f"""
We're creating the presentation described below:
{presentation_xml}

Here's the subtopic for the section we're working on right now:
{subtopic_xml}

Here's the research we have for the <subtopic></subtopic>:
{research_xml}

Within the <subtopic></subtopic>, we're working on a slide called <slide_title>{slide_idea['slide_title']}</slide_title>.
We need you to create the bullet point content for this slide. 

Here's an idea for the slide content, to get you started:
<slide_content_idea>{slide_idea['slide_content_idea']}</slide_content_idea>
You don't have to follow this idea exactly, but it should give you a sense of what we're looking for.

You may only use information you see in the research we've provided to create the bullet points. Never include your background knowledge or other research.

Put your bullet points in a <markdown_content></markdown_content> tag, and use markdown to format the bullet points. You can use numbered and unnumbered lists, and you should nest lists whenever possible. You should also use other markdown conventions like bold and italics when appropriate, and you can use headings to organize your bullet points if you like.

For each fact you include, you must add a footnote reference (e.g. `[^1]`) in the markdown text in your <markdown_content></markdown_content> tag.
Then, in a <footnotes></footnotes> tag, include a list of <footnote></footnote> each with a <marker></marker> and an <excerpt_id></excerpt_id>. The <marker></marker> should be ONLY THE NUMBER of the footnote reference in the bullet point content (e.g. `1`), and the <excerpt_id></excerpt_id> should be A SINGLE <excerpt_id></excerpt_id> of the <excerpt></excerpt> from the <research></research> above that supports the fact. Each <footnote></footnote> can only include one <excerpt_id></excerpt_id> and one <marker></marker>, but you can reference more than one <footnote></footnote> in the <markdown_content></markdown_content> tag like this: `[^1][^2][^3]`.
Do not include a list of footnotes at the end of the <markdown_content></markdown_content>, just give us the <footnotes></footnotes> tag with all the <footnote></footnote> tags inside it.

Please respond in the following XML format:
{generate_variable_input_xml(CompletionLongBulletsSlide)}

Make sure you consider not just the <slide_title></slide_title>, but also the <subtopic></subtopic>, and the <topic></topic>, <audience></audience> and <goal></goal> of the <presentation></presentation> we mentioned earlier when creating the bullet points.
Remember you must cite an excerpt id as a source for every bullet point, so you can only use information found in our research."""

    messages = [{'role': 'user', 'content': prompt}]

    long_bullets_slide, messages = await get_basemodel_instance_from_llm(
        client=bedrock_client,
        pydantic_model_class=CompletionLongBulletsSlide,
        max_iterations=5,
        dynamic_val_params={"valid_ids": id_suffixes},
        model=claude_haiku,
        max_tokens=2000,
        messages=messages,
        temperature=0.5,
    )

    new_footnotes = {}

    for old_footnote in long_bullets_slide.dict()['footnotes']:
        excerpt_id = get_id_from_suffix(
            excerpt_ids, old_footnote['excerpt_id'])
        source_excerpt = next(
            (doc['page_content'] for doc in reduced_docs if doc['metadata']['id'] == excerpt_id), None)
        source_id = next((doc['metadata']['source']['id']
                         for doc in reduced_docs if doc['metadata']['id'] == excerpt_id), None)
        new_footnotes[old_footnote['marker']] = {
            'excerpt_id': excerpt_id,
            'source_id': source_id,
            'text': source_excerpt
        }

    slide_content = {
        'content': clean_markdown(long_bullets_slide.markdown_content, slide_idea['slide_title']),
        'footnotes': new_footnotes
    }

    return MarkdownSlide(
        slide_title=slide_idea['slide_title'],
        id=uuid7str(),
        generation_messages=messages,
        generation_excerpt_ids=excerpt_ids,
        slide_type='markdown_slide',
        slide_content=slide_content
    )



async def get_markdown_table_slide(presentation_xml, subtopic_xml, reduced_docs, slide_idea, excerpt_ids):
    id_suffixes = [id[-8:] for id in excerpt_ids]
    research_xml = get_research_xml(reduced_docs)

    class CompletionFootnote(BaseModel):
        marker: int = Field(..., ge=1)
        excerpt_id: str = Field(..., min_length=8, max_length=8)

        validate_excerpt_id = create_dynamic_enum_validator(
            'valid_ids', 'excerpt_id')

    class CompletionMarkdownTableSlide(BaseModel):
        markdown_table: str = Field(..., min_length=1, max_length=3000)
        footnotes: List[CompletionFootnote]

    prompt = f"""
We're creating the presentation described below:
{presentation_xml}

Here's the subtopic for the section we're working on right now:
{subtopic_xml}

Here's the research we have for the <subtopic></subtopic>:
{research_xml}

Within the <subtopic></subtopic>, we're working on a slide called <slide_title>{slide_idea['slide_title']}</slide_title>.
We need you to create a markdown table for this slide.

Here's an idea for the slide content, to get you started:
<slide_content_idea>{slide_idea['slide_content_idea']}</slide_content_idea>
You don't have to follow this idea exactly, but it should give you a sense of what we're looking for.

You may only use information you see in the research we've provided to create the bullet points. Never include your background knowledge or other research.
IMPORTANT: For every fact you include in the table, you must use a footnote to cite the <excerpt_id></excerpt_id> of the excerpt from the research above that supports the fact.

Put your table in a <markdown_table></markdown_table> tag. You can use markdown conventions like lists, bold and italics within the table cells. You can't put line breaks inside the table cells so you'll have to use html <br/> tags if you need to break a line inside a cell.
IMPORTANT: For every fact stated in your table, you must add a footnote reference (e.g. `[^1]`) in the markdown text in your <markdown_table></markdown_table>.

Then, in a <footnotes></footnotes> tag, include a list of <footnote></footnote> each with a <marker></marker> and an <excerpt_id></excerpt_id>. The <marker></marker> should be the number of the footnote reference in the bullet point content, and the <excerpt_id></excerpt_id> should be the <excerpt_id></excerpt_id> of the <excerpt></excerpt> from the <research></research> above that supports the bullet point.
Do not include a list of footnotes in the <markdown_table></markdown_table>, just give us the <footnotes></footnotes> tag with all the <footnote></footnote> tags inside it.

Please respond in the following XML format:
{generate_variable_input_xml(CompletionMarkdownTableSlide)}

Make sure you consider not just the <slide_title></slide_title>, but also the <subtopic></subtopic>, and the <topic></topic>, <audience></audience> and <goal></goal> of the <presentation></presentation> we mentioned earlier when creating the table.
Remember you must cite an <excerpt_id></excerpt_id> as a source for every fact in the table, so you can only use information found in our research."""

    messages = [{'role': 'user', 'content': prompt}]

    markdown_table_slide, messages = await get_basemodel_instance_from_llm(
        client=bedrock_client,
        pydantic_model_class=CompletionMarkdownTableSlide,
        max_iterations=5,
        dynamic_val_params={"valid_ids": id_suffixes},
        model=claude_haiku,
        max_tokens=2000,
        messages=messages,
        temperature=0.5,
    )

    new_footnotes = {}

    for old_footnote in markdown_table_slide.dict()['footnotes']:
        excerpt_id = get_id_from_suffix(
            excerpt_ids, old_footnote['excerpt_id'])
        source_excerpt = next(
            (doc['page_content'] for doc in reduced_docs if doc['metadata']['id'] == excerpt_id), None)
        source_id = next((doc['metadata']['source']['id']
                         for doc in reduced_docs if doc['metadata']['id'] == excerpt_id), None)
        new_footnotes[old_footnote['marker']] = {
            'excerpt_id': excerpt_id,
            'source_id': source_id,
            'text': source_excerpt
        }

    slide_content = {
        'content': clean_markdown(markdown_table_slide.markdown_table, slide_idea['slide_title']),
        'footnotes': new_footnotes
    }

    return MarkdownSlide(
        slide_title=slide_idea['slide_title'],
        id=uuid7str(),
        generation_messages=messages,
        generation_excerpt_ids=excerpt_ids,
        slide_type='markdown_slide',
        slide_content=slide_content
    )



async def get_simple_mermaid_slide(presentation_xml, subtopic_xml, reduced_docs, slide_idea, excerpt_ids):
    id_suffixes = [id[-8:] for id in excerpt_ids]
    research_xml = get_research_xml(reduced_docs)

    class CompletionExcerptID(BaseModel):
        excerpt_id: str = Field(..., min_length=8, max_length=8)
        validate_excerpt_id = create_dynamic_enum_validator(
            'valid_ids', 'excerpt_id')

    class CompletionMermaidSlide(AsyncValidationModelMixin, BaseModel):
        reasoning: str
        mermaid_diagram: str
        excerpt_ids: List[CompletionExcerptID]

        @async_field_validator('mermaid_diagram')
        async def validate_mermaid(self, value: str):
            is_valid, message = await validate_mermaid_diagram(value)
            if not is_valid:
                raise ValueError(
                    f"There was a syntax error in your mermaid diagram. Please fix the syntax error:\n{message}")
            return value

    messages = get_messages(presentation_xml=presentation_xml, research_xml=research_xml,
                            subtopic_xml=subtopic_xml, slide_title_xml=f"<slide_title>{slide_idea['slide_title']}</slide_title>")

    simple_mermaid_slide, messages = await get_basemodel_instance_from_llm(
        client=bedrock_client,
        pydantic_model_class=CompletionMermaidSlide,
        max_iterations=5,
        model=claude_haiku,
        max_tokens=2000,
        messages=messages,
        temperature=1,
        temperature_multiplier=1.1,
        max_temperature=1.0,
        dynamic_val_params={"valid_ids": id_suffixes},
    )

    diagram_excerpts = []

    for excerpt_id in simple_mermaid_slide.dict()['excerpt_ids']:
        source_excerpt_id = get_id_from_suffix(
            excerpt_ids, excerpt_id['excerpt_id'])
        source_excerpt = next(
            (doc['page_content'] for doc in reduced_docs if doc['metadata']['id'] == source_excerpt_id), None)
        source_id = next((doc['metadata']['source']['id']
                         for doc in reduced_docs if doc['metadata']['id'] == source_excerpt_id), None)
        diagram_excerpts.append({
            'excerpt_id': source_excerpt_id,
            'source_id': source_id,
            'text': source_excerpt
        })

    light_svg, dark_svg = await process_diagram_to_svgs(simple_mermaid_slide.mermaid_diagram)

    # Inside get_simple_mermaid_slide
    return SimpleMermaidSlide(
        slide_title=slide_idea['slide_title'],
        id=uuid7str(),
        generation_messages=messages[-2:],
        generation_excerpt_ids=excerpt_ids,
        slide_type='simple_mermaid_slide',
        slide_content={
            'mermaid_code': simple_mermaid_slide.mermaid_diagram,
            'excerpts': diagram_excerpts,
            'light_svg': light_svg,
            'dark_svg': dark_svg
        }
    )



async def get_slide_content(presentation_xml, subtopic_xml, all_docs, slide_idea, excerpt_ids):

    slide_type = slide_idea['slide_type']
    if slide_type == 'short_bullets_slide':
        return await get_short_bullets_slide(presentation_xml, subtopic_xml, all_docs, slide_idea, excerpt_ids)
    elif slide_type == 'long_bullets_slide':
        return await get_long_bullets_slide(presentation_xml, subtopic_xml, all_docs, slide_idea, excerpt_ids)
    elif slide_type == 'markdown_table_slide':
        return await get_markdown_table_slide(presentation_xml, subtopic_xml, all_docs, slide_idea, excerpt_ids)
    elif slide_type == 'simple_mermaid_slide':
        return await get_simple_mermaid_slide(presentation_xml, subtopic_xml, all_docs, slide_idea, excerpt_ids)
    else:
        raise ValueError(f"Unknown slide type: {slide_type}")


async def get_slide_content_wrapper(presentation_xml, subtopic_xml, all_docs, slide_idea, excerpt_ids):
    try:
        return await get_slide_content(presentation_xml, subtopic_xml, all_docs, slide_idea, excerpt_ids)
    except Exception as e:
        print(f"Error creating slide: {e}")
        return None


async def get_section_header_slide_wrapper(presentation_id, presentation_topic, presentation_audience, presentation_goal, subtopic_name):
    try:
        return await get_section_header_slide(
            presentation_id=presentation_id,
            presentation_topic=presentation_topic,
            presentation_audience=presentation_audience,
            presentation_goal=presentation_goal,
            subtopic_name=subtopic_name
        )
    except Exception as e:
        print(f"Error creating section header slide: {e}")
        return None


async def get_topic_slides(presentation_id, presentation_topic, presentation_audience, presentation_goal, subtopic_name, subtopic_id, all_docs):
    presentation_xml = get_presentation_xml(
        presentation_topic, presentation_audience, presentation_goal)
    subtopic_xml = get_subtopic_xml(subtopic_name)
    reduced_docs = await reduce_docs(presentation_id, all_docs, 4000, subtopic_name, subtopic_id)
    research_xml = get_research_xml(reduced_docs)
    excerpt_ids = get_excerpt_ids(reduced_docs)

    slide_ideas = await get_slide_ideas(
        presentation_xml=presentation_xml,
        subtopic_xml=subtopic_xml,
        research_xml=research_xml
    )

    slide_content_tasks = [
        get_slide_content_wrapper(
            presentation_xml,
            subtopic_xml,
            reduced_docs,
            slide_idea,
            excerpt_ids
        )
        for slide_idea in slide_ideas
    ]

    slides = await asyncio.gather(
        get_section_header_slide_wrapper(
            presentation_id=presentation_id,
            presentation_topic=presentation_topic,
            presentation_audience=presentation_audience,
            presentation_goal=presentation_goal,
            subtopic_name=subtopic_name
        ),
        *slide_content_tasks
    )

    section_header_slide = slides[0] if slides[0] is not None else None
    content_slides = [slide for slide in slides[1:] if slide is not None]

    if section_header_slide is not None:
        content_slides.insert(0, section_header_slide)

    return content_slides


async def get_section_header_slide(presentation_id, presentation_topic, presentation_audience, presentation_goal, subtopic_name):
    image_data = await generate_and_upload_image(presentation_id, presentation_audience, presentation_goal, presentation_topic, section_topic=subtopic_name, shape="square", model_type="sdxl")

    return SectionHeaderSlide(
        slide_title=subtopic_name,
        id=uuid7str(),
        generation_messages=[],
        slide_type='section_header_slide',
        image=image_data,
    )



async def get_presentation_title_slide(presentation_id, presentation_topic, presentation_audience, presentation_goal):
    image_data = await generate_and_upload_image(presentation_id, presentation_topic, presentation_audience, presentation_goal, section_topic=None, shape="full", model_type="core")
    
    # Inside get_presentation_title_slide
    return [PresentationTitleSlide(
        slide_title=presentation_topic,
        id=uuid7str(),
        generation_messages=[],
        slide_type='presentation_title_slide',
        image=image_data
    )]



async def make_presentation_slides(presentation_id, all_docs=None):
    print("REMAKING SLIDES")
    # Get presentation data: topics, audience, goal
    presentation = await get_presentation(presentation_id, ["candidate_topics", "outline", "audience", "goal", "topic"])

    if not all(key in presentation for key in ["candidate_topics", "outline", "audience", "goal", "topic"]):
        raise ValueError("Missing required keys in presentation data")

    # All the available topics from BERTopic
    candidate_topics = json.loads(presentation["candidate_topics"])
    outline = json.loads(presentation["outline"])

    if candidate_topics is None or outline is None:
        raise ValueError("Missing candidate_topics or outline")

    # Topics that the user has selected
    final_topics = [(next((candidate_topic for candidate_topic in candidate_topics if candidate_topic['id']
                     == outline_topic['id']), None)) for outline_topic in outline if outline_topic['included']]

    if not final_topics:
        raise ValueError("No final topics found")

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
            slide.topic_id = topic_id

    # flatten
    flat_slides = [
        slide for topic_slides in slides_list for slide in topic_slides
    ]

    # for i, slide in enumerate(flat_slides):
    #     # Set topic_id if not already set
    #     # for presentation title and section header slides
    #     if not slide.topic_id:
    #         slide.topic_id = [topic['id'] for topic in final_topics if topic['name'] in slide.slide_title][0]

    # delete all existing slides from dynamodb
    await delete_all_slides(presentation_id)
    # upload slides to dynamodb
    
    # create persistent slide list
    slide_list = PersistentSlideList(presentation_id, slides=flat_slides)

    await update_presentation(presentation_id, slide_generation_status="complete", head_slide_id=flat_slides[0].id)

    return slide_list


async def test():
    presentation_id = "0190056c-6fa2-7187-9e81-3dd7b98837fc"
    slides = await make_presentation_slides(presentation_id)
    print(slides)

if __name__ == "__main__":
    asyncio.run(test())
