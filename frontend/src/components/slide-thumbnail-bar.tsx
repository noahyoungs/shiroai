// SlideThumbnailBar.tsx

import React, { useEffect, useRef } from 'react';
import { Slide } from '@/utils/slide-types';
import { SlideThumbnail } from '@/components/slide-thumbnail';
import { cn } from '@/utils/cn';

interface SlideThumbnailBarProps {
  slides: Slide[];
  currentSlideID: string | null;
  setCurrentSlideID: (slideID: string) => void;
  blockSlideSwitching: boolean;
}

export function SlideThumbnailBar({ slides, currentSlideID, setCurrentSlideID, blockSlideSwitching }: SlideThumbnailBarProps) {
  const thumbnailRefs = useRef<(HTMLDivElement | null)[]>([]);

  useEffect(() => {
    const currentIndex = slides.findIndex((slide) => slide.id === currentSlideID);
    if (currentIndex !== -1 && thumbnailRefs.current[currentIndex]) {
      thumbnailRefs.current[currentIndex]?.scrollIntoView({
        behavior: 'smooth',
        block: 'nearest',
        inline: 'center',
      });
    }
  }, [currentSlideID, slides]);

  return (
    <div className="flex overflow-x-auto gap-4">
      {slides.map((slide, index) => (
        <div
          key={slide.id}
          ref={(el) => (thumbnailRefs.current[index] = el)}
        >
          {/* <SlideThumbnail
            slide={slide}
            selected={slide.id === currentSlideID}
            onClick={() => setCurrentSlideID(slide.id)}
          /> */}
          <div className={cn("w-[128px] aspect-video rounded-lg overflow-hidden", slide.id === currentSlideID && 'border-2 border-primary-500' )} onClick={!blockSlideSwitching ? () => setCurrentSlideID(slide.id) : undefined} >{slide.slide_title}</div>
        </div>
      ))}
    </div>
  );
}