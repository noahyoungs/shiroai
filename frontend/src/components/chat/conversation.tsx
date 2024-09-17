import React from "react";
import MessageCard from "./message-card";
import WebSearchCard from "./web-search-card";
import { Spinner } from "@nextui-org/react";
import { Icon } from "@iconify/react";
import { cn } from "@shared-utils/cn";
import { stat } from "fs";
import ToolReport from "./tool-report";
import { auth } from "@/auth";
import { useSession } from 'next-auth/react';

function getComponentForMessage(index: number, message: any, userProfileURL: string | undefined) {

  switch (message.role) {
    case "tool":
      return null;
    case "meta_web_search":
      return <WebSearchCard
        key={index}
        avatar="https://nextuipro.nyc3.cdn.digitaloceanspaces.com/components-images/avatar_ai.png"
        data={message.content}
      />
    case "meta_content_editor":
      return <ToolReport
        key={index}
        title="Edited Slide Content"
        content={message.content}
        className="bg-emerald-50 dark:bg-emerald-950"
        iconClassName="text-emerald-500 hover:text-emerald-300 dark:hover:text-emerald-700"
      />
    case "meta_image_editor":
      return <ToolReport
        key={index}
        title="Edited Slide Image"
        content={message.content}
        className="bg-fuchsia-50 dark:bg-fuchsia-950"
        iconClassName="text-fuchsia-500 hover:text-fuchsia-300 dark:hover:text-fuchsia-700"
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

export default function Component({
  messages = [] as any[],
  typing = false,
  classNames = "",
  statusMessage = "",
}) {

  const session = useSession();
  const userProfileURL = session.data?.user?.image;

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
            getComponentForMessage(index, message, userProfileURL || "undefined")
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
