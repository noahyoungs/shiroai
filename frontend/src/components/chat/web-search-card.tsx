"use client";

import React from "react";
import { SearchResultItem } from "@/components/search-result-item";
import { Avatar } from "@nextui-org/react"
import { cn } from "@shared-utils/cn";
import { Code } from "@nextui-org/react";

export type WebSearchCardProps = React.HTMLAttributes<HTMLDivElement> & {
  avatar?: string;
  data?: any;
  className?: string;
  messageClassName?: string;
};

const WebSearchCard = React.forwardRef<HTMLDivElement, WebSearchCardProps>(
  (
    {
      avatar,
      data,
      className,
      messageClassName,
      ...props
    },
    ref,
  ) => {

    const messageRef = React.useRef<HTMLDivElement>(null);

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
        <div className={cn("flex flex-col flex-shrink overflow-hidden")}>
          {/* // Message bubble */}
          <div
            className={cn(
              "relative rounded-medium bg-content2 text-default-600",
              messageClassName,
            )}
          >
            {/* // Message content */}
            <div ref={messageRef} className={"text-small p-5"}>
              <div className="flex flex-row">
                <h3>Web Search: "{query}"</h3>
              </div>
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

            </div>
          </div>
        </div>
      </div>
    );
  },
);

export default WebSearchCard;

WebSearchCard.displayName = "WebSearchCard";
