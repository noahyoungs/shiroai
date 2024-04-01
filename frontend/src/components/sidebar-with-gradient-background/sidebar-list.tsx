"use server"
import PresentationListbox from "@/components/presentation-listbox"
import CreatePresentation from "@/components/create-presentation-button"
import { getPresentationsByUserID } from "@/utils/dynamodb"
import { getServerSession } from "next-auth";
import { hashEmail } from '@/utils/hash-email';

export default async function NavbarList() {
  const session = await getServerSession();
  if (!session || !session.user || !session.user.name) {
    return <div>You must be signed in to view this page.</div>;
  }

  let presentations = await getPresentationsByUserID(hashEmail(session.user.email), ["topic", "status", "time_updated"])
  console.log(`Presentations: ${JSON.stringify(presentations)}`)

  const sortedPresentations = presentations?.sort((a, b) => {
    if (isNaN(a.time_updated) || isNaN(b.time_updated)) {
      return isNaN(a.time_updated) ? 1 : -1;
    }
    return b.time_updated - a.time_updated;
  });

  // Add href to each presentation
  // href is `home/create/${id}/ideate` if status is "new" or "ideate"
  // href is `home/create/${id}/research` if status is "research"
  const presentationsWithHref = sortedPresentations?.map((presentation) => {
    let href = null;
    if (presentation.status === "new" || presentation.status === "ideate") {
      href = `/home/create/${presentation.id}/ideate`;
    } else if (presentation.status === "research") {
      href = `/home/create/${presentation.id}/research`;
    }
    return {
      ...presentation,
      href
    }
  })

  return (
    <PresentationListbox
     presentations={presentationsWithHref}
     />
  )
}
