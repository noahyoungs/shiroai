import { Divider } from "@nextui-org/react";
type SourceCardProps = {
    source: any;
    deleteSource: (id: string) => void;
    className?: string;
    index: number;
};

import { SearchResultItem } from "./search-result-item";

import { Icon } from "@iconify/react"
import { getIcon } from "@/utils/get-file-icon";
import { cn } from "@/utils/cn";


export function SourceCard({ source, deleteSource, className, index }: SourceCardProps) {
    let pending = !source.char_count ? "opacity-50" : "";
    return (
        <div className={cn("rounded-xl flex flex-col bg-content2 max-w-full overflow-hidden", className, pending)} >
            <div className="flex gap-3 p-3 relative">
                <>
                    {source.type === "web" ? (
                        <SearchResultItem source={source.web_source} description={false} />
                    ) : (
                        <div className="flex flex-row items-center gap-3">
                            <Icon icon={getIcon(source.name) || 'file-unknown'} width={32} className="text-default-600" />
                            <p>{source.name}</p>
                        </div>
                    )}
                    <Icon
                        icon="tabler:trash-x"
                        width="27"
                        height="27"
                        className="text-danger/90 absolute top-0 right-0 mt-4 mr-4"
                        onClick={() => deleteSource(source.id)}
                    />
                </>
            </div>
                <>
                    <Divider />
                    <div className="p-3">
                        <p>{source.summary || "Shiro is reading this source..."}</p>
                    </div>
                </>
        </div>
    )

}
