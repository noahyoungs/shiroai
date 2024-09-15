// frontend/src/components/slides/view-only/view-only-section-header-slide.tsx
import React from "react";
import { SectionHeaderSlide } from '@shared-utils/database-types';
import { ViewOnlySlideImage } from "./view-only-slide-image";
import { ViewOnlyTitle } from "./view-only-title";

type ViewOnlySectionHeaderSlideComponentProps = {
  slide: SectionHeaderSlide;
  classNames?: string;
  thumbnail?: boolean;
};

export function ViewOnlySectionHeaderSlideComponent({
  slide,
  classNames,
  thumbnail = false,
}: ViewOnlySectionHeaderSlideComponentProps) {
  const isImageLeft = slide.image_position !== "right"; // Defaults to left if image_position is undefined or any other value except 'right'

  return (
    <div className="flex flex-row relative overflow-visible w-full aspect-video">
      {isImageLeft ? (
        <>
          <div className="aspect-square h-full">
            <ViewOnlySlideImage
              image={slide.image}
              variant={slide.image_position}
              thumbnail={thumbnail}
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
              thumbnail={thumbnail}
            />
          </div>
        </>
      )}
    </div>
  );
}
