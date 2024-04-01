"use client";

import React, { useState, useEffect, useRef } from "react";
import { ScrollShadow } from "@nextui-org/react";
import Conversation from "./conversation";
import PromptInputWithRegenerateButton from "./prompt-input-with-regenerate-button";
import PromptInputDropbox from "./prompt-input-dropbox";
import { set } from "lodash";

export interface ChatProps {
  presentationID: string;
  messages: any[];
  socket: any;
  block: boolean;
  setBlock: (block: boolean) => void;
  typing: boolean;
  sources?: any[];
  refreshSources?: () => void;
}

export function Chat({ presentationID, messages, socket, block, setBlock, typing, sources, refreshSources }: ChatProps) {
  const scrollShadowRef = useRef<HTMLDivElement>(null);


  useEffect(() => {
    if (scrollShadowRef.current) {
      scrollShadowRef.current.scrollTop = scrollShadowRef.current.scrollHeight;
    }
  }, [messages]);

  return (
    <>
      <div className="flex h-full w-full max-w-full flex-col gap-10">
        <ScrollShadow className="flex h-[66vh] xl:h-[65vh] flex-col" ref={scrollShadowRef}>
          <Conversation messages={messages} typing={typing} />
        </ScrollShadow>
        <div className="flex flex-col gap-2">
          {
            (Array.isArray(sources) && refreshSources) ?
              <PromptInputDropbox
                socket={socket}
                block={block}
                setBlockSend={setBlock}
                sources={sources}
                presentationID={presentationID}
                refreshSources={refreshSources}
              />
              :
              <PromptInputWithRegenerateButton
                socket={socket}
                block={block}
                setBlockSend={setBlock}
              />
          }

          <p className="px-2 text-tiny text-default-400">
            AI Presenter can make mistakes. Consider checking important information.
          </p>
        </div>
      </div>
    </>
  );
}