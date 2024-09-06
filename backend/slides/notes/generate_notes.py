from slides.xml_instructor import get_basemodel_instance_from_llm, generate_variable_input_xml
from database_models import Slide, Topic
from slides.slide_to_xml import slide_content_to_xml
from slides.script.script_styles import generate_xml_for_style
from pydantic import BaseModel, Field
from math import floor
from portkey_ai import AsyncPortkey
from typing import List
from slides.persistent_slide_list import PersistentSlideList
from database_models import Slide, Topic
from typing import List
from dynamodb import get_all_topics, get_presentation
import traceback

bedrock_client = AsyncPortkey(
    virtual_key="aldeo-portkey-b-5cf75f",
    config={"cache": {"mode": "simple"},
                "retry": {
            "attempts": 3,
            "on_status_codes": [429, 500, 502, 503, 504, 424],
            }},
)
claude_haiku = "anthropic.claude-3-haiku-20240307-v1:0"

slide_type_descriptions = {
    'short_bullets_slide': 'Icon Node Slide (This slide type has a title and 2-5 nodes, each with an icon and a short text description (<=80 chars). The nodes can be arranged in a list or a grid, and arrows can be displayed between the nodes to indicate sequentiality. The layout and arrangement of the title and nodes are determined by the content and number of nodes.)',
    'markdown_slide': 'Markdown Slide (A slide with a title and markdown content. The title is displayed above the markdown content. The markdown content typically includes either headings and bullet points or a table. Images are not supported. Icons are not supported, but emojis can be used.)',
    'section_header_slide': 'Section Header Slide (A slide with a section title and an image. The image can be positioned on the left or right side of the slide.)',
    'presentation_title_slide': 'Presentation Title Slide (A slide with the presentation title and an image. The image is displayed as the background of the entire slide, and the title is overlaid on top of it.)',
    'simple_mermaid_slide': 'Mermaid Diagram Slide (A slide with a title and a mermaid diagram. The title is displayed right above the mermaid diagram.)',
}

async def get_notes_for_presentation(presentation_topic: str, target_audience: str, presentation_goal: str, slides: List[Slide], topics: List[Topic], style_preset: str, custom_style: str = None, max_char_per_slide: int = 588):
    approx_max_words = max_char_per_slide // 4.7
    
    slide_content = ""
    for slide in slides:
        slide_content += slide_content_to_xml(slide, topics) + "\n"
    
    class SlideNotes(BaseModel):
        slide_notes: str = Field(..., min_length=1, max_length=max_char_per_slide+100)
        
    class Response(BaseModel):
        speaker_notes: List[SlideNotes] = Field(..., min_items=len(slides), max_items=len(slides))
        
    writing_style_instructions = generate_xml_for_style(style_preset) if custom_style is None else f"A custom style requested by the user: {custom_style}"
        
    prompt = f"""\
You are tasked with generating speaker notes for a PowerPoint presentation. These notes should provide key talking points and reminders for the presenter. Follow these instructions carefully to create effective and concise speaker notes.

First, let's review the key information for this presentation:
Presentation Title: <presentation_title>{presentation_topic}</presentation_title>
Target Audience: <target_audience>{target_audience}</target_audience>
Presentation Goal: <presentation_goal>{presentation_goal}</presentation_goal>
The writing style for the presentation notes should be: <writing_style>{writing_style_instructions}</writing_style>.
Match this style throughout the speaker notes.

Here is the content for each slide of the presentation:
<slide_content>
{slide_content}
</slide_content>

Each slide's speaker notes must not exceed <max_characters>{max_char_per_slide}</max_characters> characters. That's about {approx_max_words} words per slide.

When writing the speaker notes, follow these guidelines:
1. Provide brief bullet points or short phrases for key talking points.
2. Include reminders about important details or statistics to mention.
3. Suggest transitions or connections to make between slides.
4. Note any specific actions the presenter should take (e.g., "Pause for questions" or "Emphasize this point").
5. Keep the notes concise and easy to glance at during the presentation.

Your output should be formatted as follows:
- Respond with a single <speaker_notes></speaker_notes> tag containing {len(slides)} <slide_notes></slide_notes> XML tags.
- You must provide a total of {len(slides)} <slide_notes></slide_notes> tags, one for each slide in the presentation.
- You must provide the <slide_notes></slide_notes> tags in the same order as the slides in the presentation.
- Ensure the content within each <slide_notes></slide_notes> tag does not exceed the specified character limit.

Additional tips for effective speaker notes:
- Use clear and concise language that's easy to read at a glance.
- Include keywords or phrases that will trigger the presenter's memory.
- Note any specific examples or anecdotes to share, without writing them out in full.
- Suggest points where the presenter might engage the audience (e.g., "Ask for audience experiences here").
- Include reminders about body language or tone where appropriate.

Remember, the goal is to create speaker notes that will support and guide the presenter, not to be read verbatim. They should enhance the presenter's delivery while allowing for a natural and engaging presentation style.

Response Format:
{generate_variable_input_xml(Response)}

Begin writing the speaker notes for each slide, adhering to the guidelines and format specified above."""

    response, messages = await get_basemodel_instance_from_llm(
        client=bedrock_client,
        pydantic_model_class=Response,
        max_iterations=5,
        model=claude_haiku,
        max_tokens=100000,
        messages=[{'role':'user', 'content':prompt}],
    )
    
    # return list of strings containing the generated notes for each slide
    notes_strings = [slide_notes.slide_notes for slide_notes in response.speaker_notes]
    return notes_strings

async def generate_all_notes(psl: PersistentSlideList, style_key: int = 0, custom_style: str = None, max_char_per_slide: int = None):
    print(f"Generating notes for presentation {psl.presentation_id}")
    topics: List[Topic] = await get_all_topics(psl.presentation_id)
    presentation = await get_presentation(psl.presentation_id, ['topic', 'audience', 'goal'])
    
    slides_l: List[Slide] = psl.convert_to_array()

    notes: List[str] = get_notes_for_presentation(
        presentation_topic=presentation['topic'],
        target_audience=presentation['audience'],
        presentation_goal=presentation['goal'],
        slides=slides_l,
        topics=topics,
        style_preset=style_key,
        custom_style=custom_style,
        max_char_per_slide=max_char_per_slide
    )
    
    if not all(note is not None for note in notes):
        print("Error generating notes: some notes are None")
        return
    
    if not all(len(notes) > 0 for script in notes):
        print("Error generating notes: some notes are empty")
        return
    
    if not len(notes) == len(slides_l):
        print(f"Error generating notes: number of notes ({len(notes)}) doesn't match number of slides ({len(slides_l)})")
        return

    update_partial_slides = [{'id': slide.id, 'speaker_notes': note} for slide, note in zip(slides_l, notes)]
    print(f"Updating {len(update_partial_slides)} slides with generated speaker notes")
    await psl.update_slides(update_partial_slides)
    print("Notes generated and updated")