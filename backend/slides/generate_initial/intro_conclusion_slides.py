import math
from slides.xml_instructor import generate_variable_input_xml, get_basemodel_instance_from_llm
from pydantic import BaseModel, Field
from typing import List, Literal
from database_models import MarkdownSlide
from uuid_extensions import uuid7str
from slides.clean_markdown import clean_markdown
from database_models import Slide
from slides.generate_initial.utils import get_presentation_xml
from slides.slide_to_xml import slides_to_xml
from llm_clients import content_gen_client, content_gen_model


def determine_slides(content_slides):
    # Calculate the min and max number of slides based on cube root
    S_min = math.floor((content_slides + 1) ** (1/3))
    S_max = math.ceil((content_slides + 1) ** (1/3))

    # Apply hard minimum and maximum constraints
    S_min = max(S_min, 1)
    S_max = min(S_max, 5)

    return (S_min, S_max)



def get_range_string(min_slides, max_slides):
    if min_slides == max_slides:
        return f"{min_slides}"
    return f"{min_slides}-{max_slides}"


async def get_intro_or_conclusion_slides(presentation_id, presentation_topic, presentation_audience, presentation_goal, slides, slide_type):
    
    presentation_xml = get_presentation_xml(presentation_topic, presentation_audience, presentation_goal)

    n_content_slides = len(slides)
    min_section_slides, max_section_slides = determine_slides(n_content_slides)

    class Slide(BaseModel):
        slide_title: str = Field(..., min_length=5, max_length=75)
        slide_markdown: str = Field(..., min_length=20, max_length=800)

    class IntroductionSlides(BaseModel):
        slides: List[Slide] = Field(..., min_items=min_section_slides,
                                    max_items=max_section_slides)

    class ConclusionSlides(BaseModel):
        slides: List[Slide] = Field(..., min_items=min_section_slides,
                                    max_items=max_section_slides)

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

    target_slides_class = IntroductionSlides if slide_type == "introduction" else ConclusionSlides

    multi_intro_prompt = f"""
You are tasked with creating {get_range_string(min_section_slides, max_section_slides)} introduction slides for a presentation based on the given information. These slides should set the stage for the presentation and engage the audience from the start. Do not create a presentation title slide, as that will be created separately.

Here are the presentation details:
{presentation_xml}

Here are the content slides you will be introducing:
{slides_to_xml(slides)}

Using this information, create {get_range_string(min_section_slides, max_section_slides)} introduction slides that will effectively set up the presentation. Each slide should have a clear title and concise content in markdown format. The introduction slides should:

1. Provide context for the presentation topic
2. Highlight the relevance to the target audience
3. Hint at the main points or benefits that will be covered
4. Create interest and set expectations for the rest of the presentation

Note that while the content slides can contain various formats like tables and diagrams, the introduction slides can only have plaintext titles and markdown content. Use bullet points in your markdown rather than complete sentences.
Format your response as follows:
{generate_variable_input_xml(target_slides_class)}

Here are some examples of effective introduction slide titles:

1. "The Challenge We Face"
2. "Why [Topic] Matters to You"
3. "Transforming [Industry] with [Solution]"
4. "Key Trends Shaping Our Future"
5. "The Opportunity Ahead"

Remember to:
- Keep the content concise and easy to read
- Use bullet points for clarity
- Ensure each slide has a clear purpose and flows logically to the next
- Tailor the language and examples to the target audience
- Align the introduction slides with the overall presentation goal
- Create intrigue and interest without giving away all the main points

Your introduction slides should seamlessly lead into the content slides provided, creating a cohesive narrative for the entire presentation."""

    single_intro_prompt = f"""\
You are tasked with creating an introduction slide for a presentation based on the given information. The slide should set the stage for the presentation and engage the audience from the start. Do not create a presentation title slide, as that will be created separately.

Here are the presentation details:
{presentation_xml}

Here are the content slides you will be introducing:
{slides_to_xml(slides)}

Using this information, create a single introduction slide that will effectively set up the presentation. The slide should have a clear title and concise content in markdown format. The introduction slide should:

1. Provide context for the presentation topic
2. Highlight the relevance to the target audience
3. Hint at the main points or benefits that will be covered
4. Create interest and set expectations for the rest of the presentation

Note that while the content slides can contain various formats like tables and diagrams, the introduction slide can only have a plaintext title and a markdown content. Use bullet points in your markdown rather than complete sentences.
Format your response as follows:
{generate_variable_input_xml(target_slides_class)}

Here are some examples of effective introduction slide titles:

1. "The Challenge We Face"
2. "Why [Topic] Matters to You"
3. "Transforming [Industry] with [Solution]"
4. "Key Trends Shaping Our Future"
5. "The Opportunity Ahead"

Remember to:
- Keep the content concise and easy to read
- Use bullet points for clarity
- Tailor the language and examples to the target audience
- Align the introduction slide with the overall presentation goal
- Create intrigue and interest without giving away all the main points

Your introduction slide should seamlessly lead into the content slides provided, creating a cohesive narrative for the entire presentation."""

    multi_conclusion_prompt = f"""\
You are tasked with creating {get_range_string(min_section_slides, max_section_slides)} conclusion slides for a presentation based on the given information. These slides should effectively wrap up the presentation and leave a lasting impression on the audience. Do not create a "Thank You" or "Questions?" slide, as that will be created separately.

Here are the presentation details:
{presentation_xml}

Here are the content slides you will be concluding:
{slides_to_xml(slides)}

Using this information, create {get_range_string(min_section_slides, max_section_slides)} conclusion slides that will effectively summarize and close the presentation. Each slide should have a clear title and concise content in markdown format. The conclusion slides should:

1. Recap the main points of the presentation
2. Reinforce the key takeaways for the audience
3. Emphasize the relevance and impact of the information presented
4. Provide a call to action or next steps (if applicable)
5. End on a memorable note that ties back to the presentation's main message

Note that while the content slides can contain various formats like tables and diagrams, the conclusion slides can only have plaintext titles and markdown content. Use bullet points in your markdown rather than complete sentences.
Format your response as follows:
{generate_variable_input_xml(target_slides_class)}

Here are some examples of effective conclusion slide titles:
1. "Key Takeaways"
2. "The Road Ahead"
3. "Putting It All Together"
4. "Your Next Steps"
5. "The Impact of [Topic]"

Remember to:
- Keep the content concise and easy to read
- Use bullet points for clarity
- Ensure each slide has a clear purpose and flows logically from the previous content
- Tailor the language and examples to the target audience
- Align the conclusion slides with the overall presentation goal
- Reinforce the main message without introducing new information

Your conclusion slides should seamlessly follow the content slides provided, creating a cohesive narrative for the entire presentation and leaving the audience with a clear understanding of the key points and their significance."""

    single_conclusion_prompt = f"""
You are tasked with creating a single conclusion slide for a presentation based on the given information. The slide should effectively wrap up the presentation and leave a lasting impression on the audience. Do not create a "Thank You" or "Questions?" slide, as that will be created separately.

Here are the presentation details:
{presentation_xml}

Here are the content slides you will be concluding:
{slides_to_xml(slides)}

Using this information, create a single conclusion slide that will effectively summarize and close the presentation. The slide should have a clear title and concise content in markdown format. The conclusion slide should:

1. Recap the main points of the presentation
2. Reinforce the key takeaways for the audience
3. Emphasize the relevance and impact of the information presented
4. Provide a call to action or next steps (if applicable)
5. End on a memorable note that ties back to the presentation's main message

Note that while the content slides can contain various formats like tables and diagrams, the conclusion slide can only have a plaintext title and a markdown content. Use bullet points in your markdown rather than complete sentences.
Format your response as follows:
{generate_variable_input_xml(target_slides_class)}

Here are some examples of effective conclusion slide titles:
1. "Key Takeaways"
2. "The Road Ahead"
3. "Putting It All Together"
4. "Your Next Steps"
5. "The Impact of [Topic]"

Remember to:
- Keep the content concise and easy to read
- Use bullet points for clarity
- Tailor the language and examples to the target audience
- Align the conclusion slide with the overall presentation goal
- Reinforce the main message without introducing new information

Your conclusion slide should seamlessly follow the content slides provided, creating a cohesive narrative for the entire presentation and leaving the audience with a clear understanding of the key points and their significance."""

    target_prompt = None
    if slide_type == "introduction":
        if min_section_slides == 1:
            target_prompt = single_intro_prompt
        else:
            target_prompt = multi_intro_prompt
    elif slide_type == "conclusion":
        if min_section_slides == 1:
            target_prompt = single_conclusion_prompt
        else:
            target_prompt = multi_conclusion_prompt

    messages = [{'role': 'user', 'content': target_prompt}]

    section_slides_list, messages = await get_basemodel_instance_from_llm(
        client=content_gen_client,
        pydantic_model_class=target_slides_class,
        max_iterations=5,
        model=content_gen_model,
        max_tokens=2000,
        temperature_multiplier=1.2,
        messages=messages,
    )

    return [
        MarkdownSlide(
            presentation_id=presentation_id,
            slide_id=uuid7str(),
            slide_type="markdown_slide",
            slide_title=slide.slide_title,
            slide_content={
                'content': clean_markdown(slide.slide_markdown, slide.slide_title),
                'footnotes': []
            },
        )
        for slide in section_slides_list.slides
    ]
