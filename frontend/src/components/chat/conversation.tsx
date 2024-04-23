import React from "react";
import MessageCard from "./message-card";
import WebSearchCard from "./web-search-card";
import {Spinner} from "@nextui-org/react";
import { Icon } from "@iconify/react";
import { cn } from "@/utils/cn";

export default function Component({ messages = [] as any[], typing = false, classNames= ""}) {
  return (
    <>
      {/* {JSON.stringify(messages)} */}
      {!messages || messages.length < 1 ? (
        <div className={cn("flex flex-col items-center justify-center flex-grow", classNames)}>
          <Spinner size="lg" />
        </div>
      ) : (
        <div className={cn("flex flex-col gap-4 px-1", classNames)}>
          {messages.map(({ role, content }, index) => (
            (role == "assistant" || role == "error" || role == "user" || role == "meta_research_agent") ? (
              content && (
                <MessageCard
                key={index}
                // attempts={index === 1 ? 2 : 1}
                avatar={
                  role === "assistant" || role === "error" || role === "meta_research_agent"
                    ? "https://nextuipro.nyc3.cdn.digitaloceanspaces.com/components-images/avatar_ai.png"
                    : "https://d2u8k2ocievbld.cloudfront.net/memojis/male/6.png"
                }
                // currentAttempt={index === 1 ? 2 : 1}
                message={content}
                messageClassName={role === "user" ? "bg-content3 text-content3-foreground" : role === "meta_research_agent" ? "bg-sky-50 dark:bg-sky-950" : ""}
                showFeedback={role === "assistant"}
                status={role === "error" ? "failed" : "success"}
              />
              )
            ) : (
             role === "meta_web_search" ? (
              <WebSearchCard
                key={index}
                avatar="https://nextuipro.nyc3.cdn.digitaloceanspaces.com/components-images/avatar_ai.png"
                data={content}
                messageClassName="bg-sky-50 dark:bg-sky-950"
              />
             ) : null
            )
          ))}
          {typing? (
            <MessageCard
              avatar="https://nextuipro.nyc3.cdn.digitaloceanspaces.com/components-images/avatar_ai.png"
              message={<Icon icon="svg-spinners:3-dots-move" className="text-4xl -my-2"/>}
              shrinkWidth
            />
          ) : null
          }
        </div>
      )}
    </>
  );
}