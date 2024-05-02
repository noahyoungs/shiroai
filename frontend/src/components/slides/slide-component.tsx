// SlideComponent.tsx
import React from "react";
import { Slide } from "@/utils/slide-types";
import { PillShortBulletsSlideComponent } from "@/components/slides/short-bullets-slides/short-bullets-slide-pills";
import { LongBulletsSlideComponent } from "@/components/slides/long-bullets-slide";
import { MarkdownTableSlideComponent } from "@/components/slides/markdown-table-slide";
import { SimpleMermaidSlideComponent } from "@/components/slides/mermaid-diagram-slide";
import { SectionHeaderSlideComponent } from "@/components/slides/section-header-slide";
import { PresentationTitleSlideComponent } from "@/components/slides/presentation-title-slide";
import { BoxesShortBulletsSlideComponent } from "@/components/slides/short-bullets-slides/short-bullets-slide-boxes";

interface SlideComponentProps {
    slide: Slide;
    presentationID: string;
    allSources?: any[];
    fetchSlide: (slideID: string) => void;
}

export const SlideComponent: React.FC<SlideComponentProps> = ({ slide, allSources, presentationID, fetchSlide }) => {
    switch (slide.slide_type) {
        case "short_bullets_slide":
            return <PillShortBulletsSlideComponent presentationID={presentationID} slide={slide} fetchSlide={fetchSlide} allSources={allSources} />;
        // return <BoxesShortBulletsSlideComponent slide={slide} allSources={allSources}/>;
        case "long_bullets_slide":
            return <LongBulletsSlideComponent presentationID={presentationID} slide={slide} fetchSlide={fetchSlide} allSources={allSources} />;
        case "markdown_table_slide":
            return <MarkdownTableSlideComponent presentationID={presentationID} slide={slide} fetchSlide={fetchSlide} allSources={allSources} />;
        case "simple_mermaid_slide":
            return <SimpleMermaidSlideComponent presentationID={presentationID} slide={slide} fetchSlide={fetchSlide} allSources={allSources} />;
        case "section_header_slide":
            return <SectionHeaderSlideComponent presentationID={presentationID} slide={slide} fetchSlide={fetchSlide} />;
        case "presentation_title_slide":
            return <PresentationTitleSlideComponent presentationID={presentationID} slide={slide} fetchSlide={fetchSlide} />;
        default:
            return <div>Slide type not supported</div>;
    }
};