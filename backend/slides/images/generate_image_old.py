import base64
from PIL import Image
from io import BytesIO
import json
import os
from s3 import upload_bytes_to_s3
from uuid_extensions import uuid7str
import sys
from dotenv import load_dotenv
from portkey_ai import AsyncPortkey, PORTKEY_GATEWAY_URL, createHeaders
from openai import AsyncOpenAI
import os
import aiohttp
import asyncio
import certifi
import ssl

load_dotenv("/Users/noahyoungs/VSCode/ai-presenter-v2/backend/.env")

# initialize gpt client
openai_client = AsyncOpenAI(
    base_url=PORTKEY_GATEWAY_URL,
    default_headers=createHeaders(
        provider="openai",
        api_key=os.getenv('PORTKEY_API_KEY'),
        config={"cache": {"mode": "simple"}},
    )
)

stability_client = AsyncPortkey(
    api_key=os.getenv('PORTKEY_API_KEY'),
    virtual_key="stability-42adfa",
    config={"cache": {"mode": "simple"}},
)


GPT_MODEL = "gpt-3.5-turbo-0125"
GENERATION_ENDPOINT = "generation/stable-diffusion-xl-1024-v1-0/text-to-image"
UPSCALE_ENDPOINT = "https://api.stability.ai/v1/generation/esrgan-v1-x2plus/image-to-image/upscale"


