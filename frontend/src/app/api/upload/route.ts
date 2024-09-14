// route.ts

import { createPresignedPost } from '@aws-sdk/s3-presigned-post';
import { S3Client } from '@aws-sdk/client-s3';
import { updateItems } from '@/utils/dynamodb-interface-factory'; // Directly update database without auth
import { uuidv7 } from 'uuidv7';
import { auth } from "@/auth"

export async function POST(request: Request) {
  const { filename, contentType, presentationID } = await request.json();

  const extension = filename.split('.').pop();

  // Authenticate manually here because were sending a signed URL to the client
  const session = await auth();
  if (!session || !session.user || !session.user.id) {
    throw new Error("Unauthorized.");
  }

   // Directly update database without auth
  await updateItems('source', [{
    user_id: session.user.id,
    presentation_id: presentationID,
    source_id: uuidv7(),
    s3_filepath: `${filename}`,
    type: extension,
    name: `${filename}`
  }])

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