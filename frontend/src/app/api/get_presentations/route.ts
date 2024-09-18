// app/api/getPresentations/route.ts
import { NextRequest, NextResponse } from 'next/server';
import { fetchPresentationsForAuthenticatedUser } from "@/utils/dynamodb-service";
import { auth } from "@/auth";
import { AttributeValue } from '@aws-sdk/client-dynamodb';

export async function POST(request: NextRequest) {
  try {
    const session = await auth();
    if (!session || !session.user || !session.user.id) {
      return NextResponse.json({ message: "Unauthorized" }, { status: 401 });
    }

    const { lastEvaluatedKey } = await request.json();

    const result = await fetchPresentationsForAuthenticatedUser(
      lastEvaluatedKey as Record<string, AttributeValue> | undefined,
      15
    );

    return NextResponse.json({
      presentations: result.presentations,
      lastEvaluatedKey: result.lastEvaluatedKey
    });
  } catch (error) {
    console.error("Error fetching presentations:", error);
    return NextResponse.json({ message: "Internal Server Error" }, { status: 500 });
  }
}
