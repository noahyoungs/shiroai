// frontend/src/components/slides/view-only/view-only-title.tsx
import React from "react";
import { cn } from "../../../utils/cn";

type ViewOnlyTitleProps = {
  title: string;
  classNames?: string;
};

export function ViewOnlyTitle({ title, classNames }: ViewOnlyTitleProps) {
  return (
    <div className="border-b-medium border-transparent rounded-none">
      <div
        className={cn(
          "pb-[8px] box-border text-4xl font-bold [overflow-wrap:anywhere]",
          classNames
        )}
      >
        {title}
      </div>
    </div>
  );
}
