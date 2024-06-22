import { Slide } from "./slide-types";
import {
  getHeadSlideID as getHeadSlideIDAction,
  getSlides as getSlidesAction,
  updateSlides as updateSlidesAction,
  getAllSlides as getAllSlidesAction,
} from "@/actions/slides-actions";

export class PersistentSlideList {
  private presentationID: string;
  private headID: string;
  private slides: { [key: string]: Slide };
  private saving: boolean;
  private errors: string[];
  length: number;

  constructor(presentationID: string) {
    this.presentationID = presentationID;
    this.headID = "";
    this.slides = {};
    this.length = 0;
    this.saving = false;
    this.errors = [];
  }

  /**
   * Fetches all slides for the current presentation and initializes the slides list.
   */
  async fetchAllSlides() {
    // Clear slides
    this.slides = {};
    this.length = 0;

    try {
      if (!this.headID) {
        this.headID = await getHeadSlideIDAction(this.presentationID);
      }

      const slidesData = await getAllSlidesAction(this.presentationID);
      if (slidesData) {
        slidesData.forEach((data: Slide) => {
          this.slides[data.id] = data;
          this.length++;
        });
      }
    } catch (error) {
      this.errors.push(
        `Error fetching all slides: ${(error as Error).message}`
      );
    }
  }

  /**
   * Converts the slides list to an array, maintaining the order based on the linked list structure.
   * @returns A read-only array of slides.
   */
  convertToArray(): ReadonlyArray<Slide> {
    const result: Slide[] = [];
    let currentId = this.headID;
    while (currentId) {
      const slide = this.slides[currentId];
      if (!slide) {
        break;
      }
      if (!slide.hidden) {
        result.push(slide);
      }
      currentId = slide.next!;
    }

    return Object.freeze(result);
  }

  /**
   * Fetches a specific slide by its ID.
   * @param slideID The ID of the slide to fetch.
   * @returns A promise that resolves to an array of slides.
   */
  async fetchSlide(slideID: string): Promise<Slide[]> {
    try {
      let fetchedSlides: Slide | Slide[];
      let oldNextSlideId = this.slides[slideID].next;

      fetchedSlides = await getSlidesAction(this.presentationID, slideID);

      if (!fetchedSlides) {
        this.errors.push(`Error: Slide with ID ${slideID} not found`);
        return [];
      }

      if (!Array.isArray(fetchedSlides)) {
        fetchedSlides = [fetchedSlides];
      }

      fetchedSlides.forEach((data: Slide) => {
        if (!this.slides[data.id]) {
          this.length++;
        }
        this.slides[data.id] = data;
      });

      if (oldNextSlideId) {
        this.slides[oldNextSlideId].previous = fetchedSlides[0].id;
      }
      return fetchedSlides;
    } catch (error) {
      this.errors.push(
        `Error fetching slide with ID ${slideID}: ${(error as Error).message}`
      );
      return [];
    }
  }

  /**
   * Updates the given slides.
   * @param slides The slides to update.
   * @param waitForDB Whether to wait for the database operation to complete.
   */
  async updateSlides(
    slides:
      | (Partial<Slide> & { id: string })
      | (Partial<Slide> & { id: string }[]),
    waitForDB = false
  ) {
    this.saving = true;
    try {
      if (!Array.isArray(slides)) {
        if (!slides.id) {
          throw new Error("Slide id is required");
        }
        const slideId = slides.id;

        if (!this.slides[slideId]) {
          throw new Error(`Slide with id ${slideId} does not exist`);
        }

        const existingSlide = this.slides[slideId];
        Object.assign(existingSlide, slides);
      } else {
        slides.forEach((slide, index) => {
          if (!slide.id) {
            throw new Error(`Slide id is required for slide at index ${index}`);
          }
          const slideId = slide.id;

          if (!this.slides[slideId]) {
            throw new Error(
              `Slide with id ${slideId} does not exist (index ${index})`
            );
          }

          const existingSlide = this.slides[slideId];
          Object.assign(existingSlide, slide);
        });
      }

      if (waitForDB) {
        await updateSlidesAction(this.presentationID, slides);
        this.saving = false;
      } else {
        updateSlidesAction(this.presentationID, slides)
          .catch((error) => {
            this.errors.push(
              `Error updating slides: ${(error as Error).message}`
            );
          })
          .finally(() => {
            this.saving = false;
          });
      }
    } catch (error) {
      this.errors.push(`Error updating slides: ${(error as Error).message}`);
    }
  }

