# Short Bullets Slide

from typing import List, Literal, Optional, Callable, Tuple, Union, Dict, Awaitable
from pydantic import BaseModel, Field
from pydantic_async_validation import AsyncValidationModelMixin, async_field_validator
from slides.clean_markdown import clean_markdown
from slides.mermaid.mermaid_to_svg import process_diagram_to_svgs
from slides.xml_instructor import create_dynamic_enum_validator, generate_variable_input_xml, get_basemodel_instance_from_llm, generate_xml_from_instance
from dotenv import load_dotenv
from slides.mermaid.validate_mermaid import validate_mermaid_diagram
from dynamodb_service import get_items_with_user
from slides.icons.icon_similarity_search import hybrid_icon_assignment
from database_models import Slide, Excerpt, ShortBulletContent, IconData
from uuid_extensions import uuid7str
from llm_clients import content_gen_client, content_gen_model

load_dotenv()



def get_excerpt_ids(reduced_docs):
    excerpt_ids = [doc['metadata']['document_id'] for doc in reduced_docs]
    return excerpt_ids


def get_id_from_suffix(excerpt_ids, suffix):
    return next((id for id in excerpt_ids if id.endswith(suffix)), None)


async def edit_sbs(slide_title, slide_content, sequential, instruction, messages, excerpt_ids):

    id_suffixes = [id[-8:] for id in excerpt_ids]

    class BulletPoint(BaseModel):
        content: str = Field(..., min_length=1, max_length=80)
        excerpt_id: Optional[str] = Field(None, min_length=8, max_length=8)

        validate_excerpt_id = create_dynamic_enum_validator(
            'valid_ids', 'excerpt_id')

    class ShortBulletsSlide(BaseModel):
        slide_title: Optional[str] = Field(None, min_length=1, max_length=75)
        bullet_points: Optional[List[BulletPoint]
                                ] = Field(None, min_items=2, max_items=5)
        sequential_order: Optional[Literal["yes", "no"]] = None
        message_to_user: str

    class OldShortBulletsSlide(BaseModel):
        slide_title: str = Field(None, min_length=1, max_length=75)
        bullet_points: List[BulletPoint] = Field(..., min_items=2, max_items=5)
        sequential_order: Literal["yes", "no"] = None

    old_sbs = None
    try:
        old_sbs = OldShortBulletsSlide.model_validate({
            "slide_title": slide_title,
            "bullet_points": [
                BulletPoint(
                    content=bp.content,
                    excerpt_id=bp.excerpt.excerpt_id[-8:],
                    valid_ids=id_suffixes
                ) for bp in slide_content
            ],
            "sequential_order": "yes" if sequential else "no",
        })

    except Exception as e:
        print(f"Slide content: {slide_content}")
        raise RuntimeError(
            f"Error validating current Icon Node slide (SBS): {e}")

    prompt = f"""\
Here's latest slide we have so far. This slide reflects both your previous work and the user's direct changes:
{generate_xml_from_instance(old_sbs)}

<system_requirements>
Remember that the slide has to have 2-5 short bullet points (nodes) to go on this slide. Each bullet point must be 80 characters or less and the bullet points cannot be nested.
Do not include `* `, `- `, or leading numbers in your bullet point, just the text.
The slide title must be between 1 and 75 characters.
</system_requirements>

The user has requested that we make the following change to the slide:
<user_request>{instruction}</user_request>

Your task is to change the slide to reflect the user's request. If the <user_request></user_request> conflicts with any of the <system_requirements></system_requirements>, you should prioritize the <system_requirements></system_requirements> and try to fufill the <user_request></user_request> as closely as possible while following the <system_requirements></system_requirements>.

To change the <slide_title></slide_title>, include a <slide_title></slide_title> tag with the new title in your response. If you don't include the a <slide_title></slide_title> tag, the current title will be kept.

To change the <bullet_points></bullet_points>, include a <bullet_points></bullet_points> tag with the new bullet points in your response. If you don't include a <bullet_points></bullet_points> tag, the current bullet points will be kept.
If you do include a <bullet_points></bullet_points> tag, you must include 2-5 <bullet_point></bullet_point> tags inside the <bullet_points></bullet_points> tag. In each <bullet_point></bullet_point> tag, include a <content></content> and an optional <excerpt_id></excerpt_id> to cite a source from the research whenever appropriate.
Note that if you include a <bullet_points></bullet_points> tag, the current <bullet_points></bullet_points> will be replaced entirely by the new ones you provide.

To update the <sequential_order></sequential_order>, include a <sequential_order></sequential_order> tag with either "yes" or "no" in your response, indicating whether the bullet points are of a sequential or ordered nature. If you don't include the a <sequential_order></sequential_order> tag, the current sequential order will be kept.

Finally, include a <message_to_user></message_to_user> tag with a message to the user explaining the changes you made to the slide.
Remember, if the <user_request></user_request> conflicts with any <system_requirements></system_requirements> you must prioritize the <system_requirements></system_requirements> and try to fufill the <user_request></user_request> as closely as possible while following the <system_requirements></system_requirements>.
"""

    if messages is None:
        messages = []
    messages.append({'role': 'user', 'content': prompt})

    short_bullets_slide, new_messages = await get_basemodel_instance_from_llm(
        client=content_gen_client,
        pydantic_model_class=ShortBulletsSlide,
        max_iterations=5,
        force_start_with_first_tag=False,
        model=content_gen_model,
        max_tokens=2000,
        messages=messages,
        dynamic_val_params={"valid_ids": id_suffixes},
        # error_prompt_suffix="\nIf this error was caused because the user request conflicted with the system requirements, please fix your response to adhere to the system requirements and in your <message_to_user></message_to_user> tag, explain to the user why you couldn't meet the user request due to the system requirements.",
    )

    return short_bullets_slide, new_messages


