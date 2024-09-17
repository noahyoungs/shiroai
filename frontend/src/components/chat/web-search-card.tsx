"use client";

import React from "react";
import { SearchResultItem } from "@/components/search-result-item";
import { Avatar, Accordion, AccordionItem } from "@nextui-org/react"
import { cn } from "@shared-utils/cn";
import { Icon } from "@iconify/react";

export type WebSearchCardProps = React.HTMLAttributes<HTMLDivElement> & {
  avatar?: string;
  data?: any;
  className?: string;
};

const WebSearchCard = React.forwardRef<HTMLDivElement, WebSearchCardProps>(
  (
    {
      avatar,
      data,
      className,
      ...props
    },
    ref,
  ) => {


    let query = data.query;
    let sources = data.sources;

    return (
      // Message container
      <div {...props} ref={ref} className={cn("flex gap-3 w-full", className)}>
        {/* // Avatar container */}
        <div className="relative flex-none">
          <Avatar src={avatar} />
        </div>
        {/* // Message content container */}
        <div className={"flex flex-col flex-shrink overflow-hidden w-full"}>
          {/* // Message bubble */}
          
            {/* // Message content */}
              <Accordion isCompact variant="shadow" className="bg-sky-50 dark:bg-sky-950">
                <AccordionItem
                  key="1"
                  aria-label={`Web Search for "${query}"`}
                  title={`Searched the Web for "${query}"`}
                  indicator={({ isOpen }) => (isOpen ? <Icon icon="tabler:chevron-right" className="text-sky-500 hover:text-sky-300 dark:hover:text-sky-700" width={24} height={24} /> : <Icon icon="tabler:world-search" className="text-sky-500 hover:text-sky-300 dark:hover:text-sky-700" width={24} height={24} />)}
                  classNames={{  heading: "mb-0"}}
                >
                  <div className="flex flex-col gap-6">
                    {sources && sources.length >= 1 && sources.map((source: any, index: number) => (
                      // Search item
                      <SearchResultItem
                        key={index}
                        source={source}
                        className=""
                      />
                    ))}
                  </div>
                </AccordionItem>
              </Accordion>

            </div>
      </div>
    );
  },
);

export default WebSearchCard;

WebSearchCard.displayName = "WebSearchCard";
