// chat.tsx
"use client";

import React, { useState, useEffect, useRef } from "react";
import { ScrollShadow } from "@nextui-org/react";
import Conversation from "./conversation";
import PromptInputBasic from "./prompt-input-basic";
import PromptInputDropbox from "./prompt-input-dropbox";
import { set } from "lodash";
import { Source } from '@/utils/database-types';

export type ChatProps = {
  presentationID: string;
  messages: any[];
  setMessages: React.Dispatch<React.SetStateAction<any[]>>;
  socket: any;
  block: boolean;
  setBlock: (block: boolean) => void;
  typing: any;
  sources?: Source[];
  refreshSources?: () => void;
  placeholder?: string;
  title?: string;
  statusMessage?: string;
  autoFocus?: boolean;
};

export function Chat({
  presentationID,
  messages,
  setMessages,
  socket,
  block,
  setBlock,
  typing,
  sources,
  refreshSources,
  placeholder,
  title = "Chat with Shiro",
  statusMessage = "",
  autoFocus = true,
}: ChatProps) {
  console.log("setMessages in Chat:", setMessages);

  const scrollShadowRef = useRef<HTMLDivElement>(null);
  const promptInputRef = useRef<HTMLDivElement>(null);

  // Scroll to bottom when new message is added
  useEffect(() => {
    if (scrollShadowRef.current) {
      scrollShadowRef.current.scrollTop = scrollShadowRef.current.scrollHeight;
    }
  }, [messages, statusMessage]);

  // Scroll to bottom when prompt input is resized
  useEffect(() => {
    const observer = new ResizeObserver(() => {
      if (scrollShadowRef.current) {
        scrollShadowRef.current.scrollTop =
          scrollShadowRef.current.scrollHeight;
      }
    });

    if (promptInputRef.current) {
      observer.observe(promptInputRef.current);
    }

    return () => {
      if (promptInputRef.current) {
        observer.unobserve(promptInputRef.current);
      }
    };
  }, []);

  if (!messages.length && placeholder) {
    messages = [{ role: "assistant", content: placeholder }];
  }

  return (
    <>
      <div className="flex flex-col h-full">
        <div className="text-center p-1 translate-y-2 flex-none">
          <p>{title}</p>
        </div>
        <ScrollShadow
          className="flex flex-col flex-auto grow"
          ref={scrollShadowRef}
          // hideScrollBar
          size={80}
          visibility="auto"
          offset={10}
        >
          <Conversation
            messages={messages}
            typing={typing}
            classNames="py-4"
            statusMessage={statusMessage}
          />
        </ScrollShadow>

        <div className="flex flex-col gap-2">
          <p className="px-2 text-tiny text-default-400">
            Shiro can make mistakes. Consider checking important information.
          </p>

          <div ref={promptInputRef}>
            {Array.isArray(sources) && refreshSources ? (
              <PromptInputDropbox
                setMessages={setMessages}
                socket={socket}
                block={block}
                setBlockSend={setBlock}
                sources={sources}
                presentationID={presentationID}
                refreshSources={refreshSources}
                autoFocus={autoFocus}
              />
            ) : (
              <PromptInputBasic
                setMessages={setMessages}
                statusMessage={statusMessage}
                socket={socket}
                block={block}
                setBlockSend={setBlock}
                autoFocus={autoFocus}
              />
            )}
          </div>
        </div>
      </div>
    </>
  );
}
