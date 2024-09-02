// route.ts

import { createPresignedPost } from '@aws-sdk/s3-presigned-post';
import { S3Client } from '@aws-sdk/client-s3';
import { getPresentationByID, createSource } from '@/utils/dynamodb';
import { auth } from "@/auth"
import { hashEmail } from '@/utils/hash-email';

export async function POST(request: Request) {
  const { filename, contentType, presentationID } = await request.json();

  const extension = filename.split('.').pop();

  const session = await auth();

  if (!session || !session.user) {
    throw new Error("Unauthorized.");
  }

  const presentation = await getPresentationByID(presentationID, ["user"]);

  if (presentation.user !== hashEmail(session.user.email)) {
    throw new Error("Unauthorized.");
  }

  const sourceID = await createSource(presentationID, {s3_filepath: `${filename}`, type: extension, name:`${filename}`});

  try {
    const client = new S3Client({ region: process.env.AWS_REGION });

    const { url, fields } = await createPresignedPost(client, {
      Bucket: process.env.SOURCES_BUCKET_NAME || '',
      Key: `${presentationID}/${filename}`, // Use presentationID as the folder
      Conditions: [
        ['content-length-range', 0, 10485760], // up to 10 MB
        ['starts-with', '$Content-Type', contentType],
      ],
      Fields: {
        'Content-Type': contentType,
      },
      Expires: 600, // Seconds before the presigned post expires. 3600 by default.
    });

    return Response.json({ url, fields });
  } catch (error: any) {
    console.error('Error occurred:', error);
    return Response.json({ error: error.message });
  }
}