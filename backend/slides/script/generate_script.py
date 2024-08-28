from slides.xml_instructor import get_basemodel_instance_from_llm, generate_variable_input_xml
from slides.slide_models import Slide, Topic
from slides.slide_to_xml import slide_content_to_xml
from slides.script.script_styles import generate_xml_for_style
from pydantic import BaseModel, Field
from math import floor
from portkey_ai import AsyncPortkey
from slides.persistent_slide_list import PersistentSlideList
from slides.slide_models import Slide, Topic
from typing import List, Dict, Any, Callable
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

def trim_messages(messages: List[Dict[str, str]], min_length: int = 5):
    """Trim messages to a minimum length, ensuring the last message has role 'user'."""
    
    if len(messages) <= min_length:
        return messages
    else:
        i = -1 * min_length
        while True:
            if messages[i]['role'] == 'user':
                return messages[i:]
            i -= 1
        
    

async def yield_scripts_for_presentation(presentation_topic: str, target_audience: str, presentation_goal: str, slides: List[Slide], topics: List[Topic], style_preset: str, custom_style: str = None, max_char_per_slide: int = 588):
    approx_max_words = max_char_per_slide // 4.7

        
    class Response(BaseModel):
        slide_script: str = Field(..., min_length=1, max_length=max_char_per_slide)
        
    writing_style_instructions = generate_xml_for_style(style_preset) if custom_style is None else f"A custom style requested by the user: {custom_style}"
    
    messages = []
    script_strings = []
    
    for i, slide in enumerate(slides):

        slide_content = slide_content_to_xml(slide, topics)
        print(f"Slide content for slide {i+1}/{len(slides)}:\n{slide_content}")
        
        init_prompt = f"""\
Hi there, You are tasked with generating a script for a PowerPoint presentation. This script must be written in a way that allows the presenter to read it verbatim during the presentation. Follow these instructions carefully to create an engaging and effective presentation script.

First, review the key information for the presentation:

Presentation Title: <presentation_title>{presentation_topic}</presentation_title>

Target Audience: <target_audience>{target_audience}</target_audience>

Presentation Goal: <presentation_goal>{presentation_goal}</presentation_goal>

The writing style for the script should be: <writing_style>{writing_style_instructions}</writing_style>.
Adapt your language and tone to match this style throughout the script.

You are writing the presentation script one slide at a time. We are now looking at the first slide, which is the presentation title slide. There are {len(slides)} slides in total.
Heres the content on the first slide:
<slide_content>
{slide_content}
</slide_content>

Each slide's script must not exceed <max_characters>{max_char_per_slide}</max_characters> characters. That's about {approx_max_words} words per slide.

When writing the script for the first slide, follow these guidelines:
1. Introduce the topic and set the stage for the presentation, paying attention to the target audience and presentation goal.
2. Follow the writing style instructions provided and maintain a consistent tone throughout the script.

Your output should be formatted as follows:
- Respond with a single <slide_script></slide_script> tag, containing the script for the first slide.
- Ensure the content within the <slide_script></slide_script> tag does not exceed the specified character limit ({max_char_per_slide}).

Important note: The script must be written in a way that allows the presenter to read it verbatim during the presentation. Do not include cues, annotations, or any text that should not be read aloud. The presenter is a complete airhead and needs to be told exactly what to say. If you include any text that should not be read aloud, like \"[Pause]\" the presenter will read it aloud, and it will be awkward.

Additional tips for effective presentation scripting:
- Use clear and concise language to convey ideas efficiently.
- Incorporate rhetorical questions or thought-provoking statements to engage the audience.
- Balance the amount of information per slide to maintain audience interest.
- Ensure that the script flows naturally and maintains a coherent narrative throughout the presentation.

Remember, the goal is to create a script that sounds natural when read verbatim and effectively communicates the presentation's key messages to the target audience.

Response Format:
{generate_variable_input_xml(Response)}

Begin writing the script for the first slide, adhering to the guidelines and format specified above."""

        rep_prompt = f"""\
That's Great! We can now move on to the next slide.

First, lets review the key information for the presentation:

Presentation Title: <presentation_title>{presentation_topic}</presentation_title>

Target Audience: <target_audience>{target_audience}</target_audience>

Presentation Goal: <presentation_goal>{presentation_goal}</presentation_goal>

The writing style for the script should be: <writing_style>{writing_style_instructions}</writing_style>.
As before, remember to adapt your language and tone to match this style throughout the script.

We are now looking at slide {i+1} of {len(slides)}.
Here's the content for this slide:
<slide_content>
{slide_content}
</slide_content>

Remember, each slide's script must not exceed <max_characters>{max_char_per_slide}</max_characters> characters. That's about {approx_max_words} words per slide. If you go over the character limit, you'll need to revise the script.

When writing the script, follow these guidelines:
1. Begin with a smooth transition from the previous slide.
2. Clearly explain the main points of each slide in a conversational manner.
3. Use language that is appropriate for the target audience and aligns with the specified writing style.
4. Reference text or visual elements on the slides when appropriate.

Your output should be formatted as follows:
- Respond with a single <slide_script></slide_script> tag, containing the script for slide {i+1}/{len(slides)}.
- Ensure the content within the <slide_script></slide_script> tag does not exceed the specified character limit ({max_char_per_slide}).

Additional tips for effective presentation scripting:
- Use clear and concise language to convey ideas efficiently.
- Incorporate rhetorical questions or thought-provoking statements to engage the audience.
- Balance the amount of information per slide to maintain audience interest.
- Ensure that the script flows naturally and maintains a coherent narrative throughout the presentation.

Remember, the presenter is an airhead and will read aloud every single word in the script. Your goal is to create a script that sounds natural when read verbatim and effectively communicates the presentation's key messages to the target audience.

Response Format:
{generate_variable_input_xml(Response)}

Begin writing the script for slide {i+1}/{len(slides)}, adhering to the guidelines and format specified above."""

        try: 
            response, messages = await get_basemodel_instance_from_llm(
                client=bedrock_client,
                pydantic_model_class=Response,
                max_iterations=5,
                model=claude_haiku,
                max_tokens=100000,
                messages=trim_messages(messages + [{'role':'user', 'content': init_prompt if i == 0 else rep_prompt}]),
                error_message_prefix=f"There was an issue with the response you provided. Please fix the issue below and respond again with the <slide_script></slide_script> for slide {i+1}.",
            )
        except Exception as e:
            print(f"Error generating script for slide {i+1}/{len(slides)}")
            traceback.print_exc()
            script_strings.append(None)
            yield slide, None
        
        yield slide, response.slide_script
    

