import React from "react";
import { Accordion, AccordionItem, Avatar } from "@nextui-org/react";
import { cn } from "@shared-utils/cn";
import { Icon } from "@iconify/react";
interface ToolReportProps {
  title: string;
  content: string;
  className?: string;
  iconClassName?: string;
}

const ToolReport: React.FC<ToolReportProps> = ({ title, content, className, iconClassName }) => {
  return (
    <div className="w-full flex gap-3">
        <Avatar className="flex-none" src="https://nextuipro.nyc3.cdn.digitaloceanspaces.com/components-images/avatar_ai.png" />
    <Accordion isCompact variant="shadow" className={cn("w-full", className)}>
      <AccordionItem
        key="1"
        aria-label={title}
        title={title}
        indicator={({ isOpen }) => ( isOpen ? <Icon icon="tabler:chevron-right" width={24} height={24} className={iconClassName}/> : <Icon icon="tabler:report-search" width={24} height={24} className={iconClassName}/>)}
        classNames={{heading: "mb-0"}}
      >
        {content}
      </AccordionItem>
    </Accordion>
    </div>
  );
};

export default ToolReport;