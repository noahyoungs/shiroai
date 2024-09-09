import { Slide } from "./database-types";
import {
  getHeadSlideID as getHeadSlideIDAction,
  getSlides as getSlidesAction,
  updateSlides as updateSlidesAction,
  getAllSlides as getAllSlidesAction,
  addProseClassesAndSplitOverheight,
} from "@/actions/slides-actions";

export class PersistentSlideList {
  private presentationID: string;
  private headID: string;
  private slides: { [key: string]: Slide };
  private updatePushingSlideStatus: (slide_id: string, status: string) => void;
  private updateErrors: (slide_id: string, error: string) => void;
  private sendInterfaceUpdate: (slideIDs: string | string[]) => void;
  length: number;

  constructor(
    presentationID: string,
    updatePushingSlideStatus: (id: string, status: string) => void,
    updateErrors: (id: string, error: string) => void,
    sendInterfaceUpdate: (slideIDs: string | string[]) => void
  ) {
    this.presentationID = presentationID;
    this.headID = "";
    this.slides = {};
    this.length = 0;
    this.updatePushingSlideStatus = updatePushingSlideStatus;
    this.updateErrors = updateErrors;
    this.sendInterfaceUpdate = sendInterfaceUpdate;
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

      const slides = await getAllSlidesAction(this.presentationID);
      if (slides) {
        // Add slides to the local list
        slides.forEach((data: Slide) => {
          this.slides[data.slide_id] = data;
          this.length++;
        });
      }

    } catch (error) {
      this.updateErrors(
        "allSlides",
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
   * Fetches one or more slides by their IDs.
   * @param slideIDs - Either a single slide ID or an array of slide IDs to fetch.
   * @returns A promise that resolves to an array of slides.
   */
  async fetchSlides(slideIDs: string | string[]): Promise<Slide[]> {
    if (typeof slideIDs !== "string" && !Array.isArray(slideIDs)) {
      throw new Error("slideIDs must be a string or an array of strings");
    }

    try {
      let fetchedSlides: Slide | Slide[];
      fetchedSlides = await getSlidesAction(this.presentationID, slideIDs);

      if (!fetchedSlides) {
        throw new Error("No slides found");
      }

      if (!Array.isArray(fetchedSlides)) {
        fetchedSlides = [fetchedSlides];
      }

      // set slides in local list
      fetchedSlides.forEach((data: Slide) => {
        if (!this.slides[data.slide_id]) {
          this.length++;
        }
        this.slides[data.slide_id] = data;
      });

      return fetchedSlides;
    } catch (error) {
      if (Array.isArray(slideIDs)) {
        slideIDs.forEach((id) => {
          this.updateErrors(
            id,
            `Error fetching slide with ID ${id}: ${(error as Error).message}`
          );
        });
      } else {
        this.updateErrors(
          slideIDs,
          `Error fetching slide with ID ${slideIDs}: ${
            (error as Error).message
          }`
        );
      }
      return [];
    }
  }

  /**
   * Updates the given slides.
   * @param slides The slides to update. Either a slide or an array of slides.
   * @param waitForDB Whether to wait for the database operation to complete.
   * @param splitSlides Whether to update the prose class split the slides if they are overheight. If true, slides needs to be the entire slide, not just the properties to update. Default is false.
   */
  async updateSlides(
    slides: Partial<Slide> | Partial<Slide>[],
    waitForDB = false,
    splitSlides = false
  ) {
    try {
      // Convert to array if not already
      if (!Array.isArray(slides)) {
        slides = [slides];
      }

      slides.forEach((slide: Partial<Slide>) => {
        if (!slide.slide_id) {
          throw new Error("Slide id is required");
        }
        this.updatePushingSlideStatus(slide.slide_id!, "updating_prose_class");
      });

      // Update prose class and split slides regardless of whether prose class is present
      if (splitSlides) {
        console.log("Slides before split", slides);
        let splitSlides: Slide[] = (
          await Promise.all(
            slides.map(async (slide: Slide) => {
              console.log("slide before split", slide.slide_id);
              let processedSlides = await addProseClassesAndSplitOverheight(
                slide,
                false
              );
              // will result in Slide[], containing one or more slides

              if (processedSlides.length > 1) {
                // Update the prev and next of the slides
                for (let i = 0; i < processedSlides.length; i++) {
                  const currentSlide = processedSlides[i];
                  const prevSlide = processedSlides[i - 1];
                  const nextSlide = processedSlides[i + 1];

                  currentSlide.previous = prevSlide?.slide_id || slide.previous; // if prevSlide is undefined, use original previous
                  console.log(
                    `i: ${i}, nextSlide: ${nextSlide?.slide_id} slide.next: ${slide.next}`
                  );
                  currentSlide.next = nextSlide?.slide_id || slide.next; // if nextSlide is undefined, use original next
                }
              }

              return processedSlides; // This returns Slide[], so the map function returns Slide[][]
            })
          )
        ).flat(); // Flatten Slide[][] to Slide[]

        // Add a slide containing the next id of the last slide with a previous pointer to the last slide
        let nextSlide = {
          id: splitSlides[splitSlides.length - 1].next,
          previous: splitSlides[splitSlides.length - 1].slide_id,
        };

        let splitSlidesWithNext: Partial<Slide>[] = [
          ...splitSlides,
          nextSlide as Partial<Slide>,
        ];

        console.log("Slides after split", splitSlidesWithNext);

        slides = splitSlidesWithNext;
      }

      slides.forEach((slide: Partial<Slide>) => {
        this.updatePushingSlideStatus(slide.slide_id!, "uploading");
      });

      // Update the slides in the local list
      slides.forEach((slide: Partial<Slide>, index: number) => {
        if (!slide.slide_id) {
          console.log("split slides with next", slides);
          throw new Error(`Slide id is required for slide at index ${index}`);
        }
        const slideId = slide.slide_id;

        if (this.slides[slideId]) {
          const existingSlide = this.slides[slideId];
          Object.assign(existingSlide, slide);
        } else {
          // New slides added from splitting
          //@ts-ignore
          this.slides[slideId] = slide;
        }
      });

      // Update the slides in the database
      if (waitForDB) {
        // Array of slides
        slides.forEach((slide: Partial<Slide>) => {
          this.updatePushingSlideStatus(slide.slide_id!, "uploading");
        });
        await updateSlidesAction(this.presentationID, slides);
        slides.forEach((slide: Partial<Slide>) => {
          this.updatePushingSlideStatus(slide.slide_id!, "uploaded");
        });
        this.sendInterfaceUpdate(
          slides.map((slide: Partial<Slide>) => slide.slide_id)
        );
      } else {
        slides.forEach((slide: Partial<Slide>) => {
          this.updatePushingSlideStatus(slide.slide_id!, "uploading");
        });

        updateSlidesAction(this.presentationID, slides)
          .catch((error) => {
            slides.forEach((slide: Partial<Slide>) => {
              this.updatePushingSlideStatus(slide.slide_id!, "errored");
              this.updateErrors(
                slide.slide_id!,
                `Error updating slide: ${(error as Error).message}`
              );
            });
          })
          .then(() => {
            slides.forEach((slide: Partial<Slide>) => {
              this.updatePushingSlideStatus(slide.slide_id!, "uploaded");
            });
            this.sendInterfaceUpdate(
              slides.map((slide: Partial<Slide>) => slide.slide_id)
            );
          });
      }
    } catch (error) {
      slides.forEach((slide: Partial<Slide>) => {
        this.updatePushingSlideStatus(slide.slide_id!, "errored");
        this.updateErrors(
          slide.slide_id!,
          `Error updating slide: ${(error as Error).message}`
        );
      });
    }
  }

  /**
   * Adds a new slide after the specified previous slide.
   * @param previousSlideId The ID of the slide after which to add the new slide.
   * @param newSlide The new slide to add.
   * @param waitForDB Whether to wait for the database operation to complete.
   */
  async addSlide(previousSlideId: string, newSlide: Slide, waitForDB = false) {
    try {
      const previousSlide = this.slides[previousSlideId];
      const nextSlideId = previousSlide.next;
      const newSlideId = newSlide.slide_id;

      this.slides[newSlideId] = newSlide;
      this.length++;

      previousSlide.next = newSlideId;
      if (nextSlideId) {
        this.slides[nextSlideId].previous = newSlideId;
      }

      const slidesToUpdate: Partial<Slide>[] = [
        { slide_id: previousSlide.slide_id, next: newSlideId },
        { previous: previousSlide.slide_id, next: nextSlideId, ...newSlide },
      ];
      if (nextSlideId) {
        slidesToUpdate.push({ slide_id: nextSlideId, previous: newSlideId });
      }

      if (waitForDB) {
        this.updatePushingSlideStatus(newSlide.slide_id, "uploading");
        await updateSlidesAction(this.presentationID, slidesToUpdate);
        this.updatePushingSlideStatus(newSlide.slide_id, "uploaded");
        this.sendInterfaceUpdate(newSlide.slide_id);
      } else {
        this.updatePushingSlideStatus(newSlide.slide_id, "uploading");
        updateSlidesAction(this.presentationID, slidesToUpdate)
          .catch((error) => {
            this.updateErrors(
              newSlide.slide_id,
              `Error adding slide after ${previousSlideId}: ${
                (error as Error).message
              }`
            );
            this.updatePushingSlideStatus(newSlide.slide_id, "errored");
          })
          .then(() => {
            this.updatePushingSlideStatus(newSlide.slide_id, "uploaded");
            this.sendInterfaceUpdate(newSlide.slide_id);
          });
      }
    } catch (error) {
      this.updateErrors(
        newSlide.slide_id,
        `Error adding slide after ${previousSlideId}: ${
          (error as Error).message
        }`
      );
      this.updatePushingSlideStatus(newSlide.slide_id, "errored");
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
      this.updateErrors(
        "getSlide",
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
    try {
      if (!this.slides[slideID]) {
        throw new Error(`Slide with id ${slideID} does not exist`);
      }

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

      const slidesToUpdate: Partial<Slide>[] = [{ slide_id: slideID, hidden: true }];

      if (previousSlideId) {
        slidesToUpdate.push({ slide_id: previousSlideId, next: nextSlideId });
      }

      if (nextSlideId) {
        slidesToUpdate.push({ slide_id: nextSlideId, previous: previousSlideId });
      }

      if (waitForDB) {
        this.updatePushingSlideStatus(slideID, "uploading");
        await updateSlidesAction(this.presentationID, slidesToUpdate);
        this.updatePushingSlideStatus(slideID, "uploaded");
        this.sendInterfaceUpdate(slideID);
      } else {
        this.updatePushingSlideStatus(slideID, "uploading");
        updateSlidesAction(this.presentationID, slidesToUpdate)
          .catch((error) => {
            slidesToUpdate.forEach((slide) => {
              this.updateErrors(
                slide.slide_id!,
                `Error hiding slide: ${(error as Error).message}`
              );
              this.updatePushingSlideStatus(slide.slide_id!, "errored");
            });
          })
          .then(() => {
            this.updatePushingSlideStatus(slideID, "uploaded");
            this.sendInterfaceUpdate(slideID);
          });
      }
    } catch (error) {
      this.updateErrors(
        slideID,
        `Error hiding slide with ID ${slideID}: ${(error as Error).message}`
      );
      this.updatePushingSlideStatus(slideID, "errored");
    }
  }

  /**
   * Retrieves the head slide ID.
   * @returns The head slide ID.
   */
  getHeadSlideID(): string {
    return this.headID;
  }
}
