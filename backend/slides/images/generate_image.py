import base64
import os
from PIL import Image
from io import BytesIO
from dotenv import load_dotenv
from slides.xml_instructor import get_basemodel_instance_from_llm, generate_variable_input_xml
from pydantic import BaseModel
from typing import List, Literal
from portkey_ai import AsyncPortkey
from dotenv import load_dotenv
from s3 import upload_bytes_to_s3
from dynamodb import update_slides
import aiohttp
import ssl
import certifi
import asyncio
from uuid_extensions import uuid7str
import ssl
import httpx

load_dotenv()

# Constants for thumbnail sizes
THUMBNAIL_SIZE_FULL = (320, 180)
THUMBNAIL_SIZE_SQUARE = (180, 180)

stability_styles_guidance = """\
1. 3d-model
    - Description: Realistic or semi-realistic images with depth, perspective, and detailed textures, often created using 3D modeling software.
    - Themes: Architectural design, product presentations, technical demonstrations, virtual tours, and futuristic concepts.

2. analog-film
    - Description: Images that mimic the grain, color saturation, and imperfections of traditional film photography. Has a 1930s-1960s film aesthetic.
    - Themes: Historical events, nostalgic themes, retro advertising, travel logs, and vintage fashion.

3. anime
    - Description: Stylized, colorful, and often exaggerated imagery with influences from Japanese animation.
    - Themes: Pop culture, storytelling, youth-oriented content, fantasy worlds, and character-driven narratives.

4. cinematic
    - Description: Dramatic images with careful attention to lighting, composition, and color grading, resembling movie stills. Has a 1970s-1990s film aesthetic.
    - Themes: Movie or TV show analyses, storytelling, dramatic events, high-impact marketing, and emotional appeals.

5. comic-book
    - Description: Bold, graphic imagery with strong lines, vibrant colors, and often text elements like speech bubbles or captions.
    - Themes: Superhero stories, pop culture, storytelling, educational content for kids, and lighthearted or humorous topics.

8. fantasy-art
    - Description: Imaginative and often otherworldly imagery featuring mythical creatures, magical landscapes, and fantastical elements.
    - Themes: Fantasy storytelling, mythology, game design, speculative fiction, and creative brainstorming sessions.

9. isometric
    - Description: 3D representations in a 2D format with a consistent angle, often used for technical and architectural drawings.
    - Themes: Technical illustrations, architectural designs, urban planning, infographics, and data visualization.

10. line-art
    - Description: Artistic sketches or simple and clean images created using lines, often in black and white or minimal color.
    - Themes: Sketches, Minimalist design, technical diagrams, instructional content, educational materials, and branding.

11. low-poly
    - Description: Simplified, geometric images with flat shading and minimal detail, often resembling early 3D computer graphics.
    - Themes: Modern design, video game aesthetics, abstract concepts, educational visuals, and art projects.

12. modeling-compound
    - Description: Images resembling clay or sculpted figures, often with a tactile, handcrafted look.
    - Themes: Craft and DIY projects, children's content, character design, and artistic explorations.

13. neon-punk
    - Description: Bright, vibrant imagery with neon colors and a punk aesthetic, often featuring futuristic or dystopian elements.
    - Themes: Cyberpunk narratives, music events, nightlife scenes, futuristic technology, and avant-garde fashion.

14. origami
    - Description: Images inspired by the art of paper folding, often with clean lines and geometric shapes.
    - Themes: Craft and DIY projects, educational content, geometric design, and cultural presentations.

15. photographic
    - Description: Realistic images that resemble traditional photography. 
    - Themes: Professional portfolios, travel diaries, lifestyle content, product showcases, and real-life events.

16. pixel-art
    - Description: Images created using small, discrete pixels, reminiscent of early video game graphics.
    - Themes: Retro gaming, nostalgic themes, digital art, indie game design, and playful content.
    
18. default
    - Description: Use this style if you're unsure about the specific style you want for the image, or if none of the other styles fit your theme.
    - Themes: General-purpose images, versatile visuals, and content that doesn't require a specific artistic style."""
    
openai_styles_guidance = """\
1. vivid
    - Description: Causes the model to lean towards generating hyper-real and dramatic images.
    - Themes: High-impact visuals, dramatic storytelling, vibrant colors, fantasy worlds, dream-like scenes.
    
2. natural
    - Description: Causes the model to produce more natural, less hyper-real looking images.
    - Themes: Realistic scenes, nature photography, everyday life, casual settings, realistic characters.

3. default
    - Description: Use this style if you're unsure about the specific style you want for the image, or if none of the other styles fit your theme.
    - Themes: General-purpose images, versatile visuals, and content that doesn't require a specific artistic style.
"""

