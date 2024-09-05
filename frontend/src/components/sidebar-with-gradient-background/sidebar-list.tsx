"use server"
import PresentationListboxWithPagination from "@/components/sidebar-with-gradient-background/presentation-listbox-with-pagination";
import { getPresentationsByUserID } from "@/utils/dynamodb";
import { auth } from "@/auth"

export default async function SidebarList() {
  const session = await auth();
  if (!session || !session.user || !session.user.id) {
    return <div>You must be signed in to view this page.</div>;
  }

  const initialResponse = await getPresentationsByUserID(session.user.id, ["topic", "status", "time_updated"], 10);

  const sortedPresentations = initialResponse.presentations?.sort((a, b) => {
    if (isNaN(a.time_updated) || isNaN(b.time_updated)) {
      return isNaN(a.time_updated) ? 1 : -1;
    }
    return b.time_updated - a.time_updated;
  });

  return (
    <PresentationListboxWithPagination
      initialPresentations={sortedPresentations}
      initialLastEvaluatedKey={initialResponse.lastEvaluatedKey}
    />
  );
}
