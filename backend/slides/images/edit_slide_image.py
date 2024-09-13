
from io import BytesIO
from PIL import Image
from typing import Awaitable, List, Literal, Optional, Callable, Tuple, Union, Dict
from pydantic import BaseModel
from slides.xml_instructor import generate_variable_input_xml, get_basemodel_instance_from_llm, generate_xml_from_instance
from database_models import Image as ImageType, Slide
from slides.images.generate_image import openai_style_presets, stability_style_presets, generate_image_stable_core, generate_image_dalle, generate_image_sdxl, upload_image, default_negative_prompt
from llm_clients import content_gen_client, content_gen_model


async def get_new_prompt(instruction, old_messages, old_prompt, old_style="default", old_negative_prompt=None, model_type="sdxl"):
        
    class DalleGenerationTemplate(BaseModel):
        reasoning: str
        prompt: str
        style: Literal["vivid", "natural", "default"]
        message_to_user: str
    
    class StabilityGenerationTemplate(BaseModel):
        reasoning: str
        prompt: str
        style: Literal[
            "default", "3d-model", "analog-film", "anime", "cinematic", "comic-book",
            "fantasy-art", "isometric", "line-art", "low-poly", "modeling-compound",
            "neon-punk", "origami", "photographic", "pixel-art"
        ]
        negative_prompt: Optional[str] = None
        message_to_user: str
        
    class OldDalleGenerationTemplate(BaseModel):
        prompt: str
        style: Literal["vivid", "natural", "default"]
    
    class OldStabilityGenerationTemplate(BaseModel):
        prompt: str
        negative_prompt: Optional[str] = None
        style: Literal[
            "default", "3d-model", "analog-film", "anime", "cinematic", "comic-book",
            "fantasy-art", "isometric", "line-art", "low-poly", "modeling-compound",
            "neon-punk", "origami", "photographic", "pixel-art"
        ]
        
    old_template = None
    if model_type == "dalle":
        old_template = OldDalleGenerationTemplate.model_validate({
            "prompt": old_prompt,
            "style": old_style
        })
    else:
        old_template = OldStabilityGenerationTemplate.model_validate({
            "prompt": old_prompt,
            "style": old_style
        })
        if old_negative_prompt:
            old_template.negative_prompt = old_negative_prompt
        
    
    negative_prompt_line = ", as well as a new, optional <negative_prompt></negative_prompt> parameter" if model_type != "dalle" else ""
    parameters_line = "<prompt></prompt> and <style></style> parameters" if model_type != "dalle" else "<prompt></prompt>, <style></style> and <negative_prompt></negative_prompt> parameters"
    
    prompt = f"""\
Here's latest prompt and style for the image we have so far. This reflects both your previous work and the user's direct changes:
{generate_xml_from_instance(old_template)}

The user has requested that we make the following change to the image:
<user_request>{instruction}</user_request>

Your task is to change the image to reflect the <user_request></user_request>.
In order to do this, you need to provide new <prompt></prompt> and <style></style> parameters{negative_prompt_line} which will then be sent to the image model to generate a new image.

In a <reasoning></reasoning> tag, think step by step while you examine the <user_request></user_request> and how you are going to use the {parameters_line} to reflect the changes.

In the <prompt></prompt> tag, describe the new image you want to generate based on the user's request. Remember to follow the instructions from earlier for creating a good prompt and to provide a detailed and descriptive prompt for the image.

In the <style></style> tag, choose a new style for the image from the following options: {openai_style_presets if model_type == "dalle" else stability_style_presets}. Remember the descriptions from earlier to understand the style options.

If deemed appropriate, include a <negative_prompt></negative_prompt> tag with a negative prompt for the image. In the negative prompt, you should describe any elements, styles, or themes that should NOT be seen in the image.
For example, if the user requests to remove a specific object from the image, you should include that in the negative prompt.

Finally, include a <message_to_user></message_to_user> tag with a message to the user explaining the changes you made to the image.

Please respond in the following format:
{generate_variable_input_xml(DalleGenerationTemplate if model_type == "dalle" else StabilityGenerationTemplate)}
"""

    messages = old_messages + [{"role": "user", "content": prompt}]

    template, messages = await get_basemodel_instance_from_llm(
        client=content_gen_client,
        pydantic_model_class=DalleGenerationTemplate if model_type == "dalle" else StabilityGenerationTemplate,
        model=content_gen_model,
        temperature=1.0,
        temperature_multiplier=1.1,
        max_temperature=2,
        messages=messages,
        max_tokens=500,
    )

    return template, messages

async def _edit_image(old_messages, instruction, current_slide, presentation_id):
    
    if not current_slide.image.shape:
        raise ValueError("No shape found for the image")
    
    if not current_slide.image.prompt:
        raise ValueError("No prompt found for the image")
    
    old_prompt = current_slide.image.prompt
    shape = current_slide.image.shape
    old_style = current_slide.image.style or "default"
    old_negative_prompt = current_slide.image.negative_prompt or None
    model_type = current_slide.image.model or "sdxl"
    
    # make sure style is supported by the model
    if model_type == "dalle" and old_style not in openai_style_presets:
        old_style = "default"
    elif model_type != "dalle" and old_style not in stability_style_presets:
        old_style = "default"
    
    template, messages = await get_new_prompt(instruction, old_messages, old_prompt, old_style, old_negative_prompt, model_type)
    
    if template.style == "default":
        style_preset = None
    else:
        style_preset = template.style
        
    negative_prompt = template.negative_prompt or default_negative_prompt
    revised_prompt = None
    
    if model_type == "core":
        image_bytes = await generate_image_stable_core(template.prompt, style_preset=style_preset, negative_prompt=negative_prompt, shape=shape)
    elif model_type == "dalle":
        image_bytes, revised_prompt = await generate_image_dalle(template.prompt, style_preset=style_preset, shape=shape)
    elif model_type == "sdxl":
        image_bytes = await generate_image_sdxl(template.prompt, style_preset=style_preset, negative_prompt=negative_prompt, shape=shape)
    else:
        raise Exception("Invalid model type")
    
    s3_key = await upload_image(image_bytes, presentation_id)

    image = Image.open(BytesIO(image_bytes))
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
    
    if template.negative_prompt:
        image_data["negative_prompt"] = template.negative_prompt
        
    return image_data, messages, template.message_to_user


async def edit_slide_image(
    presentation_id,
    current_slide: Slide,
    update_slides: Callable[[Union[Slide, Dict, List[Union[Slide, Dict]]], bool], Awaitable[None]],
    instruction: str
) -> Tuple[Slide, str]:    
    
    if not current_slide:
        raise ValueError("No current slide found")
    
    if not current_slide.slide_type:
        raise ValueError("No slide type found for the slide")
    
    image_data, generation_messages, message_to_user = await _edit_image(current_slide.generation_messages, instruction, current_slide, presentation_id)    
    
    current_slide.image = ImageType(**image_data)
    current_slide.generation_messages = generation_messages
    
    # update the slide in the PersistentSlideList and DynamoDB
    await update_slides(current_slide, True)
        
    # return the updated slide and the messages
    return current_slide, message_to_user