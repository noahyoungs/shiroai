"use server";
import {
  getSources as dynamodbGetSources,
  getPresentationByID,
  updateSlides as dynamodbUpdateSlides,
  getSlides as dynamodbGetSlides,
  getAllSlides as dynamodbGetAllSlides,
} from "@/utils/dynamodb";
import { getServerSession } from "next-auth";
import { hashEmail } from "@/utils/hash-email";
import { Slide } from "@/utils/slide-types";
import { getProseClass } from "@/actions/get-prose-class";
import { cleanMarkdown } from "@/actions/clean-editor-md";
import { splitMarkdown } from "@/actions/split-markdown";
import { uuidv7 } from "uuidv7";

/**
 * Adds prose classes and splits overheight slides.
 *
 * @param slide - The slide to process.
 * @param checkProseClass - Optional. Specifies whether to skip processing if slide.slide_content.prose_class is true. Default is true.
 * @param recursionLimit - Optional. Specifies the recursion limit. Default is 5. (Maximum number of splits for one original slide)
 * @returns A promise that resolves to an array of slides. If the slide is not a markdown slide or already has a prose class, the original slide is returned as a single-element array.
 */
export async function addProseClassesAndSplitOverheight(
  slide: Slide,
  checkProseClass: boolean = true,
  recursionLimit: number = 5
): Promise<Slide[]> {
  // console.log("Adding prose class for slide:", slide.id);
  if (
    slide.slide_type === "markdown_slide" &&
    (!slide.slide_content?.prose_class || !checkProseClass)
  ) {
    console.log("Processing markdown slide:", slide.id);

    const processSlide = async (
      slideContent: string,
      slideTitle: string,
      slideId: string,
      isContinuation: boolean = false,
      depth: number = 0
    ): Promise<Slide[]> => {
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
            slide_title: isContinuation
              ? `${slideTitle.replace(/(\s\(Cont\.\))+$/g, "")} (Cont.)`
              : slideTitle,
          },
        ];
      }

      let proseClass;

      try {
        proseClass = await getProseClass(slideContent, slideTitle);
      } catch (error) {
        throw new Error(
          `Error getting prose class for slide ${slideId}: ${error}`
        );
      }

      console.log("Prose class:", proseClass);

      if (proseClass === "overheight") {
        console.log(`Splitting overheight slide ${slideTitle}`);

        const [slide1Content, slide2Content] = splitMarkdown(slideContent);
        console.log(`Split First half: ${slide1Content}`);
        console.log(`Split Second half: ${slide2Content}`);
        const slide1Title = isContinuation
          ? slideTitle
          : slideTitle.replace(/ \(Cont\.\)$/, "");
        const slide2Title = `${slide1Title} (Cont.)`;

        const slide1Prose = await processSlide(
          slide1Content,
          slide1Title,
          slideId,
          isContinuation,
          depth + 1
        );
        const slide2Prose = await processSlide(
          slide2Content,
          slide2Title,
          uuidv7(),
          true,
          depth + 1
        );

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
            slide_title: isContinuation
              ? `${slideTitle.replace(/(\s\(Cont\.\))+$/g, "")} (Cont.)`
              : slideTitle,
          },
        ];
      }
    };

    return processSlide(
      slide.slide_content.content,
      slide.slide_title,
      slide.id
    );
  } else {
    console.log(
      // `Not processing this slide: ${slide.id}, slide type: ${slide.slide_type} prose class: ${slide.slide_content?.prose_class}, checkProseClass: ${checkProseClass}`
    );
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

/**
 * Retrieves the sources for a presentation.
 * @param presentationID - The ID of the presentation.
 * @returns A promise that resolves to an array of sources, or throws an error if the sources cannot be retrieved.
 */
export async function getSources(presentationID: string) {
  let auth = await authenticateUser(presentationID);

  if (!auth) {
    throw new Error("Unauthorized.");
  }

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
 * @returns An array of slides.
 * @throws Error if there is a failure in retrieving the slides.
 */
export async function getAllSlides(presentationID: string) {
  let auth = await authenticateUser(presentationID);

  if (!auth) {
    throw new Error("Unauthorized.");
  }

  let slides: Slide[];

  try {
    slides = await dynamodbGetAllSlides(presentationID);
  } catch (error) {
    console.error("Error retrieving slides:", error);
    throw new Error("Failed to retrieve slides");
  }
  return slides
}

/**
 * Retrieves a specific slide from a presentation.
 * @param presentationID - The ID of the presentation.
 * @param slideIDs - Either a single slide ID or an array of slide IDs.
 * @returns A promise that resolves to the requested slide, or throws an error if the slide cannot be retrieved.
 */
export async function getSlides(
  presentationID: string,
  slideIDs: string | string[]
): Promise<Slide | Slide[]> {
  let auth = await authenticateUser(presentationID);

  if (!auth) {
    throw new Error("Unauthorized.");
  }

  let slides: Slide | Slide[] | null;

  try {
    // slides = await dynamodbGetSlides(presentationID, slideIDs);
    // Looks redundant but this is to fix the type error
    if (typeof slideIDs === "string") {
      // Single slideID case
      slides = await dynamodbGetSlides(presentationID, slideIDs);
    } else if (Array.isArray(slideIDs)) {
      // Multiple slideIDs case
      slides = await dynamodbGetSlides(presentationID, slideIDs);
    } else {
      throw new Error("Invalid slideIDs type.");
    }
  } catch (error) {
    console.error("Error retrieving slide:", error);
    throw new Error("Failed to retrieve slide");
  }

  if (!slides || slides.length === 0) {
    throw new Error("Slide not found");
  }

  // Make sure slides is an array
  if (!Array.isArray(slides)) {
    slides = [slides];
  }

  let updatedSlides: Slide[] = (
    await Promise.all(
      slides.map(async (slide) => {
        let processedSlides = await addProseClassesAndSplitOverheight(
          slide,
          true
        );
        // will result in Slide[], containing one or more slides

        if (processedSlides.length > 1) {
          // Update the prev and next of the slides
          for (let i = 0; i < processedSlides.length; i++) {
            const currentSlide = processedSlides[i];
            const prevSlide = processedSlides[i - 1];
            const nextSlide = processedSlides[i + 1];

            currentSlide.previous = prevSlide?.id || slide.previous; // if prevSlide is undefined, use original previous
            currentSlide.next = nextSlide?.id || slide.next; // if nextSlide is undefined, use original next
          }
        }

        return processedSlides; // This returns Slide[], so the map function returns Slide[][]
      })
    )
  ).flat(); // Flatten Slide[][] to Slide[]

  // Add a slide to the end of the array to set the previous pointer of the slide after the last slide
  let nextSlide = {
    id: updatedSlides[updatedSlides.length - 1].next,
    previous: updatedSlides[updatedSlides.length - 1].id,
  };

  let updatedSlidesWithNext: Partial<Slide>[] = [
    ...updatedSlides,
    nextSlide as Partial<Slide>,
  ];

  // TODO: Fix the previous pointers of the slides not being updated

  // Optimize updatedSlides by only including fields that are different
  const optimizedUpdatedSlides = updatedSlidesWithNext.map(
    (updatedSlide, index): Partial<Slide> => {
      const matchingSlide = slides!.find(
        (slide: Slide) => slide.id === updatedSlide.id
      );
      const updatedFields: Partial<Slide> = {
        id: updatedSlide.id,
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
    }
  );

  // fire and forget
  await dynamodbUpdateSlides(presentationID, optimizedUpdatedSlides);
  return updatedSlides;
}

/**
 * Updates the slides in a presentation.
 * @param presentationID - The ID of the presentation.
 * @param slides - Either a single slide or an array of slides to update.
 * @returns A promise that resolves when the slides are successfully updated, or throws an error if the slides cannot be updated.
 */
export async function updateSlides(
  presentationID: string,
  slides: Partial<Slide> | Partial<Slide>[]
) {
  let auth = await authenticateUser(presentationID);

  if (!auth) {
    throw new Error("Unauthorized.");
  }

  let success = await dynamodbUpdateSlides(presentationID, slides);

  return success;
}

export async function getHeadSlideID(presentationID: string) {
  let auth = await authenticateUser(presentationID);

  if (!auth) {
    throw new Error("Unauthorized.");
  }

  const { head_slide_id: headSlideID } = await getPresentationByID(presentationID, [
    "head_slide_id",
  ]);
  return headSlideID;
}
