// frontend/src/app/api/images/cookie/[presentationID]/route.ts
import { NextResponse } from "next/server";
import { getSignedCookies } from "@aws-sdk/cloudfront-signer";
import { cookies } from 'next/headers';
import { type NextRequest } from 'next/server'
import { auth } from "@/auth"

export async function GET(req: NextRequest, { params }: { params: { presentationID: string } }) {

  if (!params.presentationID) {
    return new NextResponse("Presentation ID is required", { status: 400 });
  }

   // Authenticate manually here because were setting signed cookies
  const session = await auth();
  if (!session || !session.user || !session.user.id) {
    return new NextResponse("Not authenticated. Please log in.", { status: 401 });
  }


  // TODO: Reorganize s3 bucket to group presentations by user and allow access to entire user folder
  try {
    const resource = `https://${process.env.NEXT_PUBLIC_CLOUDFRONT_DOMAIN}/${params.presentationID}*`;
    const signedCookies = getSignedCookies({
      policy: JSON.stringify({
        Statement: [
          {
            Resource: resource,
            Condition: {
              DateLessThan: {
                "AWS:EpochTime": Math.floor(Date.now() / 1000) + 24 * 60 * 60, // 24 hours expiry
              },
            },
          },
        ],
      }),
      privateKey: process.env.CLOUDFRONT_PRIVATE_KEY!,
      keyPairId: process.env.CLOUDFRONT_KEY_PAIR_ID!,
    });

    Object.entries(signedCookies).forEach(([name, value]) => {
      cookies().set({
        name: name,
        value: value,
        httpOnly: true,
        path: '/',
        domain: '.meetshiro.com',
        expires: new Date(Date.now() + 24 * 60 * 60 * 1000) // Set the cookie to expire in 24 hours
      });
    });

    console

    const response = new NextResponse(`Signed cookies set, resource: ${resource}`, { status: 200 });

    return response;
  } catch (error) {
    console.error("Error generating signed cookies:", error);
    return new NextResponse("Error generating signed cookies", { status: 500 });
  }
}
