"use server"
import { getSources, getPresentationByID} from "@/utils/dynamodb";
import { auth } from "@/auth"
import { hashEmail } from '@/utils/hash-email';


export async function retrieveSources(presentationID: string) {
  const session = await auth();

  if (!session || !session.user) {
    throw new Error("Unauthorized.");
  }

  const presentation = await getPresentationByID(presentationID, ["user"]);

  if (presentation.user !== hashEmail(session.user.email)) {
    throw new Error("Unauthorized.");
  }

  try {
    const sources = await getSources(presentationID);
    return sources;
  } catch (error) {
    console.error("Error retrieving sources:", error);
    throw new Error("Failed to retrieve sources");
  }
}