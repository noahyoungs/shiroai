"use server"
import {
    getSources as dynamodbGetSources,
    getPresentationByID,
    getSlide as dynamodbGetSlide,
    getSlides as dynamodbGetSlides,
    batchUpdateSlides,
    updateSlide as dynamodbUpdateSlide,
    deleteSlide as dynamodbDeleteSlide,
} from "@/utils/dynamodb";
import { getServerSession } from 'next-auth';
import { hashEmail } from '@/utils/hash-email';
import { testSlideFunctions } from '@/utils/test-slides-dynamodb';
import { Slide } from '@/utils/slide-types';

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
 * Retrieves the slides for a presentation.
 * @param presentationID - The ID of the presentation.
 * @returns A promise that resolves to an array of slides, or throws an error if the slides cannot be retrieved.
 */
export async function getSlides(presentationID: string) {
    
    await authenticateUser(presentationID);

    try {
        const slides = await dynamodbGetSlides(presentationID);
        return sortSlides(slides);
    } catch (error) {
        console.error("Error retrieving slides:", error);
        throw new Error("Failed to retrieve slides");
    }
}

/**
 * Retrieves a specific slide from a presentation.
 * @param presentationID - The ID of the presentation.
 * @param slideID - The ID of the slide.
 * @returns A promise that resolves to the requested slide, or throws an error if the slide cannot be retrieved.
 */
export async function getSlide(presentationID: string, slideID: string) {
    
    await authenticateUser(presentationID);

    try {
        const slide = await dynamodbGetSlide(presentationID, slideID);
        return slide;
    } catch (error) {
        console.error("Error retrieving slide:", error);
        throw new Error("Failed to retrieve slide");
    }
}

/**
 * Updates the slides in a presentation.
 * @param presentationID - The ID of the presentation.
 * @param slides - An array of slides to update.
 * @returns A promise that resolves when the slides are successfully updated, or throws an error if the slides cannot be updated.
 */
export async function updateSlides(presentationID: string, slides: Slide[]) {
    
    await authenticateUser(presentationID);

    try {
        await batchUpdateSlides(presentationID, slides);
    } catch (error) {
        console.error("Error updating slides:", error);
        throw new Error("Failed to update slides");
    }
}

/**
 * Updates a specific slide in a presentation.
 * @param presentationID - The ID of the presentation.
 * @param slide - The slide to update. The slide must have an ID.
 * @returns A promise that resolves when the slide is successfully updated, or throws an error if the slide cannot be updated.
 */
export async function updateSlide(presentationID: string, slide: Slide) {
    await authenticateUser(presentationID);
  
    try {
      const { id, ...slideWithoutId } = slide;
      await dynamodbUpdateSlide(presentationID, id, slideWithoutId);
    } catch (error) {
      console.error("Error updating slide:", error);
      throw new Error("Failed to update slide");
    }
}