  /**
   * Adds a new slide after the specified previous slide.
   * @param previousSlideId The ID of the slide after which to add the new slide.
   * @param newSlide The new slide to add.
   * @param waitForDB Whether to wait for the database operation to complete.
   */
  async addSlide(previousSlideId: string, newSlide: Slide, waitForDB = false) {
    this.saving = true;
    try {
      const previousSlide = this.slides[previousSlideId];
      const nextSlideId = previousSlide.next;
      const newSlideId = newSlide.id;

      this.slides[newSlideId] = newSlide;
      this.length++;

      previousSlide.next = newSlideId;
      if (nextSlideId) {
        this.slides[nextSlideId].previous = newSlideId;
      }

      const slidesToUpdate: Partial<Slide>[] = [
        { id: previousSlide.id, next: newSlideId },
        { previous: previousSlide.id, next: nextSlideId, ...newSlide },
      ];
      if (nextSlideId) {
        slidesToUpdate.push({ id: nextSlideId, previous: newSlideId });
      }

      if (waitForDB) {
        await updateSlidesAction(this.presentationID, slidesToUpdate);
        this.saving = false;
      } else {
        updateSlidesAction(this.presentationID, slidesToUpdate)
          .catch((error) => {
            this.errors.push(
              `Error adding slide after ${previousSlideId}: ${
                (error as Error).message
              }`
            );
          })
          .finally(() => {
            this.saving = false;
          });
      }
    } catch (error) {
      this.errors.push(
        `Error adding slide after ${previousSlideId}: ${
          (error as Error).message
        }`
      );
    }
  }

  /**
   * Retrieves a specific slide by its ID.
   * @param slideID The ID of the slide to retrieve.
   * @returns The requested slide.
   */
  getSlide(slideID: string): Readonly<Slide> {
    try {
      if (!this.slides[slideID]) {
        throw new Error(`Slide with id ${slideID} does not exist`);
      }
      return Object.freeze({ ...this.slides[slideID] });
    } catch (error) {
      this.errors.push(
        `Error getting slide with ID ${slideID}: ${(error as Error).message}`
      );
      return null as any;
    }
  }

  /**
   * Hides a specific slide by setting its hidden property to true.
   * @param slideID The ID of the slide to hide.
   * @param waitForDB Whether to wait for the database operation to complete.
   */
  async hideSlide(slideID: string, waitForDB = false) {
    this.saving = true;
    try {
      const slideToHide = this.slides[slideID];

      if (!slideToHide) {
        throw new Error(`Slide with id ${slideID} does not exist`);
      }

      // Set the slide's hidden property to true
      slideToHide.hidden = true;

      // Update pointers
      const previousSlideId = slideToHide.previous;
      const nextSlideId = slideToHide.next;

      if (previousSlideId) {
        this.slides[previousSlideId].next = nextSlideId;
      }

      if (nextSlideId) {
        this.slides[nextSlideId].previous = previousSlideId;
      }

      const slidesToUpdate: Partial<Slide>[] = [{ id: slideID, hidden: true }];

      if (previousSlideId) {
        slidesToUpdate.push({ id: previousSlideId, next: nextSlideId });
      }

      if (nextSlideId) {
        slidesToUpdate.push({ id: nextSlideId, previous: previousSlideId });
      }

      if (waitForDB) {
        await updateSlidesAction(this.presentationID, slidesToUpdate);
        this.saving = false;
      } else {
        updateSlidesAction(this.presentationID, slidesToUpdate)
          .catch((error) => {
            this.errors.push(
              `Error hiding slide with ID ${slideID}: ${
                (error as Error).message
              }`
            );
          })
          .finally(() => {
            this.saving = false;
          });
      }
    } catch (error) {
      this.errors.push(
        `Error hiding slide with ID ${slideID}: ${(error as Error).message}`
      );
      this.saving = false;
    }
  }

