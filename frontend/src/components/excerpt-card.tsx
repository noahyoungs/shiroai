import { Card, CardHeader, CardBody, Divider } from "@nextui-org/react";
import { getIcon } from "@/utils/get-file-icon";
import { SearchResultItem } from "./search-result-item";
import { Icon } from "@iconify/react";
type ExcerptCardProps = {
    text: string;
    source: any;
};

export function ExcerptCard({ text, source }: ExcerptCardProps) {
    return (
        <>
            <h3 className="text-left text-lg">Source Excerpt</h3>
            <Card className="max-w-2xl">
                <CardHeader>
                    {
                        source.type === "web" ? (
                            <SearchResultItem source={source.web_source} description={false} />
                        ) : (
                            <div className="flex flex-row items-center gap-3">
                                <Icon icon={getIcon(source.name) || 'file-unknown'} width={32} className="text-default-600" />
                                <p>{source.name}</p>
                            </div>
                        )
                    }
                </CardHeader>
                <Divider/>
                <CardBody>
                    <p>{text}</p>
                </CardBody>
            </Card>
        </>
    )
}
