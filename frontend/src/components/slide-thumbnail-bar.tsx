import React, { useEffect, useRef } from 'react';
import { Slide } from '@/utils/slide-types';
import { cn } from '@/utils/cn';
import { SlideComponent } from './slides/slide-component';

interface SlideThumbnailBarProps {
  slides: readonly Slide[];
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
    <div className="flex overflow-x-scroll overflow-y-visible pt-1 pb-4 px-1 gap-6 -ml-1">
      {slides.map((slide, index) => (
        <div className={cn('rounded-lg flex-none overflow-hidden w-[192px] ring-1 ring-foreground/30', slide.id === currentSlideID && 'ring-2 ring-primary-500')}>
        <div
          key={slide.id}
          ref={(el) => (thumbnailRefs.current[index] = el)}
          className={"flex-none"}
          onClick={!blockSlideSwitching ? () => setCurrentSlideID(slide.id) : undefined}
          style={{ width: '192px', height: '108px', transform: 'scale(0.15)', transformOrigin: 'top left' }}
        >
          <div className="w-[1280px] h-[720px]">
          <div className="flex flex-none text-foreground bg-foreground/5 w-full aspect-video box-border shadow-lg">
            <SlideComponent 
              slide={slide} 
              viewOnly={true} 
              thumbnail={true}
            />
            </div>
          </div>
        </div>
        </div>
      ))}
    </div>
  );
}
