// interface.tsx

"use client"

import { Spinner, Spacer, Button, ScrollShadow, Progress } from "@nextui-org/react";
import { SourceCard } from "@/components/source-card";
import { useRouter } from 'next/navigation';
import { Icon } from "@iconify/react";
import { Source } from '@/utils/database-types';


interface InterfaceProps {
  sources: Source[];
  deleteSource: (source_id: string) => void;
  block: boolean;
  presentationID: string;
  refreshSources: () => void;
  loading: boolean;
  redirectPath: string;
  progress: number;
}

export default function Interface({ sources, deleteSource, block, presentationID, refreshSources, loading: loading, redirectPath, progress }: InterfaceProps) {
  const router = useRouter();

  // sources = [{ "id": "d096403e-3c8f-4b9a-9934-a924f84faf91", "presentation_id": "094075ea-7c21-4d62-b33c-d855ff997398", "name": "Canada.pdf", "s3_filepath": "Canada.pdf", "type": "pdf" }, { "type": "web", "url": "https://www.thecanadianencyclopedia.ca/en/timeline/100-great-events-in-canadian-history", "id": "39551a35-d075-493c-a67f-cb4fcddf4e7b", "web_source": { "title": "Significant Events in Canadian History | The Canadian Encyclopedia", "url": "https://www.thecanadianencyclopedia.ca/en/timeline/100-great-events-in-canadian-history", "description": "The significance of an <strong>event</strong> cannot be measured scientifically. Every historian, journalist or student could make their own lists. This selection is meant to d", "page_age": null, "netloc": "thecanadianencyclopedia.ca", "path": "› en › timeline › 100-great-events-in-canadian-history", "profile": { "name": "Thecanadianencyclopedia", "img": "https://imgs.search.brave.com/eJCy-w2OQpEvibO36Q-SdSf_YqhoqZIjRFtnv2v0HEs/rs:fit:32:32:1/g:ce/aHR0cDovL2Zhdmlj/b25zLnNlYXJjaC5i/cmF2ZS5jb20vaWNv/bnMvYmQxODM0ZjUx/OTU4YzEwNmI5ZWI1/NGQwZTMyYjgyNWQy/NzQ2MzUwNDA4NTBk/ZDhlMjFmZjI1ZDI5/MzY5MDNkOS93d3cu/dGhlY2FuYWRpYW5l/bmN5Y2xvcGVkaWEu/Y2E" } } }, { "type": "web", "url": "https://thecanadaguide.com/data/important-dates/", "id": "a33520ab-37da-4026-9f9a-aa0668e0f468", "web_source": { "title": "Timeline of Important Dates in Canadian History", "url": "https://thecanadaguide.com/data/important-dates/", "description": "Early descendants of Canada&#x27;s aboriginal people cross the Bering land bridge from east Asia into North America · Viking explorers are believed to be the first Europeans to visit North America and establish L’Anse aux Meadows settlement on the island of Newfoundland", "page_age": "2022-01-16T20:15:09", "netloc": "thecanadaguide.com", "path": " › home › data › important dates", "profile": { "name": "The Canada Guide", "img": "https://imgs.search.brave.com/IVDb8Xae2X8_hfBI_WGy89GiFCCGknXa_uLrO5HAZuU/rs:fit:32:32:1/g:ce/aHR0cDovL2Zhdmlj/b25zLnNlYXJjaC5i/cmF2ZS5jb20vaWNv/bnMvYmIyNDIxNWNi/NjkxYTM3MTllNTBk/OWE1N2JlMmJmNzFk/ZTkwMGViODcxZjdh/ODkyMmFiMDI1ZjZm/OGMwNjRjMC90aGVj/YW5hZGFndWlkZS5j/b20v" } } }]

  // sort sources by id
  sources.sort((a, b) => {
    if (a.source_id < b.source_id) {
      return -1;
    }
    if (a.source_id > b.source_id) {
      return 1;
    }
    return 0;
  });

  return (
    <div className="flex flex-col h-full flex-auto">
      {/* Sticky title at top */}
      <div className="text-center p-1 translate-y-2">
        {/* Text and spinner side by side */}
        <div className="flex gap-2 align-middle justify-center ">
          <p>{"List of Presentation Sources"}</p>
          {(loading) &&
            <Spinner size="sm" className="p-0 m-0" />
          }
        </div>
      </div>
      <ScrollShadow
        className="flex-auto"
        hideScrollBar
        size={80}
      >

        {
          // JSON.stringify(sources)
        }
        <div className={sources[0] ? "flex flex-col gap-4 py-4" : "flex flex-col items-center justify-center h-[90%]"}>
          {!sources[0] ? (
            <div className="text-foreground/70 italic">
              Shiro will create a list of sources to gather information for your presentation. <br />
              To begin, send a file to Shiro or ask Shiro to search the web.
            </div>
          ) : (
            sources.map((sources, index) => (
              <SourceCard
                key={sources.source_id}
                source={sources}
                deleteSource={deleteSource}
                index={index}
              />
            ))
          )}
        </div>

        <Spacer y={6} />

      </ScrollShadow>
      {
        progress >= 100 ? (
          <Button
            color="primary"
            className="min-h-[64px] flex flex-row rounded-b-none text-base"
            isDisabled={block}
            onClick={() => {
              !block && router.push(redirectPath);
            }}
          >
            <span>Proceed to the next step ({progress}%)</span>
            <Icon icon="tabler:arrow-narrow-right" width={30} />

          </Button>
        ) : (
          <>
            <Progress
              aria-label="Researching..."
              value={progress}
              className="rounded-none z-[1000] translate-y-[64px] rounded-0 max-w-full opacity-100"
              classNames={{
                track: "rounded-none bg-transparent",
              }}
            />
            <Button
              color="primary"
              className="min-h-[64px] flex flex-row rounded-b-none text-base"
              isDisabled={true}
              onClick={() => {
                !block && router.push(redirectPath);
              }}
            >
              <span>Shiro needs to do more research ({progress}%)</span>
              <Icon icon="tabler:clock-search" width={25} />
            </Button>
          </>

        )
      }
    </div>
  );
}