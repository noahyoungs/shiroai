from pydantic import BaseModel, Field
from typing import List, Literal, Dict, Optional, Union, Any
import random
from uuid_extensions import uuid7str

def random_layout():
    return random.choice(['list', 'grid'])

def random_image_position():
    return random.choice(['left', 'right'])

class Excerpt(BaseModel):
    source_id: str
    excerpt_id: str
    text: str

class Image(BaseModel):
    s3_key: Optional[str] = None
    url: Optional[str] = None
    prompt: Optional[str] = None
    negative_prompt: Optional[str] = None
    style: Optional[str] = None
    model: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    shape: Optional[str] = None
    type: Optional[str] = None

class IconData(BaseModel):
    name: Optional[str] = None
    source: Optional[str] = None
    detailed_name: Optional[str] = None

class LLMMessage(BaseModel):
    role: Literal['user', 'assistant', 'system']
    content: str

class BaseSlide(BaseModel):
    slide_title: str
    topic_id: Optional[str] = None
    id: str
    hidden: bool = False
    generation_messages: Optional[List[LLMMessage]] = Field(default_factory=list)
    additional_fields: Dict[str, Union[str, int, float, bool, None]] = Field(default_factory=dict)
    next: Optional[str] = None
    previous: Optional[str] = None

class ShortBulletContent(BaseModel):
    content: str
    source_excerpt_id: Optional[str] = None
    excerpt: Optional[Excerpt] = None
    icon: Optional[IconData] = None
    id: str = Field(default_factory=uuid7str)

class ShortBulletsSlide(BaseSlide):
    slide_type: Literal['short_bullets_slide']
    slide_content: List[ShortBulletContent]
    sequential: bool
    layout: Literal['list', 'grid'] = Field(default_factory=random_layout)

class SimpleMermaidSlide(BaseSlide):
    slide_type: Literal['simple_mermaid_slide']
    slide_content: Dict[str, Union[str, List[Excerpt]]] = {
        'mermaid_code': '',
        'excerpts': [],
        'light_svg': '',
        'dark_svg': ''
    }

class MarkdownSlide(BaseSlide):
    slide_type: Literal['markdown_slide']
    slide_content: Any

class SectionHeaderSlide(BaseSlide):
    slide_type: Literal['section_header_slide']
    slide_title: Optional[str] = None
    image: Image
    image_position: Literal['left', 'right'] = Field(default_factory=random_image_position)

class PresentationTitleSlide(BaseSlide):
    slide_type: Literal['presentation_title_slide']
    slide_title: Optional[str] = None
    image: Image
    
class Topic(BaseModel):
    id: str = Field(default_factory=uuid7str)
    title: Optional[str] = None
    reduced_docs: Optional[Any]
    
    additional_attributes: Dict[str, Any] = {}

    class Config:
        extra = 'allow'

Slide = Union[ShortBulletsSlide, MarkdownSlide, SimpleMermaidSlide, SectionHeaderSlide, PresentationTitleSlide]

__all__ = [
    'Excerpt', 'Image', 'IconData', 'BaseSlide', 'ShortBulletContent', 
    'ShortBulletsSlide', 'SimpleMermaidSlide', 'MarkdownSlide', 
    'SectionHeaderSlide', 'PresentationTitleSlide', 'Slide', 'LLMMessage', 'Topic'
]
