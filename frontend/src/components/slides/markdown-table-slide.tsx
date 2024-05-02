import { MarkdownTableSlide } from "@/utils/slide-types";
import Markdown from 'markdown-to-jsx'
import { Tooltip } from "@nextui-org/react";
import { ExcerptCard } from "@/components/excerpt-card";
import { Icon } from "@iconify/react";

type MarkdownTableSlideComponentProps = {
    slide: MarkdownTableSlide;
    allSources?: any[];
};
export function MarkdownTableSlideComponent({ slide, allSources }: MarkdownTableSlideComponentProps) {
    type FootnoteProps = {
        number: string;
        children: string;
    };

    function Footnote({ children }: FootnoteProps) {
        const excerpt = slide.slide_content.footnotes[children];
        return (
            excerpt && allSources && allSources.length > 0 &&
            (<Tooltip
                content={<ExcerptCard text={excerpt.text} source={allSources.find((source) => source.id === excerpt.source_id)} />}
                placement="bottom"
                showArrow
                className="items-start p-4"
            >
                <div className="inline-block px-1 text-primary">
                    <Icon icon="tabler:input-search" width="20" height="20" />
                </div>
            </Tooltip>)

        );
    }

    return (
        <div className="p-12 flex flex-col relative overflow-hidden height-auto text-foreground dark:bg-foreground/10 bg-foreground/5 box-border bg-content1 outline-none shadow-medium rounded-large w-full aspect-videow-full aspect-video flex-none">
            <h1 className="self-start">{slide.slide_title}</h1>
            <div className="flex-auto"></div>
            <div className="flex justify-center w-full flex-none slide-markdown">
                <Markdown
                    options={{
                        overrides: {
                            sup: {
                                component: Footnote,
                                props: {
                                },
                            },
                        },
                    }}
                >
                    {slide.slide_content.table}
                </Markdown>
            </div>
            <div className="flex-auto"></div>
        </div>
    );
}
