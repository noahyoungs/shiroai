# backend/database_models.py

from pydantic import BaseModel, create_model, Field, ConfigDict
from typing import List, Literal, Dict, Optional, Union, Any, get_type_hints
import random
from uuid_extensions import uuid7str

def random_layout():
    return random.choice(['list', 'grid'])

def random_image_position():
    return random.choice(['left', 'right'])

class Partialable(BaseModel):
    """
    A base class to create a partial model where all fields are optional.

    This class provides a `partial()` class method that generates a new model
    where all fields are optional. This is useful when you want to create a 
    model that can be instantiated with a subset of fields, without requiring 
    all fields to be provided.

    **Important Note:**
    - When using the `partial()` method to create a partial model, default values
      defined in the original model are not applied. Instead, fields that are not 
      provided will be set to `None`. This differs from the behavior of the 
      original models where fields with default values are automatically populated.
    
    **Usage Example:**

    ```python
    class ExampleModel(Partialable):
        name: str
        age: Optional[int] = 30

    PartialExampleModel = ExampleModel.partial()
    
    # Create an instance of the partial model with only the `name` field
    instance = PartialExampleModel(name="Noah")

    # Output:
    # instance.name == "Noah"
    # instance.age is None
    ```

    In this example, `PartialExampleModel` allows creating instances with only
    a subset of fields. The `age` field, even though it has a default value in
    the original model, is `None` in the partial instance because the partial model
    does not use default values from the original model.
    """

    @classmethod
    def partial(cls):
        # Dynamically create a model with all fields set to Optional
        fields = {
            field: (Optional[typ], None) if not isinstance(typ, type(Optional)) else (typ, None)
            for field, typ in get_type_hints(cls).items()
        }
        return create_model(f'Partial{cls.__name__}', **fields)

class Excerpt(Partialable):
    source_id: str
    excerpt_id: str
    text: str

    def __repr__(self):
        return f"Excerpt(source_id={self.source_id}, excerpt_id={self.excerpt_id}, text={self.text})"





class BaseSlide(Partialable):
    user_id: Optional[str] = None # This is required in the database but the dynamodb_service will fill it in
    slide_id: str
    presentation_id: str
    topic_id: Optional[str] = None
    slide_title: str
    presentation_id: str
    hidden: Optional[bool] = False
    previous: Optional[str] = None
    next: Optional[str] = None
    generation_messages: Optional[List[Dict]] = None
    script: Optional[str] = None
    speaker_notes: Optional[str] = None
    extra: Dict[str, Any] = Field(default_factory=dict)

    def __repr__(self):
        return (f"BaseSlide(slide_title={self.slide_title}, topic_id={self.topic_id}, id={self.slide_id}, "
                f"hidden={self.hidden}, previous={self.previous}, next={self.next}, "
                f"generation_messages={self.generation_messages}, extra={self.extra})")


class ShortBulletsSlide(BaseSlide):
    slide_type: str = 'short_bullets_slide'
    slide_content: List[dict]
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
    image: dict
    image_position: str = Field(default_factory=random_image_position)  # 'left' or 'right'

    def __repr__(self):
        return (f"SectionHeaderSlide(slide_type={self.slide_type}, slide_title={self.slide_title}, "
                f"image={self.image}, image_position={self.image_position})")

class PresentationTitleSlide(BaseSlide):
    slide_type: str = 'presentation_title_slide'
    image: dict

    def __repr__(self):
        return (f"PresentationTitleSlide(slide_type={self.slide_type}, slide_title={self.slide_title}, "
                f"image={self.image})")
    
class Topic(Partialable):
    user_id: Optional[str] = None # This is required in the database but the dynamodb_service will fill it in
    presentation_id: str
    topic_id: str = Field(default_factory=uuid7str)
    title: Optional[str] = None
    reduced_docs: Optional[Any] = None
    additional_attributes: Dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(extra="allow")

    def __repr__(self):
        return (f"Topic(id={self.topic_id}, title={self.title}, reduced_docs={self.reduced_docs}, "
                f"additional_attributes={self.additional_attributes})")

Slide = Union[ShortBulletsSlide, MarkdownSlide, SimpleMermaidSlide, SectionHeaderSlide, PresentationTitleSlide]

__all__ = [
    'Excerpt', 'BaseSlide', 
    'ShortBulletsSlide', 'SimpleMermaidSlide', 'MarkdownSlide', 
    'SectionHeaderSlide', 'PresentationTitleSlide', 'Slide', 'Topic'
]
