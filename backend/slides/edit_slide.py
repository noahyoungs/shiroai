# Short Bullets Slide

from typing import List, Literal
from pydantic import BaseModel, Field, Optional
from pydantic_async_validation import AsyncValidationModelMixin, async_field_validator
from backend.slides.clean_markdown import clean_markdown
from backend.slides.mermaid.mermaid_to_svg import process_diagram_to_svgs
from backend.slides.xml_instructor import create_dynamic_enum_validator, generate_variable_input_xml, get_basemodel_instance_from_llm, generate_xml_from_instance
from portkey_ai import AsyncPortkey
from dotenv import load_dotenv
from slides.mermaid.validate_mermaid import validate_mermaid_diagram
from dynamodb import get_slide, update_slide
from backend.slides.icons.icon_similarity_search import hybrid_icon_assignment


load_dotenv()

# initialize LLM
bedrock_client = AsyncPortkey(
    virtual_key="aldeo-portkey-b-5cf75f",
    # config={"cache": {"mode": "simple"}},
)

llama3_8b = "llama3-8b-8192"
claude_haiku = "anthropic.claude-3-haiku-20240307-v1:0"

class Footnote(BaseModel):
    marker: int = Field(..., ge=1)
    excerpt_id: str = Field(..., min_length=8, max_length=8)
    
    validate_excerpt_id = create_dynamic_enum_validator('valid_ids', 'excerpt_id')
    
class MarkdownSlide(BaseModel):
    markdown_content: str = Field(..., min_length=1, max_length=2000)
    footnotes: List[Footnote]
    
# Mermaid Slide

class ExcerptId(BaseModel):
    excerpt_id: str = Field(..., min_length=8, max_length=8)
    validate_excerpt_id = create_dynamic_enum_validator('valid_ids', 'excerpt_id')

class MermaidSlide(AsyncValidationModelMixin, BaseModel):
    reasoning: str
    mermaid_diagram: str
    excerpt_ids : List[ExcerptId]
    
def get_excerpt_ids(reduced_docs):
    excerpt_ids = [doc['metadata']['id'] for doc in reduced_docs]
    return excerpt_ids

def get_id_from_suffix(excerpt_ids, suffix):
    return next((id for id in excerpt_ids if id.endswith(suffix)), None)

