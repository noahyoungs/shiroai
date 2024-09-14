import { Image, Link } from "@nextui-org/react";
import NextImage from "next/image";
import { cn } from "@shared-utils/cn";


type SearchResultItemProps = {
    source: any
    index?: number
    className?: string
    description?: boolean
};

export function SearchResultItem({ source, index, className, description: detail = true }: SearchResultItemProps) {

    return (
        <div className={cn("flex flex-col", className)}>
            {/* // publisher profile */}
            <div className={"flex flex-row gap-3 items-center"}>
                {(index != undefined || index != null) && <span className="text-lg text-foreground">{index + 1}.</span>}
                <Image
                    src={source.profile.img}
                    radius="lg"
                    className="bg-[#eee] min-w-[32px] border border-default-500"
                    fallbackSrc="/tabler--world-www.svg"
                    width={32}
                />
                <div className="flex flex-col w-full">
                    <p className="text-foreground mb-0 leading-tight">{source.profile.name}</p>
                    {
                        detail ? <p className="text-foreground text-tiny truncate max-w-[85%]">{source.netloc + " " + source.path}</p>
                            : <Link
                                href={source.url}
                                className="text-blue-500 text-base max-w-full leading-tight"
                                isExternal
                                showAnchorIcon
                            >
                                {source.title}
                            </Link>
                    }
                </div>
            </div>
            {
                detail && <Link
                    href={source.url}
                    className="text-blue-500 mt-0.5 text-base"
                    isExternal
                    showAnchorIcon
                >
                    {source.title}
                </Link>
            }

            {detail && <p className="text-foreground/70 text-tiny max-w-[95%]" dangerouslySetInnerHTML={{ __html: source.description }} />}
        </div>
    )
}