async def edit_markdown_slide(slide_title, slide_content, instruction, messages, excerpt_ids=None):
    
    footnotes = slide_content.get('footnotes', [])
    no_footnotes = not isinstance(footnotes, list) or len(footnotes) == 0

    if not no_footnotes:
        id_suffixes = [id[-8:] for id in excerpt_ids]

        class Footnote(BaseModel):
            marker: int = Field(..., ge=1)
            excerpt_id: str = Field(..., min_length=8, max_length=8)

            validate_excerpt_id = create_dynamic_enum_validator(
                'valid_ids', 'excerpt_id')

        class MarkdownSlide(BaseModel):
            slide_title: Optional[str] = Field(None, min_length=5, max_length=75)
            markdown_content: Optional[str] = Field(
                None, min_length=1, max_length=2000)
            footnotes: Optional[List[Footnote]] = Field(
                None, min_items=1, max_items=15)
            message_to_user: str

        class OldMarkdownSlide(BaseModel):
            slide_title: Optional[str] = Field(None, min_length=5, max_length=75)
            markdown_content: Optional[str] = Field(
                None, min_length=1, max_length=2000)
            footnotes: List[Footnote]

        old_mds = OldMarkdownSlide.model_validate({
            "slide_title": slide_title,
            "markdown_content": slide_content['content'],
            "footnotes": [{"marker": int(marker), "excerpt_id": excerpt['excerpt_id'][-8:]} for marker, excerpt in slide_content['footnotes'].items()],
            "valid_ids": id_suffixes
        })
    else:
        class MarkdownSlide(BaseModel):
            slide_title: Optional[str] = Field(None, min_length=5, max_length=75)
            markdown_content: Optional[str] = Field(
                None, min_length=1, max_length=2000)
            message_to_user: str

        class OldMarkdownSlide(BaseModel):
            slide_title: Optional[str] = Field(None, min_length=5, max_length=75)
            markdown_content: Optional[str] = Field(
                None, min_length=1, max_length=2000)

        old_mds = OldMarkdownSlide.model_validate({
            "slide_title": slide_title,
            "markdown_content": slide_content['content'],
        })

    prompt = f"""\
Here's the slide we have so far:
{generate_xml_from_instance(old_mds)}

<system_requirements>
The markdown content should be 2000 characters or less.
The slide title must be between 5 and 75 characters.
</system_requirements>

The user has requested that we make the following change to the slide:
<user_request>{instruction}</user_request>

Your task is to change the slide to reflect the user's request. If the <user_request></user_request> conflicts with any of the <system_requirements></system_requirements>, you should prioritize the <system_requirements></system_requirements> and try to fufill the <user_request></user_request> as closely as possible while following the <system_requirements></system_requirements>.

To change the <slide_title></slide_title>, include a <slide_title></slide_title> tag with the new title in your response. If you don't include the a <slide_title></slide_title> tag, the current title will be kept.

To change the <markdown_content></markdown_content>, include a <markdown_content></markdown_content> tag with the new markdown content in your response. If you don't include a <markdown_content></markdown_content> tag, the current markdown content will be kept.
Note that if you include a <markdown_content></markdown_content> tag, the current <markdown_content></markdown_content> will be replaced entirely by the new one you provide.

"""

    if not no_footnotes:
        prompt += """\
If you update the <markdown_content>, make sure you keep the footnote references (e.g. [^1]) in the markdown content up to date and update the <footnotes></footnotes> tag accordingly.

To update the <footnotes></footnotes>, include a <footnotes></footnotes> tag with the new footnotes in your response. If you don't include the a <footnotes></footnotes> tag, the current footnotes will be kept.
If you do include a <footnotes></footnotes> tag, you must include a list of <footnote></footnote> tags inside the <footnotes></footnotes> tag. In each <footnote></footnote> tag, include a <marker></marker> and an optional <excerpt_id></excerpt_id> to cite a source from the research whenever appropriate. The <marker></marker> must be an integer (e.g. 1) that corresponds to the footnote reference (e.g. [^1]) in the markdown content. The <excerpt_id></excerpt_id> must match one of the <excerpt_id></excerpt_id> tags in the <research><research>.
Note that if you include the <footnotes></footnotes> tag, the current <footnotes></footnotes> will be replaced entirely by the new ones you provide.
"""
    
    prompt += """\
Finally, include a <message_to_user></message_to_user> tag with a message to the user explaining the changes you made to the slide.
Remember, there should be up to date footnote references in the format [^1], [^2], etc. in the <markdown_content></markdown_content> and the <marker></marker> in the <footnotes></footnotes> should correspond to these references. The <excerpt_id></excerpt_id> in the <footnotes></footnotes> should be a valid <excerpt_id></excerpt_id> from the <research></research>.
"""

    if messages is None:
        messages = []
    messages.append({'role': 'user', 'content': prompt})

    markdown_slide, new_messages = await get_basemodel_instance_from_llm(
        client=content_gen_client,
        pydantic_model_class=MarkdownSlide,
        max_iterations=5,
        force_start_with_first_tag=False,
        model=content_gen_model,
        max_tokens=2000,
        messages=messages,
        dynamic_val_params={"valid_ids": id_suffixes} if not no_footnotes else {},
    )

    return markdown_slide, new_messages



