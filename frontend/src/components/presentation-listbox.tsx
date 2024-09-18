"use client"
import {
  Listbox,
  ListboxItem
} from "@nextui-org/react";

import { Presentation } from "@shared-utils/database-types";

type PresentationListboxProps = {
  presentations?: Presentation[];
};


function PresentationListbox({ presentations }: { presentations: { presentation_id: string; topic: string; status: string }[]}) {

  return (

    <Listbox
      items={presentations}
      aria-label="List of presentations"
      className="p-0 "
      itemClasses={{
        base: "data-[hover=true]:bg-background/50 px-2 mx-0 my-1",
        title: "text-clip line-clamp-2 text-foreground !no-underline",
      }}
    >
      {(presentation) => (
        <ListboxItem
          key={presentation.presentation_id}
          color={"default"}
          href={
            presentation.status && ['ideate', 'research', 'outline', 'slides'].includes(presentation.status)
              ? `/home/create/${presentation.presentation_id}/${presentation.status}`
              : `/home/create/${presentation.presentation_id}/ideate`
          }
        >
          {presentation.topic || "Untitled Presentation"}
        </ListboxItem>
      )}
    </Listbox>

  );
}

export default PresentationListbox;