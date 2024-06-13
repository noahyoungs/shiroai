"use server";
import {
  getSources as dynamodbGetSources,
  getPresentationByID,
  getSlide as dynamodbGetSlide,
  getSlides as dynamodbGetSlides,
  batchUpdateSlides,
  updateSlide as dynamodbUpdateSlide,
  deleteSlide as dynamodbDeleteSlide,
  addSlideAfterOrder as dynamodbAddSlideAfterOrder,
  getNextSlideOrder as dynamodbGetNextSlideOrder,
} from "@/utils/dynamodb";
import { getServerSession } from "next-auth";
import { hashEmail } from "@/utils/hash-email";
import { Slide } from "@/utils/slide-types";
import { getProseClass } from "@/actions/get-prose-class";
import { cleanMarkdown } from "@/actions/clean-editor-md";
import { splitMarkdown } from "@/actions/split-markdown";
import { uuidv7 } from "uuidv7";


async function _addProseClassesAndSplitOverheight(slide: Slide, checkProseClass: boolean = true, recursionLimit: number = 5): Promise<Slide[]> {
  if (slide.slide_type === "markdown_slide" && (!slide.slide_content?.prose_class || !checkProseClass)) {
    // console.log("Processing markdown slide:", slide.id);

    const processSlide = async (slideContent: string, slideTitle: string, slideId: string, isContinuation: boolean = false, depth: number = 0): Promise<Slide[]> => {
      if (depth > recursionLimit) {
        console.log(`Recursion limit reached for slide ${slideTitle}`);
        return [
          {
            ...slide,
            id: slideId,
            slide_content: {
              ...slide.slide_content,
              content: slideContent,
              prose_class: "prose-sm",
            },
            // regex replaces any number of (Cont.) at the end of the title
            slide_title: isContinuation ? `${slideTitle.replace(/(\s\(Cont\.\))+$/g, '')} (Cont.)` : slideTitle,
          },
        ];
      }

      const proseClass = await getProseClass(slideContent);
      // console.log("Prose class:", proseClass);

      if (proseClass === "overheight") {
        console.log(`Splitting overheight slide ${slideTitle}`);

        const [slide1Content, slide2Content] = splitMarkdown(slideContent);
        console.log(`Split First half: ${slide1Content}`);
        console.log(`Split Second half: ${slide2Content}`);
        const slide1Title = isContinuation ? slideTitle : slideTitle.replace(/ \(Cont\.\)$/, '');
        const slide2Title = `${slide1Title} (Cont.)`;

        const slide1Prose = await processSlide(slide1Content, slide1Title, slideId, isContinuation, depth + 1);
        const slide2Prose = await processSlide(slide2Content, slide2Title, uuidv7(), true, depth + 1);

        return [...slide1Prose, ...slide2Prose];
      } else {
        return [
          {
            ...slide,
            id: slideId,
            slide_content: {
              ...slide.slide_content,
              content: slideContent,
              prose_class: proseClass || "prose-sm",
            },
            slide_title: isContinuation ? `${slideTitle.replace(/(\s\(Cont\.\))+$/g, '')} (Cont.)` : slideTitle,
          },
        ];
      }
    };

    return processSlide(slide.slide_content.content, slide.slide_title, slide.id);
  }

  return [slide];
}


/**
 * Authenticates the user based on the presentation ID.
 * @param presentationID - The ID of the presentation.
 * @returns A promise that resolves to true if the user is authenticated, or throws an error if the user is unauthorized.
 */
async function authenticateUser(presentationID: string) {
  const session = await getServerSession();

  if (!session || !session.user) {
    throw new Error("Unauthorized.");
  }

  const presentation = await getPresentationByID(presentationID, ["user"]);

  if (presentation.user !== hashEmail(session.user.email)) {
    throw new Error("Unauthorized.");
  }

  return true;
}

async function sortSlides(slides: Slide[]) {
  return slides.sort((a, b) => a.slide_order - b.slide_order);
}

/**
 * Retrieves the sources for a presentation.
 * @param presentationID - The ID of the presentation.
 * @returns A promise that resolves to an array of sources, or throws an error if the sources cannot be retrieved.
 */
export async function getSources(presentationID: string) {
  await authenticateUser(presentationID);

  try {
    const sources = await dynamodbGetSources(presentationID);
    return sources;
  } catch (error) {
    console.error("Error retrieving sources:", error);
    throw new Error("Failed to retrieve sources");
  }
}


/**
 * Retrieves the slides for a given presentation ID. Also processes the markdown slides to determine the prose class and splits it if overheight.
 * 
 * @param presentationID - The ID of the presentation.
 * @returns A sorted array of slides.
 * @throws Error if there is a failure in retrieving the slides.
 */
