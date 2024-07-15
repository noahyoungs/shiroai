import React from "react";
import MessageCard from "./message-card";
import WebSearchCard from "./web-search-card";
import { Spinner } from "@nextui-org/react";
import { Icon } from "@iconify/react";
import { cn } from "@/utils/cn";

export default function Component({
  messages = [] as any[],
  typing = false,
  classNames = "",
  statusMessage = "",
}) {
  return (
    <>
      {/* {JSON.stringify(messages)} */}
      {!messages || messages.length < 1 ? (
        <div
          className={cn(
            "flex flex-col items-center justify-center flex-grow",
            classNames
          )}
        >
          <Spinner size="lg" />
        </div>
      ) : (
        <div className={cn("flex flex-col gap-4 px-1", classNames)}>
          {messages.map(({ role, content }, index) =>
            role === "tool" ? null : role === "meta_web_search" ? (
              <WebSearchCard
                key={index}
                avatar="https://nextuipro.nyc3.cdn.digitaloceanspaces.com/components-images/avatar_ai.png"
                data={content}
                messageClassName="bg-sky-50 dark:bg-sky-950"
              />
            ) : (
              content && (
                <MessageCard
                  key={index}
                  avatar={
                    role === "user"
                      ? "https://d2u8k2ocievbld.cloudfront.net/memojis/male/6.png"
                      : "https://nextuipro.nyc3.cdn.digitaloceanspaces.com/components-images/avatar_ai.png"
                  }
                  message={content}
                  messageClassName={
                    role === "user"
                      ? "bg-content3 text-content3-foreground"
                      : role === "meta_research_agent"
                      ? "bg-sky-50 dark:bg-sky-950"
                      : role === "meta_content_editor"
                      ? "bg-emerald-50 dark:bg-emerald-950"
                      : role === "meta_image_editor"
                      ? "bg-fuchsia-50 dark:bg-fuchsia-950"
                      : ""
                  }
                  showFeedback={role === "assistant"}
                  status={role === "error" ? "failed" : "success"}
                />
              )
            )
          )}
          {typing ? (
            <MessageCard
              avatar="https://nextuipro.nyc3.cdn.digitaloceanspaces.com/components-images/avatar_ai.png"
              message={
                <Icon
                  icon="svg-spinners:3-dots-move"
                  className="text-4xl -my-2"
                />
              }
              shrinkWidth
            />
          ) : null}
        </div>
      )}
    </>
  );
}
