from uuid_extensions import uuid7str
from slides.slide_models import PresentationTitleSlide
from slides.images.generate_image import generate_and_upload_image

async def get_presentation_title_slide(presentation_id, presentation_topic, presentation_audience, presentation_goal):
    image_data, messages = await generate_and_upload_image(presentation_id, presentation_topic, presentation_audience, presentation_goal, section_topic=None, shape="full", model_type="core")
    
    return [PresentationTitleSlide(
        slide_title=presentation_topic,
        id=uuid7str(),
        generation_messages=messages,
        slide_type='presentation_title_slide',
        image=image_data
    )]