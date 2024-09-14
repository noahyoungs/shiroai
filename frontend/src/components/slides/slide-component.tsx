// frontend/src/components/slides/slide-component.tsx
import React from "react";
import { Slide } from "@shared-utils/database-types";
import { PillShortBulletsSlideComponent } from "@/components/slides/short-bullets-slides/short-bullets-slide-pills";
import { MarkdownSlideComponent } from "@/components/slides/markdown-slide";
import { SimpleMermaidSlideComponent } from "@/components/slides/mermaid-diagram-slide";
import { SectionHeaderSlideComponent } from "@/components/slides/section-header-slide";
import { PresentationTitleSlideComponent } from "@/components/slides/presentation-title-slide";
import { BoxesShortBulletsSlideComponent } from "@/components/slides/short-bullets-slides/short-bullets-slide-boxes";

// View Only
import { ViewOnlyPresentationTitleSlideComponent } from "./view-only/view-only-presentation-title-slide";
import { ViewOnlySectionHeaderSlideComponent } from "./view-only/view-only-section-header-slide";
import { ViewOnlySimpleMermaidSlideComponent } from "./view-only/view-only-mermaid-diagram-slide";
import { ViewOnlyMarkdownSlideComponent } from "./view-only/view-only-markdown-slide";
import { ViewOnlyPillShortBulletsSlideComponent } from "./view-only/view-only-short-bullets-slide-pills";
import { ViewOnlyBoxesShortBulletsSlideComponent } from "./view-only/view-only-short-bullets-slide-boxes";

interface CommonSlideComponentProps {
  slide: Slide;
  allSources?: any[];
  thumbnail?: boolean;
}

interface EditModeProps extends CommonSlideComponentProps {
  viewOnly?: false;
  setSlide: (slide: Partial<Slide>, splitSlides?: boolean) => void;
  presentationID: string;
  setBlockArrowKeys: (block: boolean) => void;
}

interface ViewOnlyModeProps extends CommonSlideComponentProps {
  viewOnly: true;
}

type SlideComponentProps = EditModeProps | ViewOnlyModeProps;

export const SlideComponent: React.FC<SlideComponentProps> = (props) => {
  const { slide, allSources, thumbnail } = props;

  if (props.viewOnly) {
    switch (slide.slide_type) {
      case "short_bullets_slide":
        return slide.layout === 'list' ? (
          <ViewOnlyPillShortBulletsSlideComponent slide={slide} allSources={allSources} />
        ) : (
          <ViewOnlyBoxesShortBulletsSlideComponent slide={slide} allSources={allSources} />
        );

      case "markdown_slide":
        return <ViewOnlyMarkdownSlideComponent slide={slide} allSources={allSources} />;

      case "simple_mermaid_slide":
        return <ViewOnlySimpleMermaidSlideComponent slide={slide} allSources={allSources} />;

      case "section_header_slide":
        return <ViewOnlySectionHeaderSlideComponent slide={slide} thumbnail={thumbnail}/>;

      case "presentation_title_slide":
        return <ViewOnlyPresentationTitleSlideComponent slide={slide} thumbnail={thumbnail}/>;

      default:
        return <div>Slide type not supported: {JSON.stringify(slide)}</div>;
    }
  } else {
    const { setSlide, presentationID, setBlockArrowKeys } = props;

    switch (slide.slide_type) {
      case "short_bullets_slide":
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
  }
};
