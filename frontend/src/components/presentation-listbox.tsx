"use client"
import {
  Listbox,
  ListboxItem
} from "@nextui-org/react";

type PresentationListboxProps = {
  presentations?: {
    id: string;
    href?: string;
    topic?: string;
    status?: string;
    time_updated: number;
  }[];
};


function PresentationListbox({ presentations }: PresentationListboxProps) {

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
            key={presentation.id}
            color={"default"}
            href={presentation.href}
          >
            {presentation.topic || "Untitled Presentation"}
          </ListboxItem>
        )}
      </Listbox>

  );
}

export default PresentationListbox;