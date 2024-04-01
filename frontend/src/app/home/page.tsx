import PresentationListbox from "@/components/presentation-listbox"
import CreatePresentation from "@/components/create-presentation-button"
import { getPresentationsByUserID } from "@/utils/dynamodb"
import { getServerSession } from "next-auth";
import { hashEmail } from '@/utils/hash-email';

export default async function Page() {
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

  return (
    <PresentationListbox
     presentations={sortedPresentations}
     />
  )
}
