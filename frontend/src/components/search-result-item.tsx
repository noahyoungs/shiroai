import { Image, Link } from "@nextui-org/react";
import NextImage from "next/image";
import { cn } from "@/utils/cn";

type SearchResultItemProps = {
    source: any
    index?: number
    className?: string
    description?: boolean
};

export function SearchResultItem({ source, index, className, description=true }: SearchResultItemProps) {

    return (
        <div className={cn("flex flex-col", className)}>
            {/* // publisher profile */}
            <div className={"flex flex-row gap-3 items-center"}>
                { (index != undefined || index != null ) && <span className="text-lg text-foreground">{index + 1}.</span>}
                <Image
                    src={source.profile.img}
                    radius="lg"
                    className="bg-[#eee] min-w-[32px] border border-default-500"
                    fallbackSrc="/tabler--world-www.svg"
                    width={32}
                />
                <div className="flex flex-col w-[85%]">
                    <p className="text-foreground">{source.profile.name}</p>
                    <p className="text-foreground text-tiny truncate max-w-full">{source.netloc + " " + source.path}</p>
                </div>
            </div>
            <Link
                href={source.url}
                className="text-blue-500 mt-0.5 text-base"
                isExternal
                showAnchorIcon
            >
                {source.title}
            </Link>
                { description && <p className="text-foreground/70 text-tiny max-w-[95%]" dangerouslySetInnerHTML={{ __html: source.description }} /> }
        </div>
    )
}