async def generate_all_scripts(psl: PersistentSlideList, interface_data: Any, emitter: Callable[[Any], None],  style_key: int = 0, custom_style: str = None, max_char_per_slide: int = None):
    print(f"Generating scripts for presentation {psl.presentation_id}, style {style_key}, custom style {custom_style}, max characters per slide {max_char_per_slide}")
    topics: List[Topic] = await get_all_topics(psl.presentation_id)
    presentation = await get_presentation(psl.presentation_id, ['topic', 'audience', 'goal'])
    
    slides_l: List[Slide] = psl.convert_to_array()

    # initial update for progress bar
    interface_data["script"]["status"] = f"0/{len(slides_l)}"

    i = 0
    async for slide, script in yield_scripts_for_presentation(
        presentation_topic=presentation['topic'],
        target_audience=presentation['audience'],
        presentation_goal=presentation['goal'],
        slides=slides_l,
        topics=topics,
        style_preset=style_key,
        custom_style=custom_style,
        max_char_per_slide=max_char_per_slide
    ):
        await psl.update_slides({
            'id': slide.id,
            'script': script
        })  
        # update status in interfaceData for progress bar
        interface_data["script"]["status"] = f"{i+1}/{len(slides_l)}"
        # emit interface update with new status
        await emitter(data=interface_data)
        print(f"Script generated for slide {slide.id} ({i}/{len(slides_l)})")
        i += 1
    
    print("All scripts generated and updated")