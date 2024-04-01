// interface.tsx

"use client"

import { Spinner, Spacer, Button, ScrollShadow } from "@nextui-org/react";
import { SourceCard } from "@/components/source-card";
import { useRouter } from 'next/navigation';

interface InterfaceProps {
  sources: any[];
  deleteSource: (id: string) => void;
  block: boolean;
  presentationID: string;
  refreshSources: () => void;
  sourcesLoading: boolean;
  redirectPath: string;
}

export default function Interface({ sources, deleteSource, block, presentationID, refreshSources, sourcesLoading, redirectPath }: InterfaceProps) {
  const router = useRouter();

  // sources = [{ "id": "d096403e-3c8f-4b9a-9934-a924f84faf91", "presentation_id": "094075ea-7c21-4d62-b33c-d855ff997398", "name": "Canada.pdf", "s3_filepath": "Canada.pdf", "type": "pdf" }, { "type": "web", "url": "https://www.thecanadianencyclopedia.ca/en/timeline/100-great-events-in-canadian-history", "id": "39551a35-d075-493c-a67f-cb4fcddf4e7b", "web_source": { "title": "Significant Events in Canadian History | The Canadian Encyclopedia", "url": "https://www.thecanadianencyclopedia.ca/en/timeline/100-great-events-in-canadian-history", "description": "The significance of an <strong>event</strong> cannot be measured scientifically. Every historian, journalist or student could make their own lists. This selection is meant to d", "page_age": null, "netloc": "thecanadianencyclopedia.ca", "path": "› en › timeline › 100-great-events-in-canadian-history", "profile": { "name": "Thecanadianencyclopedia", "img": "https://imgs.search.brave.com/eJCy-w2OQpEvibO36Q-SdSf_YqhoqZIjRFtnv2v0HEs/rs:fit:32:32:1/g:ce/aHR0cDovL2Zhdmlj/b25zLnNlYXJjaC5i/cmF2ZS5jb20vaWNv/bnMvYmQxODM0ZjUx/OTU4YzEwNmI5ZWI1/NGQwZTMyYjgyNWQy/NzQ2MzUwNDA4NTBk/ZDhlMjFmZjI1ZDI5/MzY5MDNkOS93d3cu/dGhlY2FuYWRpYW5l/bmN5Y2xvcGVkaWEu/Y2E" } } }, { "type": "web", "url": "https://thecanadaguide.com/data/important-dates/", "id": "a33520ab-37da-4026-9f9a-aa0668e0f468", "web_source": { "title": "Timeline of Important Dates in Canadian History", "url": "https://thecanadaguide.com/data/important-dates/", "description": "Early descendants of Canada&#x27;s aboriginal people cross the Bering land bridge from east Asia into North America · Viking explorers are believed to be the first Europeans to visit North America and establish L’Anse aux Meadows settlement on the island of Newfoundland", "page_age": "2022-01-16T20:15:09", "netloc": "thecanadaguide.com", "path": " › home › data › important dates", "profile": { "name": "The Canada Guide", "img": "https://imgs.search.brave.com/IVDb8Xae2X8_hfBI_WGy89GiFCCGknXa_uLrO5HAZuU/rs:fit:32:32:1/g:ce/aHR0cDovL2Zhdmlj/b25zLnNlYXJjaC5i/cmF2ZS5jb20vaWNv/bnMvYmIyNDIxNWNi/NjkxYTM3MTllNTBk/OWE1N2JlMmJmNzFk/ZTkwMGViODcxZjdh/ODkyMmFiMDI1ZjZm/OGMwNjRjMC90aGVj/YW5hZGFndWlkZS5j/b20v" } } }]
  
  // // sort sources by time_updated
  // sources.sort((a, b) => {
  //   return (b.time_updated - a.time_updated)
  // });

  return (
    <div className="p-5 flex flex-col max-h-[85vh]">
      <div className="flex gap-4 align-middle mb-3">
        <h1 className="m-0">Sources & Research</h1>
        {(sourcesLoading) &&
          <Spinner size="md" className="p-0 m-0" />
        }
      </div>
      <ScrollShadow>


        {
          // JSON.stringify(sources)
        }
        {
          sources[0] && sources.map((source, index) => (
            <SourceCard
              key={source.id}
              source={source}
              deleteSource={deleteSource}
              className="my-4"
              index={index}
            />
          ))
        }


        {/* <Spacer y={6} />
        <div className="flex items-middle gap-2">
          <Input
            type="url"
            label="URL"
            size="sm"
          />
          <Button color="primary" size="lg">
            Add URL Source
          </Button>
        </div> */}

        <Spacer y={6} />

      </ScrollShadow>
      <Button
        color="primary"
        className="w-full block min-h-[40px]"
        onClick={() => {
          router.push(redirectPath);
        }}>
        Proceed to Next Step
      </Button>
    </div>
  );
}