export async function getSlides(presentationID: string) {
  await authenticateUser(presentationID);

  let slides: Slide[];

  try {
    slides = await dynamodbGetSlides(presentationID);
  } catch (error) {
    console.error("Error retrieving slides:", error);
    throw new Error("Failed to retrieve slides");
  }

  slides = await sortSlides(slides);

  if (slides.length === 0) {
    return slides;
  }

  let updatedSlides = (await Promise.all(
    slides.flatMap((slide) => _addProseClassesAndSplitOverheight(slide, true))
  )).flat();

  // reset slide order
  updatedSlides = updatedSlides.map((slide, index) => ({
    ...slide,
    slide_order: (index + 1) * 1000,
  }));

  // Optimize updatedSlides by only including fields that are different
  const optimizedUpdatedSlides = updatedSlides.map((updatedSlide, index): Partial<Slide> => {
    const matchingSlide = slides.find((slide) => slide.id === updatedSlide.id);
    const updatedFields: Partial<Slide> = {
      id: updatedSlide.id,
      slide_order: updatedSlide.slide_order,
    };
  
    if (matchingSlide) {
      for (const key in updatedSlide) {
        if (updatedSlide[key] !== matchingSlide[key]) {
          updatedFields[key] = updatedSlide[key];
        }
      }
    } else {
      for (const key in updatedSlide) {
        updatedFields[key] = updatedSlide[key];
      }
    }

    return updatedFields;
  });
  // console.log("Optimized Updated Slides:", optimizedUpdatedSlides);

  batchUpdateSlides(presentationID, optimizedUpdatedSlides);
  return sortSlides(updatedSlides);
}

/**
 * Retrieves a specific slide from a presentation.
 * @param presentationID - The ID of the presentation.
 * @param slideID - The ID of the slide.
 * @returns A promise that resolves to the requested slide, or throws an error if the slide cannot be retrieved.
 */
export async function getSlide(presentationID: string, slideID: string) {
  await authenticateUser(presentationID);

  let slide;

  try {
    slide = await dynamodbGetSlide(presentationID, slideID);
  } catch (error) {
    console.error("Error retrieving slide:", error);
    throw new Error("Failed to retrieve slide");
  }

  if (!slide) {
    throw new Error("Slide not found");
  }

  const originalOrder = slide.slide_order;
  console.log("Original Order:", originalOrder);
  let processedSlides = await _addProseClassesAndSplitOverheight(slide, false);
  console.log(`Got ${processedSlides.length} processed slides`);

  if (processedSlides.length === 1) {
    // Update the single slide with the prose_class
    const { id, slide_content } = processedSlides[0];
    await dynamodbUpdateSlide(presentationID, id, { slide_content });
  } else if (processedSlides.length > 1) {
    // Get the next slide's order
    const nextSlideOrder = await dynamodbGetNextSlideOrder(presentationID, originalOrder);
    console.log("Next Slide Order:", nextSlideOrder);
    if (!nextSlideOrder) {
      throw new Error("Failed to get next slide order");
    }

    // Assign new slide_order to every slide in processedSlides
    processedSlides = processedSlides.map((slide, index) => {
      const newOrder = Math.round(originalOrder + ((nextSlideOrder - originalOrder) * index) / (processedSlides.length));
      return {
        ...slide,
        slide_order: newOrder,
      };
    });

    // Update the slides with the new orders
    await batchUpdateSlides(presentationID, processedSlides);
  }

  return processedSlides;
}


/**
 * Updates the slides in a presentation.
 * @param presentationID - The ID of the presentation.
 * @param slides - An array of partial slides to update, each must contain an ID. Only the fields that need to be updated should be included.
 * @returns A promise that resolves when the slides are successfully updated, or throws an error if the slides cannot be updated.
 */
export async function updateSlides(
  presentationID: string,
  slides: Partial<Slide>[]
) {
  await authenticateUser(presentationID);

  try {
    await batchUpdateSlides(presentationID, slides);
  } catch (error) {
    console.error("Error updating slides:", error);
    throw new Error("Failed to update slides");
  }
}

async function _updateSlide(
  presentationID: string,
  slide: Partial<Slide>
) {
  try {
    const { id, ...slideWithoutId } = slide;
    if (!id) {
      throw new Error("Slide ID is required");
    }
    await dynamodbUpdateSlide(presentationID, id, slideWithoutId);
  } catch (error) {
    console.error("Error updating slide:", error);
    throw new Error("Failed to update slide");
  }
}

/**
 * Updates a specific slide in a presentation.
 * @param presentationID - The ID of the presentation.
 * @param slide - The partial slide to update, must contain an id. Only the fields that need to be updated should be included.
 * @returns A promise that resolves when the slide is successfully updated, or throws an error if the slide cannot be updated.
 */
export async function updateSlide(
  presentationID: string,
  slide: Partial<Slide>
) {
  await authenticateUser(presentationID);
  // if the type is markdown_slide clean the markdown
  if (slide.slide_type === "markdown_slide" && slide.slide_content?.content) {
    slide.slide_content.content = cleanMarkdown(
      slide.slide_content.content
    );
  }

  await _updateSlide(presentationID, slide);
}

async function _addSlideAfter(presentationID: string, slide: Slide) {
  // get order from the slide
  const { slide_order, ...slideWithoutOrder } = slide;
  try {
    await dynamodbAddSlideAfterOrder(
      presentationID,
      slide_order,
      slideWithoutOrder
    );
  } catch (error) {
    console.error("Error adding slide:", error);
    throw new Error("Failed to add slide");
  }
}

/**
 * Adds a new slide to a presentation after a specified slide.
 * @param presentationID - The ID of the presentation.
 * @param slide - The slide to add. The slide must have an order.
 * @returns A promise that resolves when the slide is successfully added, or throws an error if the slide cannot be added.
 */
export async function addSlideAfter(presentationID: string, slide: Slide) {
  await authenticateUser(presentationID);
  await _addSlideAfter(presentationID, slide);
}
