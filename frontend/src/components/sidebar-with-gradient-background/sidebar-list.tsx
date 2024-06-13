"use server"
import PresentationListboxWithPagination from "@/components/sidebar-with-gradient-background/presentation-listbox-with-pagination";
import { getPresentationsByUserID } from "@/utils/dynamodb";
import { getServerSession } from "next-auth";
import { hashEmail } from '@/utils/hash-email';

export default async function NavbarList() {
  const session = await getServerSession();
  if (!session || !session.user || !session.user.email) {
    return <div>You must be signed in to view this page.</div>;
  }

  const initialResponse = await getPresentationsByUserID(hashEmail(session.user.email), ["topic", "status", "time_updated"], 10);

  const sortedPresentations = initialResponse.presentations?.sort((a, b) => {
    if (isNaN(a.time_updated) || isNaN(b.time_updated)) {
      return isNaN(a.time_updated) ? 1 : -1;
    }
    return b.time_updated - a.time_updated;
  });

  const presentationsWithHref = sortedPresentations?.map((presentation) => {
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

  return (
    <PresentationListboxWithPagination
      initialPresentations={presentationsWithHref}
      initialLastEvaluatedKey={initialResponse.lastEvaluatedKey}
    />
  );
}
