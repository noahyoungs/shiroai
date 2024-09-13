"use server"
import { uuidv7 } from "uuidv7";
import { updateItemsWithAuth } from "@/utils/dynamodb-service";
import { revalidatePath } from 'next/cache';
import { redirect } from 'next/navigation'

export default async function CreatePresentation() {
  const uuid = uuidv7();

  try {
    const presentation = {
      presentation_id: uuid,
      status: "new",
      created_time: Date.now(),
    };

    console.log(JSON.stringify(presentation));

    await updateItemsWithAuth('presentation', [presentation]);

  } catch (error) {
    console.error("Error creating presentation:", error);
    throw new Error("Failed to create presentation");
  }
  redirect(`/home/create/${uuid}/ideate`);

  return uuid;
}