// frontend/src/app/api/images/cookie/[presentationID]/route.ts
import { NextResponse } from "next/server";
import { getSignedCookies } from "@aws-sdk/cloudfront-signer";
import { cookies } from 'next/headers';
import { type NextRequest } from 'next/server'
import { getPresentationByID } from '@/utils/dynamodb';
import { auth } from "@/auth"
import { hashEmail } from '@/utils/hash-email';

export async function GET(req: NextRequest, { params }: { params: { presentationID: string } }) {

  if (!params.presentationID) {
    return new NextResponse("Presentation ID is required", { status: 400 });
  }

  // Authenticate
  const session = await auth();
  if (!session || !session.user) {
    return new NextResponse("Not authenticated. Please log in.", { status: 401 });
  }

  const presentation = await getPresentationByID(params.presentationID, ["user"]);

  if (!presentation) {
    return new NextResponse("Presentation not found", { status: 404 });
  }

  if (presentation.user !== hashEmail(session.user.email)) {
    return new NextResponse("You are not authorized to access this presentation", { status: 403 });
  }


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
