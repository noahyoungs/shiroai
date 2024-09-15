import React from "react";
import { SectionHeaderSlide } from "@shared-utils/database-types";
import { ViewOnlySlideImage } from "./view-only-slide-image";
import { ViewOnlyTitle } from "./view-only-title";

type ViewOnlySectionHeaderSlideComponentProps = {
  slide: SectionHeaderSlide;
  classNames?: string;
  signedUrlSuffix?: string;
};

export function ViewOnlySectionHeaderSlideComponent({
  slide,
  classNames,
  signedUrlSuffix,
}: ViewOnlySectionHeaderSlideComponentProps) {
  const isImageLeft = slide.image_position !== "right"; // Defaults to left if image_position is undefined or any other value except 'right'

  return (
    <div className="flex flex-row relative w-screen h-screen">
      {isImageLeft ? (
        <>
          <div className="aspect-square h-screen">
            <ViewOnlySlideImage
              image={slide.image}
              variant={slide.image_position}
              signedUrlSuffix={signedUrlSuffix}
            />
          </div>
          <div className="flex-auto flex flex-col justify-center p-12">
            <ViewOnlyTitle
              title={slide.slide_title}
              classNames={classNames}
            />
          </div>
        </>
      ) : (
        <>
          <div className="flex-auto flex flex-col justify-center p-12">
            <ViewOnlyTitle
              title={slide.slide_title}
              classNames={classNames}
            />
          </div>
          <div className="aspect-square h-full">
            <ViewOnlySlideImage
              image={slide.image}
              variant={slide.image_position}
              signedUrlSuffix={signedUrlSuffix}
            />
          </div>
        </>
      )}
    </div>
  );
}
