# add_prose_class_and_split.py

import os
import aiohttp
import ssl
import asyncio
from slides.slide_models import *
from uuid_extensions import uuid7str

HEADLESS_API_PATH = os.getenv('HEADLESS_API_PATH')
HEADLESS_API_INTERNAL_KEY = os.getenv('HEADLESS_API_INTERNAL_KEY')  # Get the API key from environment variable
SSL_VERIFY = False  # Set to True to enable SSL verification, False to disable

# Create an SSL context that disables verification if SSL_VERIFY is False
ssl_context = None
if not SSL_VERIFY:
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

async def split_markdown(markdown_text):
    headers = {'x-api-key': HEADLESS_API_INTERNAL_KEY}  # Include the API key in the headers
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f'{HEADLESS_API_PATH}/markdown-split/split', 
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
    headers = {'x-api-key': HEADLESS_API_INTERNAL_KEY}  # Include the API key in the headers
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f'{HEADLESS_API_PATH}/prose-class', 
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

# Sample data for testing
test_slides = [
    MarkdownSlide(
        slide_title="Short Text Markdown Slide",
        topic_id="topic-1",
        id=uuid7str(),
        slide_content={
            "content": "This is a short text.",
            "footnotes": []
        },
        hidden=False,
        previous=None,
        next=None,
        generation_messages=[LLMMessage(role="system", content="Generate a short markdown slide.")],
        extra={}
    ),
    MarkdownSlide(
        slide_title="Large Text Markdown Slide",
        topic_id="topic-2",
        id=uuid7str(),
        slide_content={
            "content": "This is a very large text. " * 300,
            "footnotes": []
        },
        hidden=False,
        previous=None,
        next=None,
        generation_messages=[LLMMessage(role="system", content="Generate a large markdown slide.")],
        extra={}
    ),
    MarkdownSlide(
        slide_title="Markdown Slide with Table",
        topic_id="topic-3",
        id=uuid7str(),
        slide_content={
            "content": "| Header 1 | Header 2 | Header 3 |\n|----------|----------|----------|\n" + 
                       "| Cell 1.1 | Cell 1.2 | Cell 1.3 |\n" * 20,
            "footnotes": []
        },
        hidden=False,
        previous=None,
        next=None,
        generation_messages=[LLMMessage(role="system", content="Generate a markdown slide with a table.")],
        extra={}
    ),
    SimpleMermaidSlide(
        slide_title="Simple Mermaid Slide",
        topic_id="topic-4",
        id=uuid7str(),
        slide_content={
            "mermaid_code": "graph TD;\nA-->B;",
            "excerpts": [],
            "light_svg": "<svg>Light SVG Content</svg>",
            "dark_svg": "<svg>Dark SVG Content</svg>"
        },
        hidden=False,
        previous=None,
        next=None,
        generation_messages=[LLMMessage(role="system", content="Generate a simple mermaid slide.")],
        extra={}
    ),
    SectionHeaderSlide(
        slide_title="Section Header Slide",
        topic_id="topic-5",
        id=uuid7str(),
        image=Image(
            prompt="Sunset over mountains",
            model="stable-diffusion",
            width=800,
            height=600,
            shape="rectangle",
            type="generated"
        ),
        hidden=False,
        previous=None,
        next=None,
        generation_messages=[LLMMessage(role="system", content="Generate a section header slide.")],
        extra={}
    )
]

# Run the functions
if __name__ == "__main__":
    for slide in test_slides:
        print(f"Processing original slide: {slide.slide_title}")
        processed_slides = asyncio.run(process_slide(slide))
        for processed_slide in processed_slides:
            print(processed_slide)