async def edit_sbs(slide_title, slide_content, sequential, instruction, messages, excerpt_ids):
    
    id_suffixes = [id[-8:] for id in excerpt_ids]
    
    class BulletPoint(BaseModel):
        content: str = Field(..., min_length=1, max_length=80)
        excerpt_id: Optional[str] = Field(None, min_length=8, max_length=8)
        
        validate_excerpt_id = create_dynamic_enum_validator('valid_ids', 'excerpt_id')

    class ShortBulletsSlide(BaseModel):
        slide_title: Optional[str] = Field(None, min_length=5, max_length=75)
        bullet_points: List[BulletPoint] = Field(..., min_items=2, max_items=5)
        sequential_order: Optional[Literal["yes", "no"]] = None
        message_to_user: str
    
    class OldShortBulletsSlide(BaseModel):
        slide_title: Optional[str] = Field(None, min_length=5, max_length=75)
        bullet_points: List[BulletPoint] = Field(..., min_items=2, max_items=5)
        sequential_order: Optional[Literal["yes", "no"]] = None
        
    
    old_sbs = OldShortBulletsSlide.model_validate({
        "slide_title": slide_title,
        "bullet_points": [{"content": bp['content'], "excerpt_id": bp['excerpt']['excerpt_id'][-8:]} for bp in slide_content],
        "sequential_order": "yes" if sequential else "no"
    })
    
    prompt = f"""\
Here's the slide we have so far:
{generate_xml_from_instance(old_sbs)}

<system_requirements>
Remember that the slide has to have 2-5 short bullet points to go on this slide. Each bullet point should be 10 words or less and the bullet points cannot be nested.
Do not include `* `, `- `, or leading numbers in your bullet point, just the text.
The slide title must be between 5 and 75 characters.
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

    messages = messages + [{'role': 'user', 'content': prompt}]
        
    short_bullets_slide, new_messages = await get_basemodel_instance_from_llm(
        client=bedrock_client,
        pydantic_model_class=ShortBulletsSlide,
        max_iterations=5,
        force_start_with_first_tag=False,
        model=claude_haiku,
        max_tokens=2000,
        messages=messages,
        dynamic_val_params={"valid_ids": id_suffixes},
        error_prompt_suffix="\nIf this error was caused because the user request conflicted with the system requirements, please fix your response to adhere to the system requirements and in your <message_to_user></message_to_user> tag, explain to the user why you couldn't meet the user request due to the system requirements.",
    )
    
    return short_bullets_slide, new_messages

async def edit_markdown_slide(slide_title, slide_content, instruction, messages, excerpt_ids):
    
    id_suffixes = [id[-8:] for id in excerpt_ids]
    
    class Footnote(BaseModel):
        marker: int = Field(..., ge=1)
        excerpt_id: str = Field(..., min_length=8, max_length=8)
        
        validate_excerpt_id = create_dynamic_enum_validator('valid_ids', 'excerpt_id')
    
    class MarkdownSlide(BaseModel):
        slide_title: Optional[str] = Field(None, min_length=5, max_length=75)
        markdown_content: Optional[str] = Field(..., min_length=1, max_length=2000)
        footnotes: Optional[List[Footnote]]
        message_to_user: str
    
    class OldMarkdownSlide(BaseModel):
        slide_title: Optional[str] = Field(None, min_length=5, max_length=75)
        markdown_content: str = Field(..., min_length=1, max_length=2000)
        footnotes: List[Footnote]
        
    old_mds = OldMarkdownSlide.model_validate({
        "slide_title": slide_title,
        "markdown_content": slide_content['content'],
        "footnotes": [{"marker": int(marker), "excerpt_id": excerpt['excerpt_id'][-8:]} for marker, excerpt in slide_content['footnotes'].items()]
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

If you update the <markdown_content>, make sure you keep the footnote references (e.g. [^1]) in the markdown content up to date and update the <footnotes></footnotes> tag accordingly.

To update the <footnotes></footnotes>, include a <footnotes></footnotes> tag with the new footnotes in your response. If you don't include the a <footnotes></footnotes> tag, the current footnotes will be kept.
If you do include a <footnotes></footnotes> tag, you must include a list of <footnote></footnote> tags inside the <footnotes></footnotes> tag. In each <footnote></footnote> tag, include a <marker></marker> and an optional <excerpt_id></excerpt_id> to cite a source from the research whenever appropriate. The <marker></marker> must be an integer (e.g. 1) that corresponds to the footnote reference (e.g. [^1]) in the markdown content. The <excerpt_id></excerpt_id> must match one of the <excerpt_id></excerpt_id> tags in the <research><research>.
Note that if you include the <footnotes></footnotes> tag, the current <footnotes></footnotes> will be replaced entirely by the new ones you provide.

Finally, include a <message_to_user></message_to_user> tag with a message to the user explaining the changes you made to the slide.
Remember, there should be up to date footnote references in the format [^1], [^2], etc. in the <markdown_content></markdown_content> and the <marker></marker> in the <footnotes></footnotes> should correspond to these references. The <excerpt_id></excerpt_id> in the <footnotes></footnotes> should be a valid <excerpt_id></excerpt_id> from the <research></research>.
"""

    messages = messages + [{'role': 'user', 'content': prompt}]
    markdown_slide, new_messages = await get_basemodel_instance_from_llm(
        client=bedrock_client,
        pydantic_model_class=MarkdownSlide,
        max_iterations=5,
        force_start_with_first_tag=False,
        model=claude_haiku,
        max_tokens=2000,
        messages=messages,
        dynamic_val_params={"valid_ids": id_suffixes},
        error_prompt_suffix="\nIf this error was caused because the user request conflicted with the system requirements, please fix your response to adhere to the system requirements and in your <message_to_user></message_to_user> tag, explain to the user why you couldn't meet the user request due to the system requirements.",
    )
    
    return markdown_slide, new_messages

async def edit_mermaid_slide(slide_title, diagram, instruction, messages, excerpt_ids):
    
    id_suffixes = [id[-8:] for id in excerpt_ids]
    
    class ExcerptId(BaseModel):
        excerpt_id: str = Field(..., min_length=8, max_length=8)
        validate_excerpt_id = create_dynamic_enum_validator('valid_ids', 'excerpt_id')

    class Response(AsyncValidationModelMixin, BaseModel):
        slide_title: Optional[str]
        reasoning: str
        mermaid_diagram: str
        excerpt_ids : Optional[List[ExcerptId]]
        
        @async_field_validator('mermaid_diagram')
        async def validate_mermaid(self, value: str):
            is_valid, message = await validate_mermaid_diagram(value)
            if not is_valid:
                raise ValueError(f"There was a syntax error in your mermaid diagram. Please fix the syntax error:\n{message}")
            return value
        
    old_mermaid_slide = Response.model_validate({
        "slide_title": slide_title,
        "reasoning": "The mermaid diagram is a visual representation of the information in the research provided.",
        "mermaid_diagram": diagram,
        "excerpt_ids": [ExcerptId(excerpt_id=ex_id) for ex_id in excerpt_ids]
    })

    prompt = f"""\
Here's the mermaid diagram slide content we have so far:
{generate_xml_from_instance(old_mermaid_slide)}

The user has requested the following changes to the markdown diagram.
<user_request>{instruction}</user_request>

Please make the requested changes to the markdown diagram. 
Respond in the following format:
{generate_variable_input_xml(Response)}"""

    messages = messages + [{'role': 'user', 'content': prompt}]
    markdown_slide, new_messages = await get_basemodel_instance_from_llm(
        client=bedrock_client,
        pydantic_model_class=Response,
        max_iterations=5,
        force_start_with_first_tag=False,
        model=claude_haiku,
        max_tokens=2000,
        messages=messages,
        temperature=1.0,
        dynamic_val_params={"valid_ids": id_suffixes},
        error_prompt_suffix="\nIf this error was caused because the user request conflicted with the system requirements, please fix your response to adhere to the system requirements and in your <message_to_user></message_to_user> tag, explain to the user why you couldn't meet the user request due to the system requirements.",
    )
    
    return markdown_slide, new_messages

