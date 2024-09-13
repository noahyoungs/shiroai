"use server"
import { getAllItemsForPresentationWithAuth } from "@/utils/dynamodb-service";

export async function retrieveSources(presentationID: string) {
  try {
    // Use the new getAllItemsForPresentationWithAuth function
    const sources = await getAllItemsForPresentationWithAuth("source", presentationID);

    // Assert that every source has a source_id, presentation_id, and user_id
    for (const source of sources) {
      if (!source.source_id || !source.presentation_id || !source.user_id) {
        throw new Error("Invalid source data");
      }
    }
    return sources;
  } catch (error) {
    console.error("Error retrieving sources:", error);
    throw new Error("Failed to retrieve sources");
  }
}