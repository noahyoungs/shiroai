import React from "react";
import MessageCard from "./message-card";
import WebSearchCard from "./web-search-card";
import { Spinner } from "@nextui-org/react";
import { Icon } from "@iconify/react";
import { cn } from "@shared-utils/cn";
import { stat } from "fs";
import ToolReport from "./tool-report";
import { auth } from "@/auth";

function getComponentForMessage(index: number, message: any, userProfileURL: string | undefined) {
  switch (message.role) {
    case "tool":
      return null;
    case "meta_web_search":
      return <WebSearchCard
        key={index}
        avatar="https://nextuipro.nyc3.cdn.digitaloceanspaces.com/components-images/avatar_ai.png"
        data={message.content}
        messageClassName="bg-sky-50 dark:bg-sky-950"
      />
    case "meta_content_editor":
      return <ToolReport
        key={index}
        title="Edited Slide Content"
        content={message.content}
      />
    case "meta_image_editor":
      return <ToolReport
        key={index}
        title="Edited Slide Image"
        content={message.content}
      />
    case "user":
      return message.content ? <MessageCard
        key={index}
        avatar={userProfileURL}
        message={message.content}
        messageClassName="bg-content3 text-content3-foreground"
        /> : null
    case "assistant":
      return message.content ? <MessageCard
        key={index}
        avatar="https://nextuipro.nyc3.cdn.digitaloceanspaces.com/components-images/avatar_ai.png"
        message={message.content}
        // messageClassName="bg-content3 text-content3-foreground"
        /> : null
    case "error":
      return <MessageCard
        key={index}
        avatar="https://nextuipro.nyc3.cdn.digitaloceanspaces.com/components-images/avatar_ai.png"
        message={message.content}
        status={'failed'}
        />
    default:
      return `Strange message: ${JSON.stringify(message)}`;
  }
}

export default async function Component({
  messages = [] as any[],
  typing = false,
  classNames = "",
  statusMessage = "",
}) {

  const session = await auth()
  const userProfileURL = session?.user?.image ?? undefined;
  
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
          {messages.map((message, index) =>
            getComponentForMessage(index, message, userProfileURL)
          )}
          {
            statusMessage && !typing && (
              <MessageCard
                avatar="https://nextuipro.nyc3.cdn.digitaloceanspaces.com/components-images/avatar_ai.png"
                message={statusMessage}
                messageClassName=""
              />
            )
          }
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
