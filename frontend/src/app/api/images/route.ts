// app/api/images/route.ts

import { NextResponse } from "next/server";
import { S3Client, GetObjectCommand } from "@aws-sdk/client-s3";
import { getSignedUrl } from "@aws-sdk/s3-request-presigner";

type ResponseData = {
  url: string;
};

export const revalidate = 600 // 10 minutes

export async function GET(request: Request): Promise<ResponseData> {
  const { searchParams } = new URL(request.url);
  const key = searchParams.get('key');

  if (!key) {
    return new NextResponse('Missing key parameter', { status: 400 });
  }

  try {
    const s3Client = new S3Client({
      region: process.env.AWS_REGION,
      credentials: {
        accessKeyId: process.env.AWS_ACCESS_KEY_ID!,
        secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY!,
      },
    });

    const command = new GetObjectCommand({
      Bucket: process.env.SOURCES_BUCKET_NAME!,
      Key: key,
    });

    const url = await getSignedUrl(s3Client, command, { expiresIn: 600 }); // 600 seconds = 10 minutes

    return new NextResponse(JSON.stringify({ url }), {
      headers: { 'Content-Type': 'application/json' },
    });
  } catch (error) {
    console.error('Error fetching signed URL from S3:', error);
    return new NextResponse('Error fetching signed URL from S3', { status: 500 });
  }
}