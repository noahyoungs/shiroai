from uuid_extensions import uuid7str
from database_models import SectionHeaderSlide
from slides.images.generate_image import generate_and_upload_image

async def get_section_header_slide(presentation_id, presentation_topic, presentation_audience, presentation_goal, subtopic_name):
    image_data, messages = await generate_and_upload_image(presentation_id, presentation_audience, presentation_goal, presentation_topic, section_topic=subtopic_name, shape="square", model_type="sdxl")

    return SectionHeaderSlide(
        slide_title=subtopic_name,
        presentation_id=presentation_id,
        slide_id=uuid7str(),
        generation_messages=messages,
        slide_type='section_header_slide',
        image=image_data,
    )