async def edit_mermaid_slide(slide_title, slide_content, instruction, messages, excerpt_ids):

    diagram = slide_content['mermaid_code']
    excerpts = slide_content['excerpts']
    excerpt_id_suffixes = [ex.excerpt_id[-8:] for ex in excerpts]

    id_suffixes = [id[-8:] for id in excerpt_ids]

    class ExcerptId(BaseModel):
        excerpt_id: str = Field(..., min_length=8, max_length=8)
        validate_excerpt_id = create_dynamic_enum_validator(
            'valid_ids', 'excerpt_id')

    class OldMermaidSlide(BaseModel):
        slide_title: str = Field(None, min_length=1, max_length=75)
        mermaid_diagram: str
        excerpt_ids: List[ExcerptId]

    class Response(AsyncValidationModelMixin, BaseModel):
        slide_title: Optional[str] = Field(None, min_length=1, max_length=75)
        mermaid_diagram: Optional[str] = Field(
            None, min_length=1, max_length=2000)
        excerpt_ids: Optional[List[ExcerptId]] = Field(
            None, min_items=1, max_items=20)
        message_to_user: str

        @async_field_validator('mermaid_diagram')
        async def validate_mermaid(self, value: str):
            is_valid, message = await validate_mermaid_diagram(value)
            if not is_valid:
                raise ValueError(
                    f"There was a syntax error in your mermaid diagram. Please fix the syntax error:\n{message}")
            return value

    if type(excerpts[0]) == dict:
        slide_excerpt_ids = [ExcerptId(
            excerpt_id=ex['excerpt_id'][-8:], valid_ids=excerpt_id_suffixes) for ex in excerpts]
    else:
        slide_excerpt_ids = [ExcerptId(
            excerpt_id=ex.excerpt_id[-8:], valid_ids=excerpt_id_suffixes) for ex in excerpts]

    old_mermaid_slide = OldMermaidSlide(
        slide_title=slide_title,
        mermaid_diagram=diagram,
        excerpt_ids=slide_excerpt_ids
    )

    prompt = f"""\
Here's the mermaid diagram slide content we have so far:
{generate_xml_from_instance(old_mermaid_slide)}

The user has requested the following changes to the markdown diagram.
<user_request>{instruction}</user_request>

Please make the requested changes to the markdown diagram. 
Respond in the following format:
{generate_variable_input_xml(Response)}"""

    if messages is None:
        messages = []
    messages.append({'role': 'user', 'content': prompt})
    markdown_slide, new_messages = await get_basemodel_instance_from_llm(
        client=content_gen_client,
        pydantic_model_class=Response,
        max_iterations=5,
        force_start_with_first_tag=False,
        model=content_gen_model,
        max_tokens=2000,
        messages=messages,
        temperature=1.0,
        dynamic_val_params={"valid_ids": id_suffixes},
    )

    return markdown_slide, new_messages


