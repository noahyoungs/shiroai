# add_prose_class_and_split.py

import os
import aiohttp
import ssl
import asyncio
from database_models import *
from uuid_extensions import uuid7str
from session_log_config import get_child_logger, current_user_id

CONTEXT_USER_ID = current_user_id.get()
HEADLESS_API_URL = os.getenv('HEADLESS_API_URL')
HEADLESS_API_INTERNAL_KEY = os.getenv('HEADLESS_API_INTERNAL_KEY')  # Get the API key from environment variable
SSL_VERIFY = False  # Set to True to enable SSL verification, False to disable

# Create an SSL context that disables verification if SSL_VERIFY is False
ssl_context = None
if not SSL_VERIFY:
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

async def split_markdown(markdown_text):
    context_user_id = current_user_id.get()
    headers = {
        'x-api-key': HEADLESS_API_INTERNAL_KEY,
        'x-user-id': context_user_id
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f'{HEADLESS_API_URL}/markdown-split/split', 
            json={'markdown': markdown_text}, 
            headers=headers,  # Pass headers with the API key
            ssl=ssl_context
        ) as response:
            if response.status == 200:
                data = await response.json()
                return data['firstPart'], data['secondPart']
            else:
                error_message = await response.text()
                print(f"Failed to split markdown: {response.status} - {error_message}")
                return None, None

async def get_prose_class(markdown, title):
    context_user_id = current_user_id.get()
    headers = {
        'x-api-key': HEADLESS_API_INTERNAL_KEY,
        'x-user-id': context_user_id
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f'{HEADLESS_API_URL}/prose-class', 
            json={'markdown': markdown, 'title': title}, 
            headers=headers,  # Pass headers with the API key
            ssl=ssl_context
        ) as response:
            if response.status == 200:
                data = await response.json()
                return data['proseClass']
            else:
                error_message = await response.text()
                print(f"Failed to get prose class: {response.status} - {error_message}")
                return None


async def process_slide(slide):
    if slide.slide_type != 'markdown_slide':
        print(f"Warning: Unsupported slide type '{slide.slide_type}'. Returning the input slide without changes.")
        return [slide]
    
    prose_class = await get_prose_class(slide.slide_content['content'], slide.slide_title)
    
    if prose_class != 'overheight':
        slide.slide_content['prose_class'] = prose_class
        return [slide]
    
    first_half, second_half = await split_markdown(slide.slide_content['content'])
    if not first_half or not second_half:
        print("Error splitting markdown content.")
        return [slide]
    
    # Create the first slide using spread operator and update content
    first_slide = MarkdownSlide(
        **{**slide.__dict__, 'slide_content': {**slide.slide_content, 'content': first_half}}
    )
    
    # Create the second slide using spread operator and update content, title, and id
    second_title = slide.slide_title
    if "(Cont.)" not in second_title:
        second_title += " (Cont.)"
    
    second_slide = MarkdownSlide(
        **{**slide.__dict__, 
           'slide_title': second_title, 
           'id': uuid7str(), 
           'slide_content': {**slide.slide_content, 'content': second_half}}
    )
    
    # Process both new slides recursively
    slides = []
    slides.extend(await process_slide(first_slide))
    slides.extend(await process_slide(second_slide))
    
    return slides
