// SlideThumbnail.tsx

import React, { useRef, useEffect, useState } from 'react';
import html2canvas from 'html2canvas';
import { renderToStaticMarkup } from 'react-dom/server';
import { Slide } from '@/utils/slide-types';
import { SlideComponent } from '@/components/slides/slide-component';
import { cn } from '@/utils/cn';

interface SlideThumbnailProps {
  slide: Slide;
  selected: boolean;
  onClick: () => void;
}

export function SlideThumbnail({ slide, selected, onClick }: SlideThumbnailProps) {
  const thumbnailRef = useRef<HTMLDivElement>(null);
  const [thumbnailUrl, setThumbnailUrl] = useState<string | null>(null);

  useEffect(() => {
    const captureThumbnail = async () => {
      const canvas = document.createElement('canvas');
      canvas.width = 1280;
      canvas.height = 720;

      const slideContainer = document.createElement('div');
      slideContainer.style.width = '1280px';
      slideContainer.style.height = '720px';
      slideContainer.style.position = 'absolute';
      slideContainer.style.left = '-9999px';
      document.body.appendChild(slideContainer);

      const slideHtml = renderToStaticMarkup(<SlideComponent slide={slide} />);
      slideContainer.innerHTML = slideHtml;

      const slideCanvas = await html2canvas(slideContainer);
      const thumbnailUrl = slideCanvas.toDataURL("image/webp", 0.1);

      document.body.removeChild(slideContainer);

      setThumbnailUrl(thumbnailUrl);
    };

    captureThumbnail();
  }, [slide]);

  return (
    <div
      className={cn('w-[128px] rounded-lg overflow-hidden flex-none aspect-video m-2 cursor-pointer', selected ? 'border-blue-500 border-2' : 'border-gray-300 border')}
      onClick={onClick}
    >
      {thumbnailUrl && (
        <img src={thumbnailUrl} alt={slide.slide_title} className="w-full h-full object-cover" />
      )}
    </div>
  );
}