default_negative_prompt = "looks bad, ugly, bad anatomy, bad hands, three hands, three legs, bad arms, missing legs, missing arms, poorly drawn face, bad face, fused face, cloned face, worst face, three crus, extra crus, fused crus, worst feet, three feet, fused feet, fused thigh, three thigh, fused thigh, extra thigh, worst thigh, missing fingers, extra fingers, ugly fingers, long fingers, horn, extra eyes, huge eyes, amputation, disconnected limbs, nsfw"

stability_style_presets = [
    "default",
    "3d-model",
    "analog-film",
    "anime",
    "cinematic",
    "comic-book",
    "fantasy-art",
    "isometric",
    "line-art",
    "low-poly",
    "modeling-compound",
    "neon-punk",
    "origami",
    "photographic",
    "pixel-art",
]

openai_style_presets = [
    "default",
    "vivid",
    "natural",
]

# initialize LLM
bedrock_client = AsyncPortkey(
    virtual_key="aldeo-portkey-b-5cf75f",
    config={"cache": {"mode": "simple"}},
)

anthropic_client = AsyncPortkey(
    virtual_key="anthropic-b4a29a",
    config={"cache": {"mode": "simple"}},
)

claude_haiku = "anthropic.claude-3-haiku-20240307-v1:0"

client = bedrock_client
model = claude_haiku
force_start_with_first_tag = True


async def generate_image_sdxl(prompt, negative_prompt=None, style_preset=None, shape="square"):
    width = 1344 if shape == "full" else 1024
    height = 768 if shape == "full" else 1024

    engine_id = "stable-diffusion-xl-1024-v1-0"
    api_host = os.getenv('API_HOST', 'https://api.stability.ai')
    api_key = os.getenv("SAI_API_KEY")

    if api_key is None:
        raise Exception("Missing Stability API key.")

    text_prompts = [{"text": prompt, "weight": 1.0}]
    if negative_prompt:
        text_prompts.append({"text": negative_prompt, "weight": -1.0})

    payload = {
        "text_prompts": text_prompts,
        "cfg_scale": 7,
        "height": height,
        "width": width,
        "samples": 1,
        "steps": 30
    }
    if style_preset:
        payload["style_preset"] = style_preset

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    ssl_context = ssl.create_default_context(cafile=certifi.where())
    async with aiohttp.ClientSession() as session:
        async with session.post(f"{api_host}/v1/generation/{engine_id}/text-to-image", json=payload, headers=headers, ssl=ssl_context) as response:
            if response.status != 200:
                raise Exception(f"Non-200 response: {await response.text()}")

            data = await response.json()
            img_data = base64.b64decode(data["artifacts"][0]["base64"])

            return img_data


async def generate_image_stable_core(prompt, negative_prompt=None, style_preset=None, shape="square"):
    api_host = os.getenv('API_HOST', 'https://api.stability.ai')
    api_key = os.getenv("SAI_API_KEY")

    if api_key is None:
        raise Exception("Missing Stability API key.")

    aspect_ratio = "16:9" if shape == "full" else "1:1"

    files = {
        'prompt': (None, prompt),
        'aspect_ratio': (None, aspect_ratio)
    }

    if style_preset:
        files['style_preset'] = (None, style_preset)
    if negative_prompt:
        files['negative_prompt'] = (None, negative_prompt)

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json"
    }

    ssl_context = ssl.create_default_context(cafile=certifi.where())
    
    async with httpx.AsyncClient(verify=ssl_context, timeout=httpx.Timeout(60.0)) as client:
        retries = 3
        for attempt in range(retries):
            try:
                response = await client.post(f"{api_host}/v2beta/stable-image/generate/core", headers=headers, files=files)

                if response.status_code != 200:
                    # Log request details for debugging
                    request_log = {
                        "url": f"{api_host}/v2beta/stable-image/generate/core",
                        "headers": headers,
                        "files": files
                    }
                    print(f"Request Log: {request_log}")
                    raise Exception(f"Non-200 response: {response.text}")

                data = response.json()
                # print(data)
                img_data = base64.b64decode(data["image"])
                return img_data

            except httpx.RequestError as e:
                print(f"Request attempt {attempt + 1} failed: {str(e)}")
                if attempt == retries - 1:
                    raise
        
