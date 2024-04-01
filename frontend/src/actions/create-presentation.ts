"use server"
import { getServerSession } from "next-auth";
import { hashEmail } from '@/utils/hash-email';
import { v4 as uuidv4 } from 'uuid';
import { updatePresentationByID } from "@/utils/dynamodb";
import { revalidatePath } from 'next/cache';
import { redirect } from 'next/navigation'

export default async function CreatePresentation() {
  let uuid = uuidv4();

  const session = await getServerSession();
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

  revalidatePath('/home');
  redirect(`home/create/${uuid}/ideate`)

  return uuid;
}