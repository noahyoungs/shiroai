import { SimpleMermaidSlide } from "@/utils/slide-types";
import Mermaid from "@/components/mermaid";

type SimpleMermaidSlideComponentProps = {
    presentationID: string;
    slide: SimpleMermaidSlide;
    fetchSlide: (slideID: string) => void;
    allSources?: any[];
    setBlockArrowKeys: (block: boolean) => void;
};
export function SimpleMermaidSlideComponent({ presentationID, slide, fetchSlide, allSources, setBlockArrowKeys }: SimpleMermaidSlideComponentProps) {
    return (
        <div className="p-12 flex flex-col relative overflow-hidden height-auto text-foreground bg-foreground/5 dark:bg-foreground/10 box-border bg-content1 outline-none shadow-medium rounded-large w-full aspect-videow-full aspect-video flex-none">
            <h1 className="self-start mb-0">{slide.slide_title}</h1>
            {/* Vertical centering: */}
            <div className="flex flex-col h-full pt-5">
                <div className="flex-grow"></div>
                <div className="flex-none">
                    <Mermaid
                        chart={slide.slide_content.mermaid_code}
                        className="w-full flex flex-row justify-center max-h-[50vh]"
                    />
                </div>
                <div className="flex-grow"></div>
            </div>
        </div>
    );
}