async def generate_image_dalle(prompt, style_preset, shape="square"):
    api_key = os.getenv("OPENAI_API_KEY")
    api_host = 'https://api.openai.com/v1/images/generations'

    if api_key is None:
        raise Exception("Missing OpenAI API key.")

    size = "1792x1024" if shape == "full" else "1024x1024"

    payload = {
        "model": "dall-e-3",
        "prompt": prompt,
        "n": 1,
        "size": size,
        "response_format": "b64_json",
    }
    
    if style_preset:
        payload["style"] = style_preset

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    ssl_context = ssl.create_default_context(cafile=certifi.where())
    async with aiohttp.ClientSession() as session:
        async with session.post(api_host, json=payload, headers=headers, ssl=ssl_context) as response:
            if response.status != 200:
                raise Exception(f"Non-200 response: {await response.text()}")

            data = await response.json()
            img_data = base64.b64decode(data["data"][0]["b64_json"])
            revised_prompt = data["data"][0].get("revised_prompt")

            return img_data, revised_prompt

async def get_prompt(presentation_topic, presentation_audience="General", presentation_goal="N/A", section_topic=None, model_type="sdxl"):
        
    class DalleGenerationTemplate(BaseModel):
        reasoning: str
        prompt: str
        style: Literal["vivid", "natural", "default"]
    
    class StabilityGenerationTemplate(BaseModel):
        reasoning: str
        prompt: str
        style: Literal[
            "default", "3d-model", "analog-film", "anime", "cinematic", "comic-book",
            "fantasy-art", "isometric", "line-art", "low-poly", "modeling-compound",
            "neon-punk", "origami", "photographic", "pixel-art"
        ]
        
    section_line = f"I need a prompt and a style for an image that goes on a section header slide titled <section_title>{section_topic}</section_title>." if section_topic else "I need a prompt and a style for an image that's used as a background for the presentation title slide."

    prompt = f"""\
### Image Styles Descriptions and Presentation Themes

{openai_styles_guidance if model_type == "dalle" else stability_styles_guidance}

### Instructions for Creating a Good Prompt

1. **Start with a Single Subject**
    - **Subject**: Focus on a single, clear subject or scene to avoid confusion.
    - **Example**: "A dog playing in a park" instead of "A dog, a cat, and a person playing in a park."

2. **Be Descriptive**
    - **Detail**: Provide detail about the main subject, background, and elements of the scene. This helps the model visualize and create the specific image you have in mind.
    - **Example**: Instead of "a dog", use "a large, fluffy Samoyed dog with bright blue eyes sitting under a cherry blossom tree in full bloom."

3. **Define the Atmosphere**
    - **Mood**: Specify the mood or emotion of the scene to influence the tone of the image.
    - **Example**: "A serene and peaceful garden at sunset."

4. **Incorporate Style and Artistic References**
    - **Style**: Mention specific artistic styles or influences if you want the image to mimic a certain artistic genre.
    - **Example**: "In the style of an impressionist painting."
    
5. **Public Figures**
    - **Name**: You can refer to public figures, celebrities, or fictional characters in your prompt by name, but the figure needs to be popular enough that their appearance is widely recognized.
    - **Example**: "Barack Obama playing chess with Albert Einstein in a library"

    
### Example of a Full Prompt

"A large, fluffy Samoyed with bright blue eyes, sitting under a cherry blossom tree in full bloom. Serene and peaceful atmosphere. In the style of an impressionist painting."

### Task Description

Your task is to help us create an image prompt and pick an image style for a presentation slide.

We're making a presentation titled <presentation_title>{presentation_topic}</presentation_title>.
The target audience is <presentation_audience>{presentation_audience}</presentation_audience>.
The goal of the presentation is <presentation_goal>{presentation_goal}</presentation_goal>.
{section_line}

First, in a <reasoning></reasoning> tag, think step by step about the following:
- What themes you see in the given <presentation_title></presentation_title> and <section_title></section_title>?
- How you can visually represent the themes in an image: what will the the main subjects, background, and elements of the scene be?
    - Think of what objects and elements could be a visual representation of the themes.
- What mood or atmosphere should the image convey?
- What style or artistic influences do you want the image to have?

Then, give us a <prompt></prompt> for an image that fits the theme of the presentation. The prompt will be given to a text-to-image model, like Dall-E or Stable Diffusion. Only describe what will be seen in the image. NEVER include your reasoning behind the image, or what the image represents, symbolizes, or suggests in the prompt.
Follow the instructions above to create a good prompt.

You also need to choose a <style></style> for the image from the following options: {openai_style_presets if model_type == "dalle" else stability_style_presets}.
Refer to the descriptions above to understand the style options.
You have to use one of the options mentioned as the value for the <style></style> field in the response, you can't use anything else.
However, if your not sure what style to use, you can use the `default` style.

Please respond in the following format:
{generate_variable_input_xml(DalleGenerationTemplate if model_type == "dalle" else StabilityGenerationTemplate)}

Remember to follow the instructions for creating a good prompt and to provide a detailed and descriptive prompt for the image."""

    messages = [{"role": "user", "content": prompt}]

    template, messages = await get_basemodel_instance_from_llm(
        client=bedrock_client,
        pydantic_model_class=DalleGenerationTemplate if model_type == "dalle" else StabilityGenerationTemplate,
        model=claude_haiku,
        temperature=1.0,
        temperature_multiplier=1.1,
        max_temperature=2,
        messages=messages,
        max_tokens=500,
    )

    return template, messages

