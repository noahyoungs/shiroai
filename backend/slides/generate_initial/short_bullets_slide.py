from pydantic import BaseModel, Field
from typing import List, Literal
from slides.generate_initial.utils import get_id_from_suffix, get_research_xml
from slides.xml_instructor import generate_variable_input_xml, get_basemodel_instance_from_llm, create_dynamic_enum_validator
from slides.icons.icon_similarity_search import hybrid_icon_assignment
from uuid_extensions import uuid7str
from database_models import ShortBulletsSlide
from portkey_ai import AsyncPortkey

bedrock_client = AsyncPortkey(
    virtual_key="aldeo-portkey-b-5cf75f",
    config={"cache": {"mode": "simple"},
                "retry": {
            "attempts": 3,
            "on_status_codes": [429, 500, 502, 503, 504, 424],
            }},
)

claude_haiku = "anthropic.claude-3-haiku-20240307-v1:0"

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

    prompt = f"""\
We're creating the presentation described below:
{presentation_xml}

Here's the subtopic for the section we're working on right now:
{subtopic_xml}

Here's the research we have for the <subtopic></subtopic>:
{research_xml}

Within the <subtopic></subtopic>, we're working on a slide called <slide_title>{slide_idea['slide_title']}</slide_title>.
We need you to create 2-5 short bullet points to go on this slide. Each bullet point should be 10 words or less and the bullet points cannot be nested.
Do not include * , - , or leading numbers in your bullet point, just the text.
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
    for bullet_point in short_bullets_slide.dict()['bullet_points']:
        source_excerpt_id = get_id_from_suffix(
            excerpt_ids, bullet_point['excerpt_id'])
        source_excerpt = next(
            (doc['page_content'] for doc in reduced_docs if doc['metadata']['id'] == source_excerpt_id), None)
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

    return ShortBulletsSlide(
        slide_title=slide_idea['slide_title'],
        id=uuid7str(),
        generation_messages=messages,
        slide_type='short_bullets_slide',
        slide_content=bullet_points_list,
        sequential=short_bullets_slide.sequential_order == 'yes',
    )