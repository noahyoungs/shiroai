from typing import Dict, List, Optional, Union, Callable
import asyncio
from dynamodb_service import get_items_with_user, get_all_items_for_presentation_with_user, update_items_with_user
from database_models import Slide as SlideModel

async def _get_head_slide_id_action(presentation_id: str) -> str:
    """
    Retrieves the head slide ID for a given presentation.

    Args:
        presentation_id (str): The ID of the presentation.

    Returns:
        str: The head slide ID.
    """
    # presentation = await get_presentation_action(presentation_id, ["head_slide_id"])
    presentation = await get_items_with_user('presentation', {'presentation_id': presentation_id}, ['head_slide_id'])
    return presentation.get("head_slide_id")


class PersistentSlideList:
    def __init__(self, presentation_id: str, slides: Optional[List[SlideModel]] = None, emitter: Callable[[str, Dict], None] = None):
        """
        Initializes a PersistentSlideList object.

        Args:
            presentation_id (str): The ID of the presentation.
            initial_slides (Optional[List[SlideModel]]): An optional list of initial slides.
            emitter (Callable[[str, Dict], None]): An optional emitter function for event handling.
        """
        self.presentation_id = presentation_id
        self.head_id = ""
        self.slides: Dict[str, SlideModel] = {}
        self.length = 0
        self.saving = False
        self.emitter = emitter
        
        if slides:
            self._initialize_slides(slides)

    async def _update_dynamodb_then_emit_update(self, slides_to_update, push_value=None):
        """
        Updates the slides in DynamoDB and emits an update event for all slides.
        
        Args:
            slides_to_update (List[SlideModel]): The slides to update.
            push_value (Union[str, List[str]]): The value include for push in the emiited socket message. Defaults to slide ids of slides_to_update.
        """
        # must be list
        if not isinstance(slides_to_update, list):
            slides_to_update = [slides_to_update]
            
        # error on length 0
        if len(slides_to_update) == 0:
            raise ValueError("No slides to update")
        
        if push_value is None:
            if isinstance(slides_to_update[0], SlideModel):
                push_value = [slide.slide_id for slide in slides_to_update]
            elif isinstance(slides_to_update[0], dict):
                push_value = [slide['slide_id'] for slide in slides_to_update]
            else:
                raise ValueError("Invalid slide type _update_dynamodb_then_emit_update")
            
            if len(push_value) == 1:
                push_value = push_value[0]
        
        await update_items_with_user('slide', slides_to_update)
        print(f"Emitting interface_update event, ")
        await self.emitter('interface_update', {'push': push_value})
        

    def _initialize_slides(self, initial_slides: List[SlideModel]):
        """
        Initializes the slides in the linked list.

        Args:
            initial_slides (List[SlideModel]): A list of slides to initialize.
        """
        if not initial_slides:
            return

        for slide in initial_slides:
            if not hasattr(slide, 'slide_id') or not slide.slide_id:
                print(f"Slide: {slide}")
                raise ValueError("Each slide must have an ID")

        self.head_id = initial_slides[0].slide_id
        for i, slide in enumerate(initial_slides):
            self.slides[slide.slide_id] = slide
            self.length += 1
            if i == 0:
                slide.previous = None  # The first slide's previous should be None
            else:
                slide.previous = initial_slides[i - 1].slide_id
            
            if i == len(initial_slides) - 1:
                slide.next = None  # The last slide's next should be None
            else:
                slide.next = initial_slides[i + 1].slide_id

        # Update slides in DynamoDB then emit an update event
        asyncio.create_task(self._update_dynamodb_then_emit_update(initial_slides, push_value='*'))
        

    async def fetch_all_slides(self):
        """
        Fetches all slides for the presentation and stores them in the linked list.
        """
        self.slides = {}
        self.length = 0
        
        if not self.head_id:
            self.head_id = await _get_head_slide_id_action(self.presentation_id)

        # slides_data = await get_all_slides_action(self.presentation_id)
        slides_data = await get_all_items_for_presentation_with_user('slide', self.presentation_id, return_type='model')
        if slides_data:
            for slide in slides_data:
                self.slides[slide.slide_id] = slide
                self.length += 1

    def convert_to_array(self) -> List[SlideModel]:
        """
        Converts the linked list of slides to an ordered array.

        Returns:
            List[SlideModel]: An ordered list of slides.
        """
        result = []
        current_id = self.head_id
        while current_id:
            slide = self.slides[current_id]
            if not slide.hidden:
                result.append(slide)
            current_id = slide.next

        return result

    async def fetch_slides(self, slide_ids: Union[str, List[str]]) -> List[SlideModel]:
        """
        Fetches one or more slides by their IDs.

        Args:
            slide_ids (Union[str, List[str]]): A single slide ID or a list of slide IDs to fetch.

        Returns:
            List[SlideModel]: A list of fetched slides.
        """
        # fetched_slides = await get_slides_action(self.presentation_id, slide_ids)
        if isinstance(slide_ids, str):
            identifiers = {'presentation_id': self.presentation_id, 'slide_id': slide_ids}
        elif isinstance(slide_ids, list):
            identifiers = [{'presentation_id': self.presentation_id, 'slide_id': slide_id} for slide_id in slide_ids]
        else:
            raise ValueError("Slide IDs must be either a string or a list of strings")

        fetched_slides = await get_items_with_user('slide', identifiers, return_type='model')

        if not fetched_slides:
            raise ValueError(f"Error: Slides with IDs {slide_ids} not found")

        if isinstance(fetched_slides, SlideModel):
            fetched_slides = [fetched_slides]

        for slide in fetched_slides:
            if slide.slide_id not in self.slides:
                self.length += 1
            self.slides[slide.slide_id] = slide

        return fetched_slides

    async def update_slides(self, slides: Union[SlideModel, Dict, List[Union[SlideModel, Dict]]], wait_for_db: bool = False):
        """
        Updates slides in the linked list and optionally waits for the database update.

        Args:
            slides (Union[SlideModel, Dict, List[Union[SlideModel, Dict]]]): The slide(s) to update.
            wait_for_db (bool): Whether to wait for the database update or not.
        """
        print("Updating slides")
        self.saving = True
        try:
            slides_to_update = []

            if not isinstance(slides, list):
                print("Converting slides to list")
                slides = [slides]

            for slide in slides:
                if isinstance(slide, SlideModel):
                    print("SlideModel")
                    if not slide.slide_id:
                        raise ValueError("Slide id is required")

                    if slide.slide_id not in self.slides:
                        raise ValueError(f"Slide with id {slide.slide_id} does not exist")

                    # Update self.slides before performing the DynamoDB operation
                    self.slides[slide.slide_id] = slide
                    slides_to_update.append(slide)
                elif isinstance(slide, dict):
                    print("Dict")
                    slide_id = slide.get('slide_id')
                    if not slide_id:
                        raise ValueError("Slide id is required in the dictionary")

                    if slide_id not in self.slides:
                        raise ValueError(f"Slide with id {slide_id} does not exist")

                    # Update the relevant slide directly
                    for key, value in slide.items():
                        setattr(self.slides[slide_id], key, value)
                    slides_to_update.append(slide)
                else:
                    raise ValueError("Slides must be either SlideModel or dict types")

            # Optimize _update_dynamodb_then_emit_update call for a single slide update
            if len(slides_to_update) == 1:
                slides_to_update = slides_to_update[0]

            if wait_for_db:
                await self._update_dynamodb_then_emit_update(slides_to_update)
            else:
                asyncio.create_task(self._update_dynamodb_then_emit_update(slides_to_update))

        finally:
            self.saving = False



    async def add_slide(self, previous_slide_id: str, new_slide: SlideModel, wait_for_db: bool = False):
        """
        Adds a new slide after a specific slide.

        Args:
            previous_slide_id (str): The ID of the previous slide.
            new_slide (SlideModel): The new slide to add.
            wait_for_db (bool): Whether to wait for the database update or not.
        """
        self.saving = True
        try:
            previous_slide = self.slides[previous_slide_id]
            next_slide_id = previous_slide.next
            new_slide_id = new_slide.slide_id

            self.slides[new_slide_id] = new_slide
            self.length += 1

            previous_slide.next = new_slide_id
            if next_slide_id:
                self.slides[next_slide_id].previous = new_slide_id

            slides_to_update = [
                SlideModel(id=previous_slide.slide_id, next=new_slide_id),
                SlideModel(id=new_slide_id, previous=previous_slide.slide_id, next=next_slide_id)
            ]
            if next_slide_id:
                slides_to_update.append(SlideModel(id=next_slide_id, previous=new_slide_id))

            if wait_for_db:
                await self._update_dynamodb_then_emit_update(slides_to_update)
            else:
                asyncio.create_task(self._update_dynamodb_then_emit_update(slides_to_update))
                
        finally:
            self.saving = False

    async def hide_slide(self, slide_id: str, wait_for_db: bool = False):
        """
        Hides a slide by setting its hidden property to true and updates the linked list pointers.

        Args:
            slide_id (str): The ID of the slide to hide.
            wait_for_db (bool): Whether to wait for the database update or not.
        """
        self.saving = True
        try:
            slide_to_hide = self.slides.get(slide_id)
            
            if not slide_to_hide:
                raise ValueError(f"Slide with id {slide_id} does not exist")

            # Set the slide's hidden property to true
            slide_to_hide.hidden = True

            # Update pointers
            previous_slide_id = slide_to_hide.previous
            next_slide_id = slide_to_hide.next

            if previous_slide_id:
                self.slides[previous_slide_id].next = next_slide_id

            if next_slide_id:
                self.slides[next_slide_id].previous = previous_slide_id

            slides_to_update = [
                {'slide_id': slide_id, 'hidden': True}
            ]

            if previous_slide_id:
                slides_to_update.append({'slide_id': previous_slide_id, 'next': next_slide_id})
            if next_slide_id:
                slides_to_update.append({'slide_id': next_slide_id, 'previous': previous_slide_id})

            if wait_for_db:
                await self._update_dynamodb_then_emit_update(slides_to_update)
            else:
                asyncio.create_task(self._update_dynamodb_then_emit_update(slides_to_update))
                
        finally:
            self.saving = False

    async def get_slide(self, slide_id: str) -> Optional[SlideModel]:
        """
        Retrieves a slide by its ID.

        Args:
            slide_id (str): The ID of the slide to retrieve.

        Returns:
            Optional[SlideModel]: The slide if found, or None if not found.
        """
        if slide_id not in self.slides:
            print(f"WARNING: Attepted to get slide with id {slide_id} which does not exist locally. Attempting to fetch from dynmamodb.")
            
            # fetched_slide = await get_slides_action(self.presentation_id, slide_id)
            fetched_slide = await get_items_with_user('slide', [{'presentation_id': self.presentation_id, 'slide_id': slide_id}], 'model')
            
            print(f"fetched slide {fetched_slide}")

            if not fetched_slide:
                raise ValueError(f"Error: Slides with IDs {slide_id} not found in local storage or dynamodb")
            else:
                self.length += 1
                self.slides[slide_id] = fetched_slide
                return fetched_slide
                    
        return self.slides[slide_id]

    def get_head_slide_id(self) -> str:
        """
        Retrieves the head slide ID of the linked list.

        Returns:
            str: The head slide ID.
        """
        return self.head_id

    def get_saving_status(self) -> bool:
        """
        Retrieves the current saving status.

        Returns:
            bool: True if saving, False otherwise.
        """
        return self.saving

