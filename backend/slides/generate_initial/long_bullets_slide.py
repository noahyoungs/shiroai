from pydantic import BaseModel, Field
from typing import List
from slides.generate_initial.utils import get_id_from_suffix, get_research_xml
from slides.xml_instructor import generate_variable_input_xml, get_basemodel_instance_from_llm, create_dynamic_enum_validator
from uuid_extensions import uuid7str
from database_models import MarkdownSlide
from slides.clean_markdown import clean_markdown
from llm_clients import content_gen_client, content_gen_model

async def get_long_bullets_slide(presentation_id, presentation_xml, subtopic_xml, reduced_docs, slide_idea, excerpt_ids):
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

    prompt = f"""
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

For each fact you include, you must add a footnote reference (e.g. [^1]) in the markdown text in your <markdown_content></markdown_content> tag.
Then, in a <footnotes></footnotes> tag, include a list of <footnote></footnote> each with a <marker></marker> and an <excerpt_id></excerpt_id>. The <marker></marker> should be ONLY THE NUMBER of the footnote reference in the bullet point content (e.g. 1), and the <excerpt_id></excerpt_id> should be A SINGLE <excerpt_id></excerpt_id> of the <excerpt></excerpt> from the <research></research> above that supports the fact. Each <footnote></footnote> can only include one <excerpt_id></excerpt_id> and one <marker></marker>, but you can reference more than one <footnote></footnote> in the <markdown_content></markdown_content> tag like this: [^1][^2][^3].
Do not include a list of footnotes at the end of the <markdown_content></markdown_content>, just give us the <footnotes></footnotes> tag with all the <footnote></footnote> tags inside it.

Please respond in the following XML format:
{generate_variable_input_xml(CompletionLongBulletsSlide)}

Make sure you consider not just the <slide_title></slide_title>, but also the <subtopic></subtopic>, and the <topic></topic>, <audience></audience> and <goal></goal> of the <presentation></presentation> we mentioned earlier when creating the bullet points.
Remember you must cite an excerpt id as a source for every bullet point, so you can only use information found in our research."""

    messages = [{'role': 'user', 'content': prompt}]

    long_bullets_slide, messages = await get_basemodel_instance_from_llm(
        client=content_gen_client,
        pydantic_model_class=CompletionLongBulletsSlide,
        max_iterations=5,
        dynamic_val_params={"valid_ids": id_suffixes},
        model=content_gen_model,
        max_tokens=2000,
        messages=messages,
        temperature=0.5,
    )

    new_footnotes = {}

    for old_footnote in long_bullets_slide.dict()['footnotes']:
        excerpt_id = get_id_from_suffix(
            excerpt_ids, old_footnote['excerpt_id'])
        source_excerpt = next(
            (doc['page_content'] for doc in reduced_docs if doc['metadata']['document_id'] == excerpt_id), None)
        source_id = next((doc['metadata']['source']['source_id']
                         for doc in reduced_docs if doc['metadata']['document_id'] == excerpt_id), None)
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
        presentation_id=presentation_id,
        slide_title=slide_idea['slide_title'],
        slide_id=uuid7str(),
        generation_messages=messages,
        slide_type='markdown_slide',
        slide_content=slide_content
    )