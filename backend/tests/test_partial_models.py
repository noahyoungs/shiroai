from backend.database_models import *
import pytest

def test_partial_excerpt():
    PartialExcerpt = Excerpt.partial()
    partial_instance = PartialExcerpt(source_id="source1")
    assert partial_instance.source_id == "source1"
    assert partial_instance.excerpt_id is None
    assert partial_instance.text is None

def test_partial_image():
    PartialImage = Image.partial()
    partial_instance = PartialImage()
    assert partial_instance.s3_key is None
    assert partial_instance.url is None
    assert partial_instance.prompt is None

def test_partial_icon_data():
    PartialIconData = IconData.partial()
    partial_instance = PartialIconData(name="icon1", source="source1")
    assert partial_instance.name == "icon1"
    assert partial_instance.source == "source1"
    assert partial_instance.detailed_name is None

def test_partial_llm_message():
    PartialLLMMessage = LLMMessage.partial()
    partial_instance = PartialLLMMessage(role="user", content="Hello!")
    assert partial_instance.role == "user"
    assert partial_instance.content == "Hello!"

def test_partial_base_slide():
    PartialBaseSlide = BaseSlide.partial()
    partial_instance = PartialBaseSlide(slide_title="Test Slide")
    assert partial_instance.slide_title == "Test Slide"
    assert partial_instance.topic_id is None
    assert partial_instance.hidden is None  # Changed from False to None
    # We expect hidden to be None because we are testing a partial model

def test_partial_short_bullet_content():
    PartialShortBulletContent = ShortBulletContent.partial()
    partial_instance = PartialShortBulletContent(
        content="Test Content", 
        icon=IconData(name="icon", source="test"), 
        id="1"
    )
    assert partial_instance.content == "Test Content"
    assert partial_instance.icon.name == "icon"
    assert partial_instance.source_excerpt_id is None

def test_partial_topic():
    PartialTopic = Topic.partial()
    partial_instance = PartialTopic(id="topic1")
    assert partial_instance.id == "topic1"
    assert partial_instance.title is None
    assert partial_instance.additional_attributes is None  # Changed from {} to None
    # We expect additional_attributes to be None because we are testing a partial model