async def generate_image(presentation_id, presentation_topic, presentation_audience, presentation_goal, slide_type, subtopic=None):
    # Extract parameters from the eventp

    SHAPE = 'full' if slide_type == "presentation_title_slide" else 'square' if slide_type == "section_header_slide" else 'half'

    # GENERATE TEXT PROMPT

    # Function options
    def get_animal_prompt(description):
        return f"{description}, wildlife photography, photograph, high quality, wildlife, f 1.8, soft focus, 8k, national geographic, award - winning photograph by nick nichols"

    def get_fashion_prompt(description):
        return f"cinematic photo a centered model, upper body, fashion model, {description}, very detailed face, intricate background, designer outfit, award-winning photo, hyper-realistic, editorial, 8k . 35mm photograph, film, bokeh, professional, 4k, highly detailed"

    def get_car_prompt(description, color):
        return f"cinematic photo of {description}, modern car, {color} color, perfectly centered, telephoto lens, bokeh, extremely detailed car, extremely detailed background, reflections, raw photo, photorealism, 35mm photograph, film, professional, 4k, highly detailed"

    def get_space_prompt(description):
        return f"{description}, by Andrew McCarthy, Navaneeth Unnikrishnan, Manuel Dietrich, photo realistic, 8k, cinematic lighting, hd, atmospheric, hyperdetailed, trending on artstation, deviantart, photography, glow effect"

    def get_sketch_prompt(description):
        return f"line art drawing, {description}, sketch, drawing, detailed, pencil, black and white, professional, sleek, modern, minimalist, graphic, line art, vector graphics"

    def get_city_prompt(city_description, subject_description):
        return f"bokeh, {city_description} skyline, full body (back portrait) of {subject_description}"

    def get_abstract_digital_art_prompt(description):
        return f"abstract digital art, minimalist style, simple, clean, uncluttered, modern, elegant, {description}"

    def get_papercut_prompt(description):
        return f"flat papercut style {description}. silhouette, clean cuts, paper, sharp edges, minimalist, color block"

    def get_food_prompt(description):
        return f"gourmet food photo of {description}. soft natural lighting, macro details, vibrant colors, fresh ingredients, glistening textures, bokeh background, styled plating, wooden tabletop, garnished, tantalizing, editorial quality"

    def play_doh_sculpture_prompt(description):
        return f"play-doh style, {description}. sculpture, clay art, centered composition, Claymation"

    def get_animal_template(description):
        return {
            "type": "animal",
            "prompt": get_animal_prompt(description),
            "style_preset": "photographic",
            "alt": f"Animal photograph, {description}"
        }

    def get_fashion_template(description):
        return {
            "type": "fashion",
            "prompt": get_fashion_prompt(description),
            "style_preset": "photographic",
            "alt": f"Fashion model photograph, {description}"
        }

    def get_car_template(description, color):
        return {
            "type": "car",
            "prompt": get_car_prompt(description, color),
            "style_preset": "cinematic",
            "alt": f"Photograph of a {color} {description} in a city street"
        }

    def get_space_template(description):
        return {
            "type": "space",
            "prompt": get_space_prompt(description),
            "style_preset": "enhance",
            "alt": f"Space Photograph, {description}"
        }

    def get_sketch_template(description):
        return {
            "type": "sketch",
            "prompt": get_sketch_prompt(description),
            "style_preset": "line-art",
            "alt": f"Sketch, {description}"

        }

    def get_landscape_template(description):
        return {
            "type": "landscape",
            "prompt": description,
            "style_preset": "cinematic",
            "steps": 30,
            "alt": f"Photograph, {description}"
        }

    def get_city_template(city="New York City", person_description="a man"):
        return {
            "type": "city",
            "prompt": get_city_prompt(city, person_description),
            "style_preset": "cinematic",
            "negative_prompt": "bad, NSFW",
            "alt": f"Photograph of {city} with a {person_description} looking at the skyline"
        }

    def get_interior_template(style, room):
        if style not in ["modern", "rustic"]:
            style = "modern"
        if room not in ["Living Room", "Bedroom", "Kitchen", "Bathroom", "Foyer", "Garage"]:
            room = "Living Room"
        return {
            "type": "interior",
            "style": style,
            "room": room,
            "style_preset": "photographic",
            "alt": f"Interior photograph of a {style} {room}"
        }

    def get_abstract_digital_art_template(description):
        return {
            "type": "abstract_digital_art",
            "prompt": get_abstract_digital_art_prompt(description),
            "style_preset": "digital-art",
            "alt": f"Abstract digital art, {description}",
            "negative_prompt": "ornate, complicated, highly detailed, cluttered, disordered, messy, noisy"
        }

    def get_papercut_template(description):
        return {
            "type": "papercut",
            "prompt": get_papercut_prompt(description),
            "style_preset": None,
            "alt": f"Papercut art, {description}",
            "negative_prompt": "3D, high detail, noise, grainy, blurry, painting, drawing, photo, disfigured"

        }

    def get_food_template(description):
        return {
            "type": "food",
            "prompt": get_food_prompt(description),
            "style_preset": "photographic",
            "alt": f"Photograph of {description}",
            "negative_prompt": "cartoon, anime, sketch, grayscale, dull, overexposed, cluttered, messy plate, deformed"
        }

    def get_play_doh_sculpture_template(description):
        return {
            "type": "play_doh_sculpture",
            "prompt": play_doh_sculpture_prompt(description),
            "style_preset": "craft-clay",
            "alt": f"Play-doh art, {description}",
            "negative_prompt": "sloppy, messy, grainy, highly detailed, ultra textured, photo"
        }

    functions_map = {
        "suggest_animal_photograph": get_animal_template,
        "suggest_fashion_model_photograph": get_fashion_template,
        "suggest_car_photograph": get_car_template,
        "suggest_space_photograph": get_space_template,
        "suggest_artistic_sketch": get_sketch_template,
        "suggest_nature_landscape_photograph": get_landscape_template,
        "suggest_city_photograph": get_city_template,
        "suggest_home_interior_photograph": get_interior_template,
        "suggest_abstract_digital_art": get_abstract_digital_art_template,
        "suggest_papercut_art": get_papercut_template,
        "suggest_food_photograph": get_food_template,
        "suggest_play_doh_sculpture": get_play_doh_sculpture_template
    }

    # OpenAI Request
    tools = [
        {
            "type": "function",
            "function": {
                "name": "suggest_animal_photograph",
                "description": "Suggest a photograph of an animal as a background image",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "description": {
                            "type": "string",
                            "description": "Describe the animal and the environment it is in (e.g. 'a lion in the savannah')",
                        }
                    },
                    "required": ["description"],
                },
            }
        },
        {
            "type": "function",
            "function": {
                "name": "suggest_fashion_model_photograph",
                "description": "Suggest a photograph of a fashion model as a background image",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "description": {
                            "type": "string",
                            "description": "Describe the fashion model, their clothing, and the environment they are in (e.g. 'a woman wearing a red dress in a studio')",
                        }
                    },
                    "required": ["description"],
                },
            }
        },
        {
            "type": "function",
            "function": {
                "name": "suggest_car_photograph",
                "description": "Suggest a photograph of a car as a background image",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "description": {
                            "type": "string",
                            "description": "Describe the make and/or model of the car and the environment it is in (e.g. 'a Ferrari in a city street')",
                        },
                        "color": {
                            "type": "string",
                            "description": "The color of the car (e.g. 'red')",
                        }
                    },
                    "required": ["description", "color"],
                },
            }
        },
        {
            "type": "function",
            "function": {
                "name": "suggest_space_photograph",
                "description": "Suggest a photograph of space as a background image",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "description": {
                            "type": "string",
                            "description": "Describe the space photograph (e.g. 'a space scene with many planets')",
                        }
                    },
                    "required": ["description"],
                },
            }
        },
        {
            "type": "function",
            "function": {
                "name": "suggest_nature_landscape_photograph",
                "description": "Suggest a nature landscape photograph that showcases the beauty of nature and the outdoors as a background image",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "description": {
                            "type": "string",
                            "description": "Describe the landscape in detail (e.g. 'An expansive arctic landscape featuring a frozen lake in the foreground, surrounded by snow-covered pine trees. In the background, towering icebergs and mountains covered in snow rise against a twilight sky, painted in hues of pink, purple, and blue. The scene conveys a sense of serene isolation and the pristine beauty of the arctic wilderness.')",
                        }
                    },
                    "required": ["description"],
                },
            }
        },
        {
            "type": "function",
            "function": {
                "name": "suggest_city_photograph",
                "description": "Suggest a photograph of a person looking at a city skyline as a background image",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "city": {
                            "type": "string",
                            "description": "The name of the city (e.g. 'Chicago')",
                        },
                        "person_description": {
                            "type": "string",
                            "description": "Describe the person looking at the city skyline (e.g. 'a man in a suit')",
                        }
                    },
                    "required": ["city_description", "subject_description"],
                },
            }
        },
        {
            "type": "function",
            "function": {
                "name": "suggest_home_interior_photograph",
                "description": "Suggest a photograph of a room interior as a background image",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "style": {
                            "type": "string",
                            "enum": ["modern", "rustic"],
                            "description": "The style of the room (e.g. 'modern')",
                        },
                        "room": {
                            "type": "string",
                            "enum": ["Living Room", "Bedroom", "Kitchen", "Bathroom", "Foyer", "Garage"],
                            "description": "The type of room (e.g. 'Living Room')",
                        }
                    },
                    "required": ["city_description", "subject_description"],
                },
            }
        },
        {
            "type": "function",
            "function": {
                "name": "suggest_food_photograph",
                "description": "Suggest a photograph of food as a background image",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "description": {
                            "type": "string",
                            "description": "Describe the food (e.g. 'a gourmet burger')",
                        }
                    },
                    "required": ["description"],
                },
            }
        },
        {
            "type": "function",
            "function": {
                "name": "suggest_abstract_digital_art",
                "description": "Suggest an abstract digital art piece as a background image",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "description": {
                            "type": "string",
                            "description": "Describe the abstract digital art piece (e.g. 'a digital art piece with vibrant colors and geometric shapes')",
                        }
                    },
                    "required": ["description"],
                },
            }
        },
        {
            "type": "function",
            "function": {
                "name": "suggest_papercut_art",
                "description": "Suggest a papercut art piece as a background image",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "description": {
                            "type": "string",
                            "description": "Describe what appears in the papercut art piece (e.g. 'cityscape with trees, buildings, and clouds')",
                        }
                    },
                    "required": ["description"],
                },
            }
        },
        {
            "type": "function",
            "function": {
                "name": "suggest_play_doh_sculpture",
                "description": "Suggest a play-doh sculpture as a background image",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "description": {
                            "type": "string",
                            "description": "Describe what the play-doh sculpture depicts (e.g. 'the 50 US states')",
                        }
                    },
                    "required": ["description"],
                },
            }
        },
        {
            "type": "function",
            "function": {
                "name": "suggest_artistic_sketch",
                "description": "Suggest a sketch of any scene, person, or object you want as an background image (NO abstract sketches)",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "description": {
                            "type": "string",
                            "description": "Describe what appears in the sketch (e.g. 'a cab in New York City')",
                        }
                    },
                    "required": ["description"],
                },
            }
        },
    ]

    # Conditionally exclude the last 3 items if SHAPE is "full"
    if SHAPE == "full":
        tools = tools[:-4]

    prompt_slide_section = f"Section Header Slide for a section about `{subtopic}`" if subtopic else "A title slide for my presentation"

    messages = [
        {
            "role": "user",
            "content": f"""\
Here's the presentation I'm working on:
Presentation Topic: {presentation_topic}
Presentation Audience: {presentation_audience}
Presentation Goal: {presentation_goal}
I need a background image for this slide:
{prompt_slide_section}"""
        },
        {
            "role": "system",
            "content": "Use one of the functions to suggest a background image. Try to pick a suggestion that matches the presentation and the slide, but if none of them match, just pick something that's appropriate. DO NOT explain your reasoning or mention what the image should symbolize or represent. ONLY mention what should appear in the image."
        }
    ]

    data = {
        "model": GPT_MODEL,
        "messages": messages,
        "tools": tools,
        "tool_choice": "auto"
    }

    completion = await openai_client.chat.completions.create(**data)

    try:
        function_key = completion.choices[0].message.tool_calls[0].function.name
    except Exception as e:
        raise Exception(f"Can't parse function name: {e}")
    if function_key not in functions_map:
        # raise Exception(f"Invalid function called: {function_key}")
        print(f"Invalid function called: {function_key}")
        print("WARNING: Using default landscape template")
        template = get_landscape_template("an expansive arctic landscape featuring a frozen lake in the foreground, surrounded by snow-covered pine trees. In the background, towering icebergs and mountains covered in snow rise against a twilight sky, painted in hues of pink, purple, and blue. The scene conveys a sense of serene isolation and the pristine beauty of the arctic wilderness.")
    else:
        try:
            args = json.loads(
                completion.choices[0].message.tool_calls[0].function.arguments)
        except Exception as e:
            raise Exception(f"Invalid arguments: {e}")

        selected_function = functions_map[function_key]

        template = selected_function(**args)

    if template.get("type") == "interior":
        s3_url = f"https://ai-presenter-slide-images.s3.amazonaws.com/interior-images/{template.get('style').lower().strip().replace(' ', '_')}_{template.get('room').lower().strip().replace(' ', '_')}_{SHAPE}.webp"
        # https://ai-presenter-slide-images.s3.us-west-2.amazonaws.com/interior-images/modern_bathroom_full.webp
        return {
            'statusCode': 200,  # Add the statusCode here
            'body': {
                'url': s3_url,
                'alt': template.get("alt"),
                'type': 'interior',
                'shape': SHAPE,
                # "messages": json.dumps(messages)
            }
        }


    prompt = template.get("prompt")
    negative_prompt = template.get("negative_prompt", "bad, blurry, NSFW")
    style_preset = template.get("style_preset", None)
    steps = template.get("steps", 50)

    # GENERATE IMAGE

    # Define dimensions
    width = 1344 if SHAPE == "full" else 1024
    height = 768 if SHAPE == "full" else 1024

    generation_body = {
        "steps": steps,
        "width": width,
        "height": height,
        "seed": 0,
        "cfg_scale": 5,
        "samples": 1,
        "text_prompts": [{"text": prompt, "weight": 1}, {"text": negative_prompt, "weight": -1}],
    }

    if style_preset is not None:
        generation_body["style_preset"] = style_preset

    generation = await stability_client.post(
        url=GENERATION_ENDPOINT,
        **generation_body
    )

    # print("Generation: ", generation)
    image_data = base64.b64decode(generation.artifacts[0]['base64'])
    
    # Upscale Image
    upscale_data = {"width": 1920} if SHAPE == "full" else {"height": 1080}
        
    async with aiohttp.ClientSession() as session:
        data = aiohttp.FormData()
        data.add_field("image", image_data, filename="image.png", content_type="image/png")
        
        if "width" in upscale_data and upscale_data["width"] is not None:
            data.add_field("width", str(upscale_data["width"]))
        if "height" in upscale_data and upscale_data["height"] is not None:
            data.add_field("height", str(upscale_data["height"]))
        
        sslcontext = ssl.create_default_context(cafile=certifi.where())
        
        async with session.post(
            url=UPSCALE_ENDPOINT,
            headers={
                "Accept": "application/json",
                "Authorization": f"Bearer {os.getenv('SAI_API_KEY')}"
            },
            data=data,
            ssl=sslcontext
        ) as response:
            if response.status != 200:
                raise Exception(f"Non-200 response: {await response.text()}")
            upscale = await response.json()
    

    upscaled_image_data = base64.b64decode(upscale["artifacts"][0]["base64"])
    upscaled_image = Image.open(BytesIO(upscaled_image_data))
    
    final_img = BytesIO()

    # Crop unless square
    if SHAPE != "square":
        new_width = 1920 if SHAPE == "full" else 960
        new_height = 1080
        width, height = upscaled_image.size
        left = (width - new_width) / 2
        top = (height - new_height) / 2
        right = (width + new_width) / 2
        bottom = (height + new_height) / 2
        cropped_image = upscaled_image.crop((left, top, right, bottom))

        # Convert and Prepare Image for Upload
        # cropped_image.convert("RGB").save(final_img, 'JPEG', quality=85, optimize=True, progressive=True)
        cropped_image.convert("RGB").save(
            final_img, 'WEBP', quality=85, optimize=True)
    else:
        # Convert and Prepare Image for Upload
        # upscaled_image.convert("RGB").save(final_img, 'JPEG', quality=85, optimize=True, progressive=True)
        upscaled_image.convert("RGB").save(
            final_img, 'WEBP', quality=85, optimize=True)
    final_img.seek(0)  # Rewind the file-like object to the beginning

    # UPLOAD IMAGE TO S3

    # convert image to bytes
    image_bytes = final_img.getvalue()

    s3_key = f"{presentation_id}/backgrounds/{uuid7str()}.webp"
    await upload_bytes_to_s3(image_bytes, s3_key)

    return {
        'statusCode': 200,
        'body': {
            's3_key': s3_key,
            'alt': template.get("alt"),
            'type': template.get("type"),
            'shape': SHAPE,
            # "messages": json.dumps(messages)
        }
    }


# Run the function
if __name__ == "__main__":
    import asyncio
    loop = asyncio.get_event_loop()

    presentation_id = "foo"
    presentation_topic = "A presentation about cats"
    presentation_audience = "Cat lovers"
    presentation_goal = "To educate people about cats"
    subtopic = "Cat breeds"
    slide_type = "section_header_slide"

    # run and print output
    print(loop.run_until_complete(generate_image(presentation_id, presentation_topic,
          presentation_audience, presentation_goal, subtopic, slide_type)))
