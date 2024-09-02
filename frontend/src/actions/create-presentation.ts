"use server"
import { auth } from "@/auth"
import { hashEmail } from '@/utils/hash-email';
import { uuidv7 } from "uuidv7";
import { updatePresentationByID } from "@/utils/dynamodb";
import { revalidatePath } from 'next/cache';
import { redirect } from 'next/navigation'

export default async function CreatePresentation() {
  let uuid = uuidv7();

  const session = await auth();
  console.log(`Session: ${JSON.stringify(session)}`);

  if (!session || !session.user || !session.user.name) {
    throw new Error("Unauthorized.");
  }

  const presentation = {
    user: hashEmail(session.user.email),
    status: "new",
    updated_time: Math.floor(Date.now() / 1000) // Add Unix timestamp
  };

  console.log(JSON.stringify(presentation));

  await updatePresentationByID(uuid, presentation);

  redirect(`/home/create/${uuid}/ideate`)

  return uuid;
}