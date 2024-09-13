from slides.xml_instructor import get_basemodel_instance_from_llm
from backend.database_models import Slide
from math import floor
from pydantic import BaseModel, Field
from llm_clients import content_gen_client, content_gen_model


slide_type_descriptions = {
    'short_bullets_slide': 'Icon Node Slide (This slide type has a title and 2-5 nodes, each with an icon and a short text description (<=80 chars). The nodes can be arranged in a list or a grid, and arrows can be displayed between the nodes to indicate sequentiality. The layout and arrangement of the title and nodes are determined by the content and number of nodes.)',
    'markdown_slide': 'Markdown Slide (A slide with a title and markdown content. The title is displayed above the markdown content. The markdown content typically includes either headings and bullet points or a table. Images are not supported. Icons are not supported, but emojis can be used.)',
    'section_header_slide': 'Section Header Slide (A slide with a section title and an image. The image can be positioned on the left or right side of the slide.)',
    'presentation_title_slide': 'Presentation Title Slide (A slide with the presentation title and an image. The image is displayed as the background of the entire slide, and the title is overlaid on top of it.)',
    'simple_mermaid_slide': 'Mermaid Diagram Slide (A slide with a title and a mermaid diagram. The title is displayed right above the mermaid diagram.)',
}


async def get_notes_for_slide(presentation_topic: str, target_audience: str, presentation_goal: str, section_title: str, slide: Slide, writing_style_instructions: str, max_length: int = 430) -> str:
    approx_max_words = max_length // 4.7

    section_title_line = f"Section Title: <section_title>{section_title}</section_title>\n" if section_title else ''

    prompt = f"""\
You are tasked with generating presenter notes for a specific slide in a PowerPoint presentation. Your goal is to create concise, informative notes that will help the presenter deliver engaging and effective content that aligns with the presentation's overall purpose and resonates with the target audience.
Here's the context for the presentation:
Presentation Topic: <presentation_topic>{presentation_topic}</presentation_topic>
Target Audience: <target_audience>{target_audience}</target_audience>
Presentation Goal: <presentation_goal>{presentation_goal}</presentation_goal>
{section_title_line}
The specific slide you're writing presenter notes for is:

Slide Type and Info: <slide_type_info>{slide_type_descriptions.get(slide.slide_type, 'Custom Slide')}</slide_type_info>
Slide Title: <slide_title>{slide.slide_title}</slide_title>

The content of the slide is as follows:
<slide_content>
</slide_content>
When writing the presenter notes, please adhere to these writing style instructions:
<writing_style>
{writing_style_instructions}
</writing_style>
Your presenter notes should include:

Key points to emphasize about the slide content
Suggestions for how to introduce the slide and relate it to the overall presentation
Potential questions to pose to the audience or points of interaction
Reminders about body language or delivery style
Transitions to the next slide or topic

Make sure the notes address the target audience appropriately and help maintain their interest. The notes should be concise yet informative, providing guidance for verbal delivery alongside the visual slide.
Remember to strictly follow the writing style instructions provided and ensure that your notes accurately reflect the content of the slide. Do not add new information that isn't present in the slide content.
Please write your presenter notes inside <presenter_notes> tags. Aim for bullet points or short phrases that are easy for the presenter to glance at during the presentation. The total length should typically be around {floor(0.85 * approx_max_words)}-{floor(approx_max_words * 0.95)} words."""

    class SlideScript(BaseModel):
        slide_script: str = Field(..., min_length=1, max_length=10)

    class Response(BaseModel):
        slide_scripts: List[SlideScript] = Field(..., min_items=5, max_items=5)

    response, messages = await get_basemodel_instance_from_llm(
        client=content_gen_client,
        pydantic_model_class=Response,
        max_iterations=5,
        model=content_gen_model,
        max_tokens=2000,
        messages={'role': 'user', 'prompt': prompt},
    )

    return response.presenter_notes