  /**
   * Retrieves the head slide ID.
   * @returns The head slide ID.
   */
  getHeadSlideID(): string {
    return this.headID;
  }

  /**
   * Retrieves the list of errors encountered.
   * @returns An array of error messages.
   */
  getErrors(): string[] {
    return this.errors;
  }

  /**
   * Retrieves the saving status.
   * @returns The saving status.
   */
  getSaving(): boolean {
    return this.saving;
  }
}


//   async reorderSlides(
//     presentationId: string,
//     slideIds: string[],
//     beforeSlideId: string
//   ) {
//     /**
//      * Moves the slides with the given slide_ids to be placed before the slide with before_slide_id.
//      */
//     const beforeSlide = this.slides[beforeSlideId];
//     let afterSlideId = beforeSlide.previous;

//     // Disconnect the slides to be moved from their current positions
//     for (const slideId of slideIds) {
//       const currentSlide = this.slides[slideId];
//       if (currentSlide.previous) {
//         this.slides[currentSlide.previous].next = currentSlide.next;
//         await updateSlides(presentationId, [
//           { id: currentSlide.previous, next: currentSlide.next },
//         ]);
//       }
//       if (currentSlide.next) {
//         this.slides[currentSlide.next].previous = currentSlide.previous;
//         await updateSlides(presentationId, [
//           { id: currentSlide.next, previous: currentSlide.previous },
//         ]);
//       }
//     }

//     // Connect the slides to be moved into their new positions
//     const slidesToUpdate: Partial<Slide>[] = [];
//     for (const slideId of slideIds) {
//       const currentSlide = this.slides[slideId];
//       currentSlide.previous = afterSlideId;
//       if (afterSlideId) {
//         this.slides[afterSlideId].next = slideId;
//         slidesToUpdate.push({ id: afterSlideId, next: slideId });
//       }
//       afterSlideId = slideId;
//     }

//     beforeSlide.previous = slideIds[slideIds.length - 1];
//     slidesToUpdate.push({
//       id: beforeSlide.id,
//       previous: slideIds[slideIds.length - 1],
//     });
//     this.slides[slideIds[slideIds.length - 1]].next = beforeSlideId;
//     slidesToUpdate.push({
//       id: slideIds[slideIds.length - 1],
//       next: beforeSlideId,
//     });

//     await updateSlides(presentationId, slidesToUpdate);
//   }
// }

// // Example usage
// (async () => {
//     const presentationId = "presentation123";
//     const persistentSlideList = new PersistentSlideList("slide1");

//     // Fetch all slides and store them in the linked list
//     await persistentSlideList.fetchAllSlides(presentationId);
//     const slidesArray = persistentSlideList.convertToArray();
//     console.log("Slides in order:", slidesArray);

//     // Fetch specific slides and update them in the linked list
//     await persistentSlideList.fetchAndUpdateSlides(presentationId, ["slide2", "slide3"]);

//     // Update a single slide
//     await persistentSlideList.updateSlide(presentationId, "slide2", { slide_title: "Updated Title" });

//     // Add a new slide after a specific slide
//     await persistentSlideList.addSlide(presentationId, "slide2", "slide_new", { slide_title: "New Slide" });

//     // Reorder slides
//     await persistentSlideList.reorderSlides(presentationId, ["slide3", "slide_new"], "slide4");
// })();
