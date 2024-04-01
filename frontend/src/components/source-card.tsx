import { Card, CardHeader, CardBody, CardFooter, Divider, Link, Image } from "@nextui-org/react";
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
    return (
        <Card className={cn("w-full py-4", className)}>
            <CardHeader className="flex-row justify-between">
                <h3 className="mb-0">Source {index + 1}</h3>
                <Icon
                    icon="tabler:trash-x"
                    width="32"
                    height="32"
                    className="text-danger/90"
                    onClick={() => deleteSource(source.id)}
                />
            </CardHeader>
            <Divider />
            <CardBody className="flex gap-3">
                {
                    source.type === "web" ? (
                        <SearchResultItem source={source.web_source} />
                    ) : (
                        <div className="flex flex-row items-center gap-3">
                            <Icon icon={getIcon(source.name)} width={32} className="text-default-600" />
                            <p>{source.name}</p>
                        </div>

                    )
                }

            </CardBody>
            <Divider />
            <CardFooter>
                <p>Lorem ipsum dolor sit amet, ea aute incididunt amet consequat labore dolor exercitation laborum ipsum voluptate esse cillum non nostrud lorem lorem esse est amet. Ut incididunt ullamco sunt magna eiusmod non ad occaecat sunt veniam tempor qui cillum excepteur occaecat sit irure adipiscing. Elit laborum sit eu elit aliqua dolor reprehenderit sed est laborum proident quis.</p>
            </CardFooter>
        </Card>
    )
}
