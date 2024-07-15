// app/api/getPresentations/route.ts
import { NextRequest, NextResponse } from 'next/server';
import { getPresentationsByUserID } from '@/utils/dynamodb';
import { getServerSession } from 'next-auth';
import { hashEmail } from '@/utils/hash-email';

export async function POST(request: NextRequest) {
  try {
    const session = await getServerSession();
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

    const presentationsWithHref = response.presentations.map((presentation) => {
      let href = null;
      switch (presentation.status) {
        case "new":
        case "ideate":
          href = `/home/create/${presentation.id}/ideate`;
          break;
        case "research":
          href = `/home/create/${presentation.id}/research`;
          break;
        case "outline":
          href = `/home/create/${presentation.id}/outline`;
          break;
        case "slides":
          href = `/home/create/${presentation.id}/slides`;
          break;
      }

      return {
        ...presentation,
        href,
      };
    });

    return NextResponse.json({
      presentations: presentationsWithHref,
      lastEvaluatedKey: response.lastEvaluatedKey,
    });
  } catch (error) {
    console.error("Error fetching presentations:", error);
    return NextResponse.json({ message: "Internal Server Error" }, { status: 500 });
  }
}
