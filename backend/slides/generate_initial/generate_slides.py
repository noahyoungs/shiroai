from dynamodb_service import get_items_with_user, delete_all_items_for_presentation_with_user, update_items_with_user
import json
import asyncio
from slides.reduce_topic_research import reduce_docs
from database_models import *
from slides.persistent_slide_list import PersistentSlideList
import traceback
from slides.add_prose_class_and_split import process_slide
from slides.generate_initial.slide_ideas import get_slide_ideas
from slides.generate_initial.short_bullets_slide import get_short_bullets_slide
from slides.generate_initial.long_bullets_slide import get_long_bullets_slide
from slides.generate_initial.markdown_table_slide import get_markdown_table_slide
from slides.generate_initial.simple_mermaid_slide import get_simple_mermaid_slide
from slides.generate_initial.section_header_slide import get_section_header_slide
from slides.generate_initial.presentation_title_slide import get_presentation_title_slide
from slides.generate_initial.utils import get_excerpt_ids, get_presentation_xml, get_subtopic_xml, get_research_xml
from slides.generate_initial.intro_conclusion_slides import get_intro_or_conclusion_slides


async def get_slide_content(presentation_id, presentation_xml, subtopic_xml, all_docs, slide_idea, excerpt_ids):
    slide_type = slide_idea['slide_type']
    if slide_type == 'short_bullets_slide':
        return await get_short_bullets_slide(presentation_id, presentation_xml, subtopic_xml, all_docs, slide_idea, excerpt_ids)
    elif slide_type == 'long_bullets_slide':
        return await get_long_bullets_slide(presentation_id, presentation_xml, subtopic_xml, all_docs, slide_idea, excerpt_ids)
    elif slide_type == 'markdown_table_slide':
        return await get_markdown_table_slide(presentation_id, presentation_xml, subtopic_xml, all_docs, slide_idea, excerpt_ids)
    elif slide_type == 'simple_mermaid_slide':
        return await get_simple_mermaid_slide(presentation_id, presentation_xml, subtopic_xml, all_docs, slide_idea, excerpt_ids)
    else:
        raise ValueError(f"Unknown slide type: {slide_type}")


async def get_slide_content_wrapper(presentation_id, presentation_xml, subtopic_xml, all_docs, slide_idea, excerpt_ids):
    try:
        slide = await get_slide_content(presentation_id, presentation_xml, subtopic_xml, all_docs, slide_idea, excerpt_ids)
        if slide.slide_type == 'markdown_slide':
            processed_slides = await process_slide(slide)
            return processed_slides
        return [slide]
    except Exception as e:
        print(f"Error creating slide: {e}")
        traceback.print_exc()
        return []


async def get_section_header_slide_wrapper(presentation_id, presentation_topic, presentation_audience, presentation_goal, subtopic_name, wrap_in_list=False):
    try:
        result = await get_section_header_slide(
            presentation_id=presentation_id,
            presentation_topic=presentation_topic,
            presentation_audience=presentation_audience,
            presentation_goal=presentation_goal,
            subtopic_name=subtopic_name
        )

        if wrap_in_list:
            return [result]
        else:
            return result

    except Exception as e:
        print(f"Error creating section header slide: {e}")
        traceback.print_exc()
        return None


async def get_topic_slides(presentation_id, presentation_topic, presentation_audience, presentation_goal, subtopic_name, subtopic_id, all_docs):
    presentation_xml = get_presentation_xml(
        presentation_topic, presentation_audience, presentation_goal)
    subtopic_xml = get_subtopic_xml(subtopic_name)
    reduced_docs = await reduce_docs(presentation_id, all_docs, 4000, subtopic_name, subtopic_id)
    research_xml = get_research_xml(reduced_docs)
    excerpt_ids = get_excerpt_ids(reduced_docs)

    slide_ideas = None
    try:
        slide_ideas = await get_slide_ideas(
            presentation_xml=presentation_xml,
            subtopic_xml=subtopic_xml,
            research_xml=research_xml
        )
    except Exception as e:
        print(f"Error getting slide idea for subtopic {subtopic_name}: {e}")
        return []

    slide_content_tasks = [
        get_slide_content_wrapper(
            presentation_id,
            presentation_xml,
            subtopic_xml,
            reduced_docs,
            slide_idea,
            excerpt_ids
        )
        for slide_idea in slide_ideas
    ]

    slides = await asyncio.gather(
        get_section_header_slide_wrapper(
            presentation_id=presentation_id,
            presentation_topic=presentation_topic,
            presentation_audience=presentation_audience,
            presentation_goal=presentation_goal,
            subtopic_name=subtopic_name
        ),
        *slide_content_tasks
    )

    section_header_slide = slides[0] if slides[0] is not None else None
    content_slides = [slide for slide_list in slides[1:]
                      for slide in slide_list if slide is not None]

    if section_header_slide is not None:
        content_slides.insert(0, section_header_slide)

    reduced_docs_no_embeddings = [
        {**doc, 'metadata': {**doc['metadata'], 'embedding': None}} for doc in reduced_docs]

    # asyncio.create_task(update_topics(presentation_id, Topic(
    #     id=subtopic_id, title=subtopic_name, reduced_docs=reduced_docs_no_embeddings)))
    asyncio.create_task(update_items_with_user('topic', [Topic(
        topic_id=subtopic_id, title=subtopic_name, reduced_docs=reduced_docs_no_embeddings, presentation_id=presentation_id)]))

    return content_slides