async def edit_slide(presentation_id, slide_id, instruction):
    slide = await get_slide(presentation_id, slide_id)
    
    slide_type = slide['slide_type']
    excerpt_ids = slide['excerpt_ids']
    
    if slide_type == 'short_bullets_slide':
        model, messages = await edit_sbs(slide['slide_title'], slide['slide_content'], slide['sequential'], instruction, slide['generation_messages'], excerpt_ids)
        
        # Update the slide with the new content if the new content exists
        if model.slide_title:
            slide['slide_title'] = model.slide_title
        if model.sequential_order:
            slide['sequential'] = model.sequential_order == 'yes'
        if model.bullet_points:
            bullet_points_list = []
            # replace excerpt_id which contains a prefix with the actual excerpt_id
            for bullet_point in model.dict()['bullet_points']:
                source_excerpt_id = get_id_from_suffix(excerpt_ids, bullet_point['excerpt_id'])
                # get excerpt text
                source_excerpt = next((doc['page_content'] for doc in slide['reduced_docs'] if doc['metadata']['id'] == source_excerpt_id), None)
                # get source id
                source_id = next((doc['metadata']['source']['id'] for doc in slide['reduced_docs'] if doc['metadata']['id'] == source_excerpt_id), None)

                bullet_points_list.append({
                    'content': bullet_point['content'],
                    'excerpt': {
                        'source_id': source_id,
                        'excerpt_id': source_excerpt_id,
                        'text': source_excerpt
                    }
                })
                slide['slide_content'] = bullet_points_list
        
            icon_data = await hybrid_icon_assignment([bullet_point['content'] for bullet_point in bullet_points_list])

            for dict in bullet_points_list:
                dict['icon'] =  { 'name': icon_data[dict['content']][0],
                                'source': icon_data[dict['content']][1] }
        
        slide['generation_messages'] = messages
        
    elif slide_type == 'markdown_slide':
        model, messages = await edit_markdown_slide(slide['slide_title'], slide['slide_content'], instruction, slide['generation_messages'], excerpt_ids)
        
        if model.slide_title:
            slide['slide_title'] = model.slide_title
        if model.footnotes:
            new_footnotes = {}
    
            for old_footnote in model.dict()['footnotes']:
                excerpt_id = get_id_from_suffix(excerpt_ids, old_footnote['excerpt_id'])
                source_excerpt = next((doc['page_content'] for doc in slide['reduced_docs'] if doc['metadata']['id'] == excerpt_id), None)
                source_id = next((doc['metadata']['source']['id'] for doc in slide['reduced_docs'] if doc['metadata']['id'] == excerpt_id), None)
                new_footnotes[old_footnote['marker']] = {
                        'excerpt_id': excerpt_id,
                        'source_id': source_id,
                        'text': source_excerpt
                    }
            
            slide['slide_content']['footnotes'] = new_footnotes
        if model.markdown_content:
            slide['slide_content']['content'] = clean_markdown(model.markdown_content, slide['slide_title']),
        
        slide['generation_messages'] = messages
        
    elif slide_type == 'simple_mermaid_slide':
        
        model, messages = await edit_mermaid_slide(slide['slide_title'], slide['slide_content'], instruction, slide['generation_messages'], excerpt_ids)
        
        if model.slide_title:
            slide['slide_title'] = model.slide_title
        
        if model.excerpt_ids:
            diagram_excerpts = []
            for excerpt_id in model.dict()['excerpt_ids']:
                source_excerpt_id = get_id_from_suffix(excerpt_ids, excerpt_id['excerpt_id'])
                source_excerpt = next((doc['page_content'] for doc in slide['reduced_docs'] if doc['metadata']['id'] == source_excerpt_id), None)
                source_id = next((doc['metadata']['source']['id'] for doc in slide['reduced_docs'] if doc['metadata']['id'] == source_excerpt_id), None)
                diagram_excerpts.append({
                    'excerpt_id': source_excerpt_id,
                    'source_id': source_id,
                    'text': source_excerpt
                })
                
            slide['slide_content']['excerpts'] = diagram_excerpts
           
        if model.mermaid_diagram:    
            light_svg, dark_svg = await process_diagram_to_svgs(model.mermaid_diagram)
            
            slide['slide_content']['mermaid_code'] = model.mermaid_diagram
            slide['slide_content']['light_svg'] = light_svg
            slide['slide_content']['dark_svg'] = dark_svg
        
        slide['generation_messages'] = messages
        
    await update_slide(presentation_id, slide_id, **slide)
    
    return slide, model['message_to_user']

            
