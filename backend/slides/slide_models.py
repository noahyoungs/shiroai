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

    def __repr__(self):
        return f"Excerpt(source_id={self.source_id}, excerpt_id={self.excerpt_id}, text={self.text})"

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

    def __repr__(self):
        return (f"Image(s3_key={self.s3_key}, url={self.url}, prompt={self.prompt}, "
                f"negative_prompt={self.negative_prompt}, style={self.style}, model={self.model}, "
                f"width={self.width}, height={self.height}, shape={self.shape}, type={self.type})")

class IconData(BaseModel):
    name: str
    source: str
    detailed_name: Optional[str] = None

    def __repr__(self):
        return f"IconData(name={self.name}, source={self.source}, detailed_name={self.detailed_name})"

class LLMMessage(BaseModel):
    role: str
    content: str

    def __repr__(self):
        return f"LLMMessage(role={self.role}, content={self.content})"
            
class BaseSlide(BaseModel):
    slide_title: str
    topic_id: Optional[str] = None
    id: str
    hidden: Optional[bool] = False
    previous: Optional[str] = None
    next: Optional[str] = None
    generation_messages: Optional[List[LLMMessage]] = None
    script: Optional[str] = None
    speaker_notes: Optional[str] = None
    extra: Dict[str, Any] = Field(default_factory=dict)

    def __repr__(self):
        return (f"BaseSlide(slide_title={self.slide_title}, topic_id={self.topic_id}, id={self.id}, "
                f"hidden={self.hidden}, previous={self.previous}, next={self.next}, "
                f"generation_messages={self.generation_messages}, extra={self.extra})")

class ShortBulletContent(BaseModel):
    content: str
    source_excerpt_id: Optional[str] = None
    excerpt: Optional[Excerpt] = None
    icon: IconData
    id: str

    def __repr__(self):
        return (f"ShortBulletContent(content={self.content}, source_excerpt_id={self.source_excerpt_id}, "
                f"excerpt={self.excerpt}, icon={self.icon}, id={self.id})")

class ShortBulletsSlide(BaseSlide):
    slide_type: str = 'short_bullets_slide'
    slide_content: List[ShortBulletContent]
    sequential: bool
    layout: str = Field(default_factory=random_layout)  # 'list' or 'grid'

    def __repr__(self):
        return (f"ShortBulletsSlide(slide_type={self.slide_type}, slide_title={self.slide_title}, slide_content={self.slide_content}, "
                f"sequential={self.sequential}, layout={self.layout})")

class SimpleMermaidSlide(BaseSlide):
    slide_type: str = 'simple_mermaid_slide'
    slide_content: Dict[str, Any]  # This should be a dictionary with keys 'mermaid_code', 'excerpts', 'light_svg', 'dark_svg'

    def __repr__(self):
        return (f"SimpleMermaidSlide(slide_type={self.slide_type}, slide_title={self.slide_title}, slide_content={self.slide_content})")

class MarkdownSlide(BaseSlide):
    slide_type: str = 'markdown_slide'
    slide_content: Dict[str, Any]  # This should be a dictionary with keys 'content', 'footnotes', and optional 'prose_class'

    def __repr__(self):
        return (f"MarkdownSlide(slide_type={self.slide_type}, slide_title={self.slide_title}, slide_content={self.slide_content})")

class SectionHeaderSlide(BaseSlide):
    slide_type: str = 'section_header_slide'
    image: Image
    image_position: str = Field(default_factory=random_image_position)  # 'left' or 'right'

    def __repr__(self):
        return (f"SectionHeaderSlide(slide_type={self.slide_type}, slide_title={self.slide_title}, "
                f"image={self.image}, image_position={self.image_position})")

class PresentationTitleSlide(BaseSlide):
    slide_type: str = 'presentation_title_slide'
    image: Image

    def __repr__(self):
        return (f"PresentationTitleSlide(slide_type={self.slide_type}, slide_title={self.slide_title}, "
                f"image={self.image})")
    
class Topic(BaseModel):
    id: str = Field(default_factory=uuid7str)
    title: Optional[str] = None
    reduced_docs: Optional[Any] = None
    
    additional_attributes: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        extra = 'allow'

    def __repr__(self):
        return (f"Topic(id={self.id}, title={self.title}, reduced_docs={self.reduced_docs}, "
                f"additional_attributes={self.additional_attributes})")

Slide = Union[ShortBulletsSlide, MarkdownSlide, SimpleMermaidSlide, SectionHeaderSlide, PresentationTitleSlide]

__all__ = [
    'Excerpt', 'Image', 'IconData', 'BaseSlide', 'ShortBulletContent', 
    'ShortBulletsSlide', 'SimpleMermaidSlide', 'MarkdownSlide', 
    'SectionHeaderSlide', 'PresentationTitleSlide', 'Slide', 'LLMMessage', 'Topic'
]