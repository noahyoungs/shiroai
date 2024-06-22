// SlideComponent.tsx
import React from "react";
import { Slide } from "@/utils/slide-types";
import { PillShortBulletsSlideComponent } from "@/components/slides/short-bullets-slides/short-bullets-slide-pills";
import { MarkdownSlideComponent } from "@/components/slides/markdown-slide";
import { SimpleMermaidSlideComponent } from "@/components/slides/mermaid-diagram-slide";
import { SectionHeaderSlideComponent } from "@/components/slides/section-header-slide";
import { PresentationTitleSlideComponent } from "@/components/slides/presentation-title-slide";
import { BoxesShortBulletsSlideComponent } from "@/components/slides/short-bullets-slides/short-bullets-slide-boxes";

interface SlideComponentProps {
  slide: Slide;
  setSlide: (slide: Partial<Slide>) => void;
  presentationID: string;
  allSources?: any[];
  setBlockArrowKeys: (block: boolean) => void;
}


export const SlideComponent: React.FC<SlideComponentProps> = ({
  slide,
  setSlide,
  allSources,
  presentationID,
  setBlockArrowKeys,
}) => {
  // console.log(`Slide ID: ${slide.id}`);
  switch (slide.slide_type) {
    case "short_bullets_slide":
      // Alternate between PillShortBulletsSlideComponent and BoxesShortBulletsSlideComponent
      return slide.layout === 'list' ? (
        <PillShortBulletsSlideComponent
          presentationID={presentationID}
          slide={slide}
          setSlide={setSlide}
          allSources={allSources}
          setBlockArrowKeys={setBlockArrowKeys}
        />
      ) : (
        <BoxesShortBulletsSlideComponent
          presentationID={presentationID}
          slide={slide}
          setSlide={setSlide}
          allSources={allSources}
          setBlockArrowKeys={setBlockArrowKeys}
        />
      );
      
    case "markdown_slide":
      return (
        <MarkdownSlideComponent
          presentationID={presentationID}
          slide={slide}
          setSlide={setSlide}
          allSources={allSources}
          setBlockArrowKeys={setBlockArrowKeys}
        />
      );

    case "simple_mermaid_slide":
      return (
        <SimpleMermaidSlideComponent
          presentationID={presentationID}
          slide={slide}
          setSlide={setSlide}
          allSources={allSources}
          setBlockArrowKeys={setBlockArrowKeys}
        />
      );

    case "section_header_slide":
      return (
        <SectionHeaderSlideComponent
          presentationID={presentationID}
          slide={slide}
          setSlide={setSlide}
          setBlockArrowKeys={setBlockArrowKeys}
        />
      );

    case "presentation_title_slide":
      return (
        <PresentationTitleSlideComponent
          presentationID={presentationID}
          slide={slide}
          setSlide={setSlide}
          setBlockArrowKeys={setBlockArrowKeys}
        />
      );

    default:
      return <div>Slide type not supported: {JSON.stringify(slide)}</div>;
  }
};