async def get_intro_conclusion_slides_wrapper(presentation_id, presentation_topic, presentation_audience, presentation_goal, slides, slide_type):
    try:
        slides = await get_intro_or_conclusion_slides(
            presentation_id=presentation_id,
            presentation_topic=presentation_topic,
            presentation_audience=presentation_audience,
            presentation_goal=presentation_goal,
            slides=slides,
            slide_type=slide_type
        )

        all_processed_slides = []

        for slide in slides:
            if slide.slide_type == 'markdown_slide':
                processed_slides = await process_slide(slide)
                all_processed_slides.extend(processed_slides)
            else:
                all_processed_slides.append(slide)

        return all_processed_slides

    except Exception as e:
        print(f"Error creating {slide_type} slide: {e}")
        traceback.print_exc()
        return []


async def get_presentation_title_wrapper(presentation_id, presentation_topic, presentation_audience, presentation_goal):
    try:
        return await get_presentation_title_slide(
            presentation_id=presentation_id,
            presentation_topic=presentation_topic,
            presentation_audience=presentation_audience,
            presentation_goal=presentation_goal
        )
    except Exception as e:
        print(f"Error creating presentation title slide: {e}")
        traceback.print_exc()
        return None


async def make_presentation_slides(presentation_id, emitter, all_docs=None,):
    print("REMAKING SLIDES")
    # presentation = await get_presentation(presentation_id, ["candidate_topics", "outline", "audience", "goal", "topic"])
    presentation = await get_items_with_user('presentation', {'presentation_id': presentation_id}, ["candidate_topics", "outline", "audience", "goal", "topic"])

    if not all(key in presentation for key in ["candidate_topics", "outline", "audience", "goal", "topic"]):
        raise ValueError("Missing required keys in presentation data")

    candidate_topics = json.loads(presentation["candidate_topics"])
    outline = json.loads(presentation["outline"])

    if candidate_topics is None or outline is None:
        raise ValueError("Missing candidate_topics or outline")

    final_topics = [(next((candidate_topic for candidate_topic in candidate_topics if candidate_topic['topic_id']
                     == outline_topic['topic_id']), None)) for outline_topic in outline if outline_topic['included']]

    if not final_topics:
        raise ValueError("No final topics found")

    slide_tasks = [
        get_presentation_title_wrapper(
            presentation_id=presentation_id,
            presentation_topic=presentation['topic'],
            presentation_audience=presentation['audience'],
            presentation_goal=presentation['goal'],
        )
    ] + [
        get_topic_slides(
            presentation_id=presentation_id,
            presentation_topic=presentation['topic'],
            presentation_audience=presentation['audience'],
            presentation_goal=presentation['goal'],
            subtopic_name=topic['name'],
            subtopic_id=topic['topic_id'],
            all_docs=all_docs
        )
        for topic in final_topics
    ] + [  # Add conclusion header slide
        get_section_header_slide_wrapper(
            presentation_id=presentation_id,
            presentation_topic=presentation['topic'],
            presentation_audience=presentation['audience'],
            presentation_goal=presentation['goal'],
            subtopic_name="Conclusion",
            wrap_in_list=True
        )
    ]

    slides_list = await asyncio.gather(*slide_tasks)

    for topic, topic_slides in zip(final_topics, slides_list[1:]):
        topic_id = topic['topic_id']
        for slide in topic_slides:
            slide.topic_id = topic_id

    flat_slides = [
        slide for topic_slides in slides_list for slide in topic_slides
    ]

    # Create and add intro and conclusion slides concurrently
    intro_slides, conclusion_slides = await asyncio.gather(
        get_intro_conclusion_slides_wrapper(
            presentation_id=presentation_id,
            presentation_topic=presentation['topic'],
            presentation_audience=presentation['audience'],
            presentation_goal=presentation['goal'],
            slides=flat_slides,
            slide_type="introduction"
        ),
        get_intro_conclusion_slides_wrapper(
            presentation_id=presentation_id,
            presentation_topic=presentation['topic'],
            presentation_audience=presentation['audience'],
            presentation_goal=presentation['goal'],
            slides=flat_slides,
            slide_type="conclusion"
        )
    )

    # Prepend intro slides and append conclusion slides to flat_slides
    flat_slides = flat_slides[:1] + intro_slides + \
        flat_slides[1:] + conclusion_slides

    # await delete_all_slides(presentation_id)
    await delete_all_items_for_presentation_with_user('slide', presentation_id)

    slide_list = PersistentSlideList(
        presentation_id, slides=flat_slides, emitter=emitter)

    # await update_presentation(presentation_id, slide_generation_status="complete", head_slide_id=flat_slides[0].id)
    await update_items_with_user('presentation', [{"presentation_id": presentation_id, "slide_generation_status": "complete", "head_slide_id": flat_slides[0].slide_id}])

    return slide_list
