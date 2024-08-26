// frontend/src/components/slides/view-only/view-only-presentation-title-slide.tsx
import React from "react";
import { PresentationTitleSlide } from "../utils/slide-types";
import { ViewOnlySlideImage } from "./view-only-slide-image";
import { ViewOnlyTitle } from "./view-only-title";

type ViewOnlyPresentationTitleSlideComponentProps = {
  slide: PresentationTitleSlide;
  classNames?: string;
  signedUrlSuffix?: string;
};

export function ViewOnlyPresentationTitleSlideComponent({
  slide,
  classNames,
  signedUrlSuffix,
}: ViewOnlyPresentationTitleSlideComponentProps) {
  return (
    <div className="relative overflow-visible w-full h-full">
      <div
        className="absolute mx-12 mb-3 bottom-10 z-[21] text-white/90 w-[90%]"
        id="presentation-title"
      >
        <ViewOnlyTitle
          title={slide.slide_title}
          classNames="!text-white/90"
        />
      </div>
      <ViewOnlySlideImage
        image={slide.image}
        variant="full"
        signedUrlSuffix={signedUrlSuffix}
      />
    </div>
  );
}
