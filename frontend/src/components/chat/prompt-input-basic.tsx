import React, { useState, useCallback } from "react";
import { useDropzone } from "react-dropzone";
import { Button, Tooltip } from "@nextui-org/react";
import { Icon } from "@iconify/react";
import { cn } from "@/utils/cn";
import PromptInput from "./prompt-input";

interface PromptInputBasicProps {
  setMessages: React.Dispatch<React.SetStateAction<any[]>>;
  socket: any;
  block: boolean;
  setBlockSend: (block: boolean) => void;
  statusMessage: string;
}

export default function PromptInputBasic({
  setMessages,
  socket,
  block,
  setBlockSend,
  statusMessage,
}: PromptInputBasicProps) {
  const [prompt, setPrompt] = useState<string>("");

  const sendMessage = useCallback(async () => {
    console.log("sendMessage called");
    console.log("setMessages:", setMessages);
    console.log("typeof setMessages:", typeof setMessages);
    console.log("Sending message: ", prompt);
    if (prompt.trim() !== "" && socket) {
      const newMessages = [];
      if (statusMessage) {
        const statusMessageObj = { role: 'assistant', content: statusMessage };
        socket.emit("message", statusMessageObj);
        newMessages.push(statusMessageObj);
      }
      const userMessage = { role: 'user', content: prompt.trim() };
      socket.emit("message", userMessage);
      newMessages.push(userMessage);

      // Add messages to messages for display
      setMessages((prevMessages: any[]) => [...prevMessages, ...newMessages]);
      setPrompt("");
      setBlockSend(true);
    }
  }, [prompt, socket, statusMessage, setMessages, setBlockSend]);

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
                  onClick={() => {
                    if (!block) sendMessage();
                  }}
                >
                  <Icon
                    className={cn(
                      "[&>path]:stroke-[2px]",
                      !prompt || block ? "text-default-600" : "text-primary-foreground"
                    )}
                    icon="tabler:arrow-narrow-up"
                    width={20}
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