import React from "react";
import { Slide } from "@shared-utils/database-types";

// View Only
import { ViewOnlyPresentationTitleSlideComponent } from "./view-only-presentation-title-slide";
import { ViewOnlySectionHeaderSlideComponent } from "./view-only-section-header-slide";
import { ViewOnlySimpleMermaidSlideComponent } from "./view-only-mermaid-diagram-slide";
import { ViewOnlyMarkdownSlideComponent } from "./view-only-markdown-slide";
import { ViewOnlyPillShortBulletsSlideComponent } from "./view-only-short-bullets-slide-pills";
import { ViewOnlyBoxesShortBulletsSlideComponent } from "./view-only-short-bullets-slide-boxes";

interface SlideComponentProps {
  slide: Slide;
  allSources?: any[];
  signedUrlSuffix?: string;
  dark : boolean;
}

export const SlideComponent: React.FC<SlideComponentProps> = (props) => {
  const { slide, allSources, signedUrlSuffix, dark} = props;

  switch (slide.slide_type) {
    case "short_bullets_slide":
      return slide.layout === "list" ? (
        <ViewOnlyPillShortBulletsSlideComponent
          slide={slide}
          allSources={allSources}
        />
      ) : (
        <ViewOnlyBoxesShortBulletsSlideComponent
          slide={slide}
          allSources={allSources}
        />
      );

    case "markdown_slide":
      return (
        <ViewOnlyMarkdownSlideComponent slide={slide} allSources={allSources} />
      );

    case "simple_mermaid_slide":
      return (
        <ViewOnlySimpleMermaidSlideComponent
          slide={slide}
          allSources={allSources}
          dark={dark}
        />
      );

    case "section_header_slide":
      return <ViewOnlySectionHeaderSlideComponent slide={slide} signedUrlSuffix={signedUrlSuffix}/>;

    case "presentation_title_slide":
      return <ViewOnlyPresentationTitleSlideComponent slide={slide} signedUrlSuffix={signedUrlSuffix}/>;

    default:
      return <div>Slide type not supported: {JSON.stringify(slide)}</div>;
  }
};