async def upload_image(image_data, presentationID):
    """Uploads the image and its thumbnail to S3 and returns the S3 key."""
    
    # Convert base64 image data to Pillow Image
    image = Image.open(BytesIO(image_data))

    # Save the image as WebP with quality=85
    image_bytes_io = BytesIO()
    image.save(image_bytes_io, format="WEBP", quality=85)
    image_bytes = image_bytes_io.getvalue()

    # Generate the S3 key
    s3_key = f"{presentationID}/backgrounds/{uuid7str()}.webp"

    # Create and upload the thumbnail
    thumbnail_size = THUMBNAIL_SIZE_FULL if image.width > image.height else THUMBNAIL_SIZE_SQUARE
    thumbnail = image.copy()
    thumbnail.thumbnail(thumbnail_size)

    thumbnail_bytes_io = BytesIO()
    thumbnail.save(thumbnail_bytes_io, format="WEBP", quality=85)
    thumbnail_bytes = thumbnail_bytes_io.getvalue()

    thumbnail_key = s3_key.replace(".webp", "_thumbnail.webp")

    # Use asyncio.gather to run both uploads concurrently
    await asyncio.gather(
        upload_bytes_to_s3(image_bytes, s3_key),
        upload_bytes_to_s3(thumbnail_bytes, thumbnail_key)
    )
    return s3_key

    
async def generate_upload_update_by_prompt(presentationID, prompt, shape, style_preset=None, model_type="sdxl", negative_prompt=None):
    
    revised_prompt = None
    
    if style_preset == "default":
        style_preset = None
        
    if model_type == "core":
        image_data = await generate_image_stable_core(prompt, style_preset=style_preset, negative_prompt=negative_prompt, shape=shape)
    elif model_type == "dalle":
        image_data, revised_prompt = await generate_image_dalle(prompt, style_preset=style_preset, shape=shape)
    elif model_type == "sdxl":
        image_data = await generate_image_sdxl(prompt, style_preset=style_preset, negative_prompt=negative_prompt, shape=shape)
    else:
        raise Exception("Invalid model type")
    
    s3_key = await upload_image(image_data, presentationID)

    image = Image.open(BytesIO(image_data))
    width, height = image.size

    image_data =  {
        "s3_key": s3_key,
        "prompt": revised_prompt or prompt,
        "width": width,
        "height": height,
        "shape": shape,
        "model": model_type,
    }
    
    return image_data
    

async def generate_and_upload_image(presentationID, presentation_topic, presentation_audience, presentation_goal, section_topic=None, shape="square", model_type="sdxl"):
    template, messages = await get_prompt(presentation_topic, presentation_audience, presentation_goal, section_topic, model_type)
    
    if template.style == "default":
        style_preset = None
    else:
        style_preset = template.style
        
    revised_prompt = None
    if model_type == "core":
        image_data = await generate_image_stable_core(template.prompt, style_preset=style_preset, negative_prompt=default_negative_prompt, shape=shape)
    elif model_type == "dalle":
        image_data, revised_prompt = await generate_image_dalle(template.prompt, style_preset=style_preset, shape=shape)
    elif model_type == "sdxl":
        image_data = await generate_image_sdxl(template.prompt, style_preset=style_preset, negative_prompt=default_negative_prompt, shape=shape)
    else:
        raise Exception("Invalid model type")
    
    s3_key = await upload_image(image_data, presentationID)

    image = Image.open(BytesIO(image_data))
    width, height = image.size

    image_data =  {
        "s3_key": s3_key,
        "style": template.style,
        "prompt": revised_prompt or template.prompt,
        "width": width,
        "height": height,
        "shape": shape,
        "model": model_type,
    }
        
    return image_data, messages
    

# test function
async def test():
    # presentationID = "1"
    # presentation_topic = "Joe Biden's Career and Achievements"
    # # section_topic = "Economic Policies"
    # section_topic = None
    # shape = "full"
    # model_type = "dalle"  # Change to "core" or "sdxl" to test different models
    # image_data = await generate_and_upload_image(presentationID, presentation_topic, section_topic, shape, model_type)
    # print(image_data)
    
    presentationID = "1"
    prompt = "A lighthouse on a cliff"
    shape = "square"
    style_preset = "natural"
    model_type = "dalle"
    
    image = await generate_upload_update_by_prompt(presentationID, prompt, shape, style_preset, model_type)
    print(image)
    

if __name__ == "__main__":
    import asyncio
    asyncio.run(test())
