import React from "react";
import { Button } from "@nextui-org/react";
import { Icon } from "@iconify/react";
import { AddScriptModal } from "@/components/slides/action-buttons/add-script-modal";
import { AddNotesModal } from "@/components/slides/action-buttons/add-notes-modal";
import { GenerateVideoModal } from "@/components/slides/action-buttons/generate-video-modal";
import { ExportToPdfModal } from "@/components/slides/action-buttons/export-to-pdf-modal";
import { ExportToPptModal } from "@/components/slides/action-buttons/export-to-ppt-modal";
import { ShareModal } from "@/components/slides/action-buttons/share-modal";
import { max } from "lodash";
import { cn } from "@/utils/cn";

export function ActionButtonBar({
  presentationId,
  generateScriptNotes,
  className,
}: {
  presentationId: string;
  generateScriptNotes: (
    target: "script" | "notes",
    style: number,
    customStyle?: string,
    maxChars?: number
  ) => void;
  className?: string;
}) {
  return (
    <div className={cn("flex flex-row gap-4", className)}>
      <AddScriptModal onGenerate={generateScriptNotes.bind(null, "script")} />
      <AddNotesModal onGenerate={generateScriptNotes.bind(null, "notes")} />
      <GenerateVideoModal />
      <ExportToPdfModal presentationId={presentationId} />
      <ExportToPptModal />
      <ShareModal />
    </div>
  );
}
