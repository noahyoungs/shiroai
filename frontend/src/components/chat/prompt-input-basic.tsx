"use client";

import React, { useState } from "react";
import { useDropzone } from "react-dropzone";
import { Button, Tooltip } from "@nextui-org/react";
import { Icon } from "@iconify/react";
import { cn } from "@/utils/cn";
import PromptInput from "./prompt-input";

export default function Component({
  socket,
  block,
  setBlockSend,
}: {
  socket: any;
  block: boolean;
  setBlockSend: (block: boolean) => void;
}) {
  const [prompt, setPrompt] = useState<string>("");

  const sendMessage = async () => {
    console.log("Sending message: ", prompt);
    if (prompt.trim() !== "" && socket) {
      socket.emit("message", prompt);
      setPrompt("");
      setBlockSend(true);
    }
  };

  const { getRootProps, getInputProps } = useDropzone();

  return (
    <div {...getRootProps()} className="flex w-full flex-col gap-4 flex-grow">
      <div className="flex w-full flex-col items-start rounded-t-xl bg-default-100 transition-colors hover:bg-default-200/70 h-full">
        <PromptInput
          classNames={{
            inputWrapper: "!bg-transparent shadow-none h-full flex-grow p-4",
            innerWrapper: "relative h-full",
            input: "pr-10 text-medium h-full",
          }}
          endContent={
            <div className="flex items-end gap-1.5">
              <Tooltip
                showArrow
                placement="top-end"
                color={block ? "warning" : "default"}
                content={
                  block
                    ? "Please wait until the assistant replies"
                    : "Send message"
                }
              >
                <Button
                  isIconOnly
                  color={!prompt ? "default" : "primary"}
                  isDisabled={!prompt}
                  radius="lg"
                  size="sm"
                  variant="solid"
                >
                  <Icon
                    className={cn(
                      "[&>path]:stroke-[2px]",
                      !prompt || block ? "text-default-600" : "text-primary-foreground"
                    )}
                    icon="tabler:arrow-narrow-up"
                    width={20}
                    onClick={() => {
                      if (!block) sendMessage();
                    }}
                  />
                </Button>
              </Tooltip>
            </div>
          }
          radius="lg"
          value={prompt}
          variant="flat"
          onValueChange={setPrompt}
          onSendMessage={() => {
            if (!block) sendMessage();
          }}
          placeholder={"Message Shiro..."}
        />
      </div>
    </div>
  );
}