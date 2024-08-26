
    
    

async def generate_all_notes(psl: PersistentSlideList, writing_style_instructions: str):
    # print(f"Generating notes for presentation {psl.presentation_id}")
    # topics: List[Topic] = await get_all_topics(psl.presentation_id)
    # presentation = await get_presentation(psl.presentation_id, ['topic', 'audience', 'goal'])
    # topic_notes_d = {topic.id: topic.title for topic in topics}
    
    # slides_l: List[Slide] = psl.convert_to_array()
    
    # async def generate_note(slide: Slide):
    #     try:
    #         topic_string = topic_notes_d.get(slide.topic_id)
    #         note = await get_notes_for_slide(
    #             presentation_topic=presentation['topic'],
    #             target_audience=presentation['audience'],
    #             presentation_goal=presentation['goal'],
    #             section_title=topic_string,
    #             slide=slide,
    #             writing_style_instructions=writing_style_instructions
    #         )
    #         return slide.id, note
    #     except Exception as e:
    #         print(f"Error generating note for slide {slide.id}: {str(e)}")
    #         return slide.id, None

    # results = await asyncio.gather(*(generate_note(slide) for slide in slides_l))
    # print(f"Generated notes for {len(results)} slides")

    # update_partial_slides = [{'id': slide_id, 'speaker_notes': note} for slide_id, note in results if note is not None]
    # print(f"Updating {len(update_partial_slides)} slides with generated notes")
    # await psl.update_slides(update_partial_slides)
    # print("Notes generated and updated")
    print("Notes generation is not implemented")
    pass
