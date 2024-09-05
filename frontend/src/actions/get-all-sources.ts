"use server"
import { getSources, getPresentationByID} from "@/utils/dynamodb";

export async function retrieveSources(presentationID: string) {

  try {
    const sources = await getSources(presentationID);
    return sources;
  } catch (error) {
    console.error("Error retrieving sources:", error);
    throw new Error("Failed to retrieve sources");
  }
}