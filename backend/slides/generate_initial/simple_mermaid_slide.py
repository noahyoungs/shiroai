from pydantic import BaseModel, Field
from typing import List
from slides.generate_initial.utils import get_id_from_suffix, get_research_xml
from slides.xml_instructor import get_basemodel_instance_from_llm, create_dynamic_enum_validator
from uuid_extensions import uuid7str
from database_models import SimpleMermaidSlide
from slides.mermaid.validate_mermaid import validate_mermaid_diagram
from slides.mermaid.mermaid_to_svg import process_diagram_to_svgs
from slides.mermaid.mermaid_prompt import get_messages
from pydantic_async_validation import async_field_validator, AsyncValidationModelMixin
from llm_clients import content_gen_client, content_gen_model


async def get_simple_mermaid_slide(presentation_id, presentation_xml, subtopic_xml, reduced_docs, slide_idea, excerpt_ids):
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
        client=content_gen_client,
        pydantic_model_class=CompletionMermaidSlide,
        max_iterations=5,
        model=content_gen_model,
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
            (doc['page_content'] for doc in reduced_docs if doc['metadata']['document_id'] == source_excerpt_id), None)
        source_id = next((doc['metadata']['source']['source_id']
                         for doc in reduced_docs if doc['metadata']['document_id'] == source_excerpt_id), None)
        diagram_excerpts.append({
            'excerpt_id': source_excerpt_id,
            'source_id': source_id,
            'text': source_excerpt
        })

    light_svg, dark_svg = await process_diagram_to_svgs(simple_mermaid_slide.mermaid_diagram)

    return SimpleMermaidSlide(
        presentation_id=presentation_id,
        slide_title=slide_idea['slide_title'],
        slide_id=uuid7str(),
        generation_messages=messages[-2:],
        slide_type='simple_mermaid_slide',
        slide_content={
            'mermaid_code': simple_mermaid_slide.mermaid_diagram,
            'excerpts': diagram_excerpts,
            'light_svg': light_svg,
            'dark_svg': dark_svg
        }
    )