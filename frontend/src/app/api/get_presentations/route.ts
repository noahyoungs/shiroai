// app/api/getPresentations/route.ts
import { NextRequest, NextResponse } from 'next/server';
import { getPresentationsByUserID } from '@/utils/dynamodb';
import { auth } from "@/auth"
import { hashEmail } from '@/utils/hash-email';

export async function POST(request: NextRequest) {
  try {
    const session = await auth();
    if (!session || !session.user || !session.user.email) {
      return NextResponse.json({ message: "Unauthorized" }, { status: 401 });
    }

    const { lastEvaluatedKey } = await request.json();

    const response = await getPresentationsByUserID(
      hashEmail(session.user.email),
      ["topic", "status", "time_updated"],
      10,
      lastEvaluatedKey
    );

    if (!response?.presentations) {
      return NextResponse.json({ message: "Internal Server Error" }, { status: 500 });
    }

    return NextResponse.json({
      presentations: response.presentations,
      lastEvaluatedKey: response.lastEvaluatedKey,
    });
  } catch (error) {
    console.error("Error fetching presentations:", error);
    return NextResponse.json({ message: "Internal Server Error" }, { status: 500 });
  }
}
