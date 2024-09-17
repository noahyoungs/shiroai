// app/api/getPresentations/route.ts
import { NextRequest, NextResponse } from 'next/server';
import { fetchPresentationsForAuthenticatedUser } from "@/utils/dynamodb-service";
import { auth } from "@/auth"

export async function POST(request: NextRequest) {
  try {
    const session = await auth();
    if (!session || !session.user || !session.user.id) {
      return NextResponse.json({ message: "Unauthorized" }, { status: 401 });
    }

    const { lastFetchedGSI1SK } = await request.json();

    const presentations = await fetchPresentationsForAuthenticatedUser(
      lastFetchedGSI1SK,
      15
    );

    if (!presentations) {
      return NextResponse.json({ message: "Internal Server Error" }, { status: 500 });
    }

    const lastItem = presentations[presentations.length - 1];
    const newLastFetchedGSI1SK = lastItem ? lastItem.gsi1sk : null;

    return NextResponse.json({
      presentations,
      lastFetchedGSI1SK: newLastFetchedGSI1SK,
    });
  } catch (error) {
    console.error("Error fetching presentations:", error);
    return NextResponse.json({ message: "Internal Server Error" }, { status: 500 });
  }
}
