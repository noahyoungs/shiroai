"use client";

import React from "react";
import { Button, Tooltip } from "@nextui-org/react";
import { Icon } from "@iconify/react";


import { cn } from "@/utils/cn";

import PromptInput from "./prompt-input";

export default function Component({ socket, block, setBlockSend }: { socket: any, block: boolean, setBlockSend: (block: boolean) => void }) {
  const [isRegenerating, setIsRegenerating] = React.useState<boolean>(false);
  const [prompt, setPrompt] = React.useState<string>("");

  const onRegenerate = () => {
    setIsRegenerating(true);
    setTimeout(() => {
      setIsRegenerating(false);
    }, 1000);
  };

  const sendMessage = () => {
    console.log("Sending message: ", prompt)
    if (prompt.trim() !== "" && socket) {
      socket.emit("message", prompt);
      setPrompt("");
      setBlockSend(true);
    }
  };


  return (
    <div className="flex w-full flex-col gap-4">
      {/* <div>
        <Button
          isDisabled={isRegenerating}
          size="sm"
          startContent={
            <Icon
              className={cn("text-medium", isRegenerating ? "origin-center animate-spin" : "")}
              icon="solar:restart-linear"
            />
          }
          variant="flat"
          onPress={onRegenerate}
        >
          Regenerate
        </Button>
      </div> */}
      <form className="flex w-full flex-col items-start rounded-medium bg-default-100 transition-colors hover:bg-default-200/70">
        <PromptInput
          classNames={{
            inputWrapper: "!bg-transparent shadow-none",
            innerWrapper: "relative",
            input: "pt-1 pl-2 pb-6 !pr-10 text-medium",
          }}
          endContent={
            <div className="flex items-end gap-2">
              <Tooltip
                showArrow
                placement="left"
                color={block ? "warning" : "default"}
                content={block ? 'Please wait until the assistant replies' : 'Send message'}
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
                      !prompt || block ? "text-default-600" : "text-primary-foreground",
                    )}
                    icon="tabler:arrow-narrow-up"
                    width={20}
                    onClick={() => { if (!block) sendMessage() }}
                  />
                </Button>
              </Tooltip>
            </div>
          }
          minRows={3}
          radius="lg"
          value={prompt}
          variant="flat"
          onValueChange={setPrompt}
          onSendMessage={() => { if (!block) sendMessage() }}
          disableAutosize
          placeholder="Enter a prompt here"
        />
      </form>
    </div>
  );
}
