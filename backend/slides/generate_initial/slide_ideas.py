from pydantic import BaseModel, Field
from typing import List, Literal
from slides.xml_instructor import generate_variable_input_xml, get_basemodel_instance_from_llm
from llm_clients import content_gen_client, content_gen_model


async def get_slide_ideas(presentation_xml, subtopic_xml, research_xml):
    class Slide(BaseModel):
        slide_type: Literal["short_bullets_slide", "long_bullets_slide",
                            "markdown_table_slide", "simple_mermaid_slide"]
        slide_title: str = Field(..., min_length=5, max_length=75)
        slide_content_idea: str = Field(..., min_length=20, max_length=600)

    class SlideList(BaseModel):
        slides: List[Slide] = Field(..., min_items=1, max_items=4)

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

    prompt = f"""
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
{generate_variable_input_xml(SlideList)}

Make sure you consider not just the <subtopic></subtopic>, but also the <topic></topic>, the <audience></audience> and the <goal></goal> of the <presentation></presentation> we mentioned earlier when creating the slides.
Remember, the <slide_content_idea></slide_content_idea> is not the actual content of the slide, but a description of what the slide could contain. It should be written in plain English and be less than 100 words long."""

    messages = [{'role': 'user', 'content': prompt}]

    slide_list, messages = await get_basemodel_instance_from_llm(
        client=content_gen_client,
        pydantic_model_class=SlideList,
        max_iterations=5,
        model=content_gen_model,
        max_tokens=2000,
        messages=messages,
    )

    return slide_list.model_dump()['slides']