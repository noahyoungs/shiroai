from typing import Dict, List, Optional, Union
import asyncio
from dynamodb import get_presentation as get_presentation_action, get_all_slides as get_all_slides_action, get_slides as get_slides_action, update_slides as update_slides_action
from slides.slide_models import Slide as SlideModel

async def _get_head_slide_id_action(presentation_id: str) -> str:
    """
    Retrieves the head slide ID for a given presentation.

    Args:
        presentation_id (str): The ID of the presentation.

    Returns:
        str: The head slide ID.
    """
    presentation = await get_presentation_action(presentation_id, ["head_slide_id"])
    return presentation.get("head_slide_id")

class PersistentSlideList:
    def __init__(self, presentation_id: str, slides: Optional[List[SlideModel]] = None):
        """
        Initializes a PersistentSlideList object.

        Args:
            presentation_id (str): The ID of the presentation.
            initial_slides (Optional[List[SlideModel]]): An optional list of initial slides.
        """
        self.presentation_id = presentation_id
        self.head_id = ""
        self.slides: Dict[str, SlideModel] = {}
        self.length = 0
        self.saving = False
        
        if slides:
            self._initialize_slides(slides)

    def _initialize_slides(self, initial_slides: List[SlideModel]):
        """
        Initializes the slides in the linked list.

        Args:
            initial_slides (List[SlideModel]): A list of slides to initialize.
        """
        if not initial_slides:
            return

        for slide in initial_slides:
            if not slide.id:
                raise ValueError("Each slide must have an ID")

        self.head_id = initial_slides[0].id
        for i, slide in enumerate(initial_slides):
            self.slides[slide.id] = slide
            self.length += 1
            if i == 0:
                slide.previous = None  # The first slide's previous should be None
            else:
                slide.previous = initial_slides[i - 1].id
            
            if i == len(initial_slides) - 1:
                slide.next = None  # The last slide's next should be None
            else:
                slide.next = initial_slides[i + 1].id

        # Update slides in DynamoDB
        asyncio.create_task(self._update_slides_in_db(initial_slides))

    async def _update_slides_in_db(self, slides: List[SlideModel]):
        """
        Updates the slides in the DynamoDB.

        Args:
            slides (List[SlideModel]): A list of slides to update.
        """
        await update_slides_action(self.presentation_id, slides)

    async def fetch_all_slides(self):
        """
        Fetches all slides for the presentation and stores them in the linked list.
        """
        self.slides = {}
        self.length = 0
        
        if not self.head_id:
            self.head_id = await _get_head_slide_id_action(self.presentation_id)

        slides_data = await get_all_slides_action(self.presentation_id)
        if slides_data:
            for slide in slides_data:
                self.slides[slide.id] = slide
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

    async def fetch_slide(self, slide_id: str) -> List[SlideModel]:
        """
        Fetches a specific slide by its ID.

        Args:
            slide_id (str): The ID of the slide to fetch.

        Returns:
            List[SlideModel]: A list containing the fetched slide.
        """
        fetched_slides = await get_slides_action(self.presentation_id, slide_id)

        if not fetched_slides:
            raise ValueError(f"Error: Slide with ID {slide_id} not found")

        if isinstance(fetched_slides, SlideModel):
            fetched_slides = [fetched_slides]

        for slide in fetched_slides:
            if slide.id not in self.slides:
                self.length += 1
            self.slides[slide.id] = slide

        return fetched_slides

    async def update_slides(self, slides: Union[SlideModel, List[SlideModel]], wait_for_db: bool = False):
        """
        Updates slides in the linked list and optionally waits for the database update.

        Args:
            slides (Union[SlideModel, List[SlideModel]]): The slide or list of slides to update.
            wait_for_db (bool): Whether to wait for the database update or not.
        """
        self.saving = True
        try:
            slides_to_update = []

            if not isinstance(slides, list):
                slides = [slides]

            for slide in slides:
                if not slide.id:
                    raise ValueError("Slide id is required")

                if slide.id not in self.slides:
                    raise ValueError(f"Slide with id {slide.id} does not exist")

                existing_slide = self.slides[slide.id]
                slides_to_update.append(slide)
                self.slides[slide.id] = slide

            if wait_for_db:
                await update_slides_action(self.presentation_id, slides_to_update)
            else:
                asyncio.create_task(update_slides_action(self.presentation_id, slides_to_update))
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
            new_slide_id = new_slide.id

            self.slides[new_slide_id] = new_slide
            self.length += 1

            previous_slide.next = new_slide_id
            if next_slide_id:
                self.slides[next_slide_id].previous = new_slide_id

            slides_to_update = [
                SlideModel(previous_slide.id, next=new_slide_id),
                SlideModel(new_slide_id, previous=previous_slide.id, next=next_slide_id)
            ]
            if next_slide_id:
                slides_to_update.append(SlideModel(next_slide_id, previous=new_slide_id))

            if wait_for_db:
                await update_slides_action(self.presentation_id, slides_to_update)
            else:
                asyncio.create_task(update_slides_action(self.presentation_id, slides_to_update))
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
                SlideModel(id=slide_id, hidden=True)
            ]

            if previous_slide_id:
                slides_to_update.append(SlideModel(id=previous_slide_id, next=next_slide_id))
            if next_slide_id:
                slides_to_update.append(SlideModel(id=next_slide_id, previous=previous_slide_id))

            if wait_for_db:
                await update_slides_action(self.presentation_id, slides_to_update)
            else:
                asyncio.create_task(update_slides_action(self.presentation_id, slides_to_update))
        finally:
            self.saving = False

    def get_slide(self, slide_id: str) -> Optional[SlideModel]:
        """
        Retrieves a slide by its ID.

        Args:
            slide_id (str): The ID of the slide to retrieve.

        Returns:
            Optional[SlideModel]: The slide if found, or None if not found.
        """
        if slide_id not in self.slides:
            raise ValueError(f"Slide with id {slide_id} does not exist")
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
    presentation_id = "presentation123"
    initial_slides = [
        SlideModel(slide_title="Slide 1", id="slide1"),
        SlideModel(slide_title="Slide 2", id="slide2"),
        SlideModel(slide_title="Slide 3", id="slide3"),
    ]
    persistent_slide_list = PersistentSlideList(presentation_id, initial_slides)

    # Fetch all slides and store them in the linked list
    await persistent_slide_list.fetch_all_slides()
    slides_array = persistent_slide_list.convert_to_array()
    print("Slides in order:", [slide.id for slide in slides_array])

    # Fetch specific slides and update them in the linked list
    await persistent_slide_list.fetch_slide("slide2")

    # Update a single slide
    await persistent_slide_list.update_slides(SlideModel(slide_title="Slide 2", id="slide2", hidden=True))

    # Add a new slide after a specific slide
    await persistent_slide_list.add_slide("slide2", SlideModel(slide_title="New Slide", id="slide_new", hidden=False))

    # Hide a slide
    await persistent_slide_list.hide_slide("slide2")

if __name__ == "__main__":
    # Run the example
    asyncio.run(main())