# Example usage
async def main():
    """
    Example usage of the PersistentSlideList class.
    """
    async def mock_emitter(event_type, data):
        print(f"Event emitted: {event_type} with data: {data}")

    presentation_id = "presentation123"
    initial_slides = [
        SlideModel(slide_title="Slide 1", id="slide1"),
        SlideModel(slide_title="Slide 2", id="slide2"),
        SlideModel(slide_title="Slide 3", id="slide3"),
    ]
    persistent_slide_list = PersistentSlideList(presentation_id, initial_slides, emitter=mock_emitter)

    # Fetch all slides and store them in the linked list
    await persistent_slide_list.fetch_all_slides()
    slides_array = persistent_slide_list.convert_to_array()
    print("Slides in order:", [slide.slide_id for slide in slides_array])

    # Fetch specific slides and update them in the linked list
    await persistent_slide_list.fetch_slides("slide2")

    # Update a single slide
    await persistent_slide_list.update_slides(SlideModel(slide_title="Slide 2", id="slide2", hidden=True))

    # Add a new slide after a specific slide
    await persistent_slide_list.add_slide("slide2", SlideModel(slide_title="New Slide", id="slide_new", hidden=False))

    # Hide a slide
    await persistent_slide_list.hide_slide("slide2")

if __name__ == "__main__":
    # Run the example
    asyncio.run(main())

