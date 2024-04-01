"use client";

import type { TextAreaProps } from "@nextui-org/react";
import React from "react";
import { Textarea } from "@nextui-org/react";
import { cn } from "@/utils/cn";

const PromptInput = React.forwardRef<
  HTMLTextAreaElement,
  TextAreaProps & { onSendMessage: () => void }
>(({ classNames = {}, onSendMessage, ...props }, ref) => {
  return (
    <Textarea
      ref={ref}
      aria-label="Prompt"
      className="min-h-[40px]"
      classNames={{
        ...classNames,
        label: cn("hidden", classNames?.label),
        input: cn("py-0", classNames?.input),
      }}
      minRows={1}
      radius="lg"
      variant="bordered"
      onKeyDown={(e) => {
        if (e.key === "Enter" && !e.shiftKey) {
          e.preventDefault();
          onSendMessage();
        }
      }}
      {...props}
    />
  );
});

export default PromptInput;

PromptInput.displayName = "PromptInput";