async def edit_slide_content(
    presentation_id,
    current_slide: Slide,
    update_slides: Callable[[Union[Slide, Dict, List[Union[Slide, Dict]]], bool], Awaitable[None]],
    instruction: str
) -> Tuple[Slide, str]:

    if not current_slide:
        raise ValueError("No current slide found")

    if not current_slide.slide_type:
        raise ValueError("No slide type found for the slide")

    slide_type = current_slide.slide_type

    reduced_docs = None
    excerpt_ids = None
    if current_slide.topic_id:
        # Get reduced docs
        # reduced_docs = (await get_topics(presentation_id, current_slide.topic_id, ['reduced_docs'])).reduced_docs
        reduced_docs = (await get_items_with_user('topic', [{'presentation_id': presentation_id, 'topic_id': current_slide.topic_id}], ['reduced_docs'], 'model')).reduced_docs
        if not reduced_docs:
            raise RuntimeError("No reduced docs found for the topic")

        # Get excerpt ids
        excerpt_ids = get_excerpt_ids(reduced_docs)

    if slide_type == 'short_bullets_slide':
        print("Editing Short Bullets Slide")
        model, messages = await edit_sbs(
            current_slide.slide_title, 
            current_slide.slide_content, 
            current_slide.sequential, 
            instruction, 
            current_slide.generation_messages, 
            excerpt_ids
        )

        # Update the slide with the new content if the new content exists
        if model.slide_title:
            current_slide.slide_title = model.slide_title
        if model.sequential_order:
            current_slide.sequential = model.sequential_order == 'yes'
        if model.bullet_points:
            print("Updating bullet points")
            bullet_points_list = []
            # replace excerpt_id which contains a prefix with the actual excerpt_id
            for bullet_point in model.dict()['bullet_points']:
                print(f"Bullet point: {bullet_point}")
                source_excerpt_id = get_id_from_suffix(
                    excerpt_ids, bullet_point['excerpt_id']
                )
                # get excerpt text
                source_excerpt = next(
                    (doc['page_content'] for doc in reduced_docs if doc['metadata']['document_id'] == source_excerpt_id), None
                )
                # get source id
                source_id = next(
                    (doc['metadata']['source']['source_id'] for doc in reduced_docs if doc['metadata']['document_id'] == source_excerpt_id), None
                )

                bullet_points_list.append(ShortBulletContent(
                    bullet_id=uuid7str(),
                    content=bullet_point['content'],
                    excerpt=Excerpt(
                        source_id=source_id,
                        excerpt_id=source_excerpt_id,
                        text=source_excerpt
                    )
                ))
            
            current_slide.slide_content = bullet_points_list

            icon_data = await hybrid_icon_assignment([bullet_point.content for bullet_point in bullet_points_list])

            updated_bullet_points_list = []
            for bullet_point in bullet_points_list:
                print(f"Bullet point: {bullet_point.content}, Icon Name: {icon_data[bullet_point.content][0]}, Icon Source: {icon_data[bullet_point.content][1]}")
                updated_bullet_point = bullet_point.copy(update={
                    "icon": IconData(
                        name=icon_data[bullet_point.content][0],
                        source=icon_data[bullet_point.content][1]
                    )
                })
                updated_bullet_points_list.append(updated_bullet_point)
            
            current_slide.slide_content = updated_bullet_points_list
            print(f"Bullet points: {updated_bullet_points_list}")

        current_slide.generation_messages = messages
    elif slide_type == 'markdown_slide':
        model, messages = await edit_markdown_slide(current_slide.slide_title, current_slide.slide_content, instruction, current_slide.generation_messages, excerpt_ids)
        print(f"Model: {model.dict()}")
        if model.slide_title:
            current_slide.slide_title = model.slide_title
        if getattr(model, 'footnotes', None):
            new_footnotes = {}

            for old_footnote in model.dict()['footnotes']:
                excerpt_id = get_id_from_suffix(
                    excerpt_ids, old_footnote['excerpt_id'])
                source_excerpt = next(
                    (doc['page_content'] for doc in reduced_docs if doc['metadata']['document_id'] == excerpt_id), None)
                source_id = next(
                    (doc['metadata']['source']['source_id'] for doc in reduced_docs if doc['metadata']['document_id'] == excerpt_id), None)
                new_footnotes[str(old_footnote['marker'])] = { # map keys in dynamodb must be strings
                    'excerpt_id': excerpt_id,
                    'source_id': source_id,
                    'text': source_excerpt
                }

            current_slide.slide_content['footnotes'] = new_footnotes
        if model.markdown_content:
            assert type(model.markdown_content) == str
            cleaned_markdown = clean_markdown(
                model.markdown_content, current_slide.slide_title)
            assert type(cleaned_markdown) == str
            current_slide.slide_content['content'] = cleaned_markdown
        current_slide.generation_messages = messages

    elif slide_type == 'simple_mermaid_slide':
        print("Editing Simple Mermaid Slide")

        model, messages = await edit_mermaid_slide(current_slide.slide_title, current_slide.slide_content, instruction, current_slide.generation_messages, excerpt_ids)

        if model.slide_title:
            current_slide.slide_title = model.slide_title

        if model.excerpt_ids:
            diagram_excerpts = []
            for excerpt_id in model.dict()['excerpt_ids']:
                source_excerpt_id = get_id_from_suffix(
                    excerpt_ids, excerpt_id['excerpt_id'])
                source_excerpt = next(
                    (doc['page_content'] for doc in reduced_docs if doc['metadata']['document_id'] == source_excerpt_id), None)
                source_id = next(
                    (doc['metadata']['source']['source_id'] for doc in reduced_docs if doc['metadata']['document_id'] == source_excerpt_id), None)
                diagram_excerpts.append(Excerpt(
                    excerpt_id=source_excerpt_id,
                    source_id=source_id,
                    text=source_excerpt
                ))

            current_slide.slide_content['excerpts'] = diagram_excerpts

        if model.mermaid_diagram:
            light_svg, dark_svg = await process_diagram_to_svgs(model.mermaid_diagram)

            current_slide.slide_content['mermaid_code'] = model.mermaid_diagram
            current_slide.slide_content['light_svg'] = light_svg
            current_slide.slide_content['dark_svg'] = dark_svg

        current_slide.generation_messages = messages

    # print(f"Updated slide: {current_slide.dict()}")

    # update the slide in the PersistentSlideList and DynamoDB
    await update_slides(current_slide, True)

    # return the updated slide and the messages
    return current_slide, model.message_to_user
