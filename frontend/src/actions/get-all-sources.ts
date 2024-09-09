"use server"
import { getAllItemsForPresentationWithAuth } from "@/utils/dynamodb-service";

export async function retrieveSources(presentationID: string) {
  try {
    // Use the new getAllItemsForPresentationWithAuth function
    const sources = await getAllItemsForPresentationWithAuth("source", presentationID);
    return sources;
  } catch (error) {
    console.error("Error retrieving sources:", error);
    throw new Error("Failed to retrieve sources");
  }
}