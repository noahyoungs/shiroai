// presentation-title-slide.tsx
import { PresentationTitleSlide, Slide } from "@/utils/slide-types";
import { SlideImage } from "./image/editable-slide-image";
import { EditableTitle } from "@/components/slides/editable-title";
import { useState } from "react";

type PresentationTitleSlideComponentProps = {
  slide: PresentationTitleSlide;
  setSlide: (slide: Partial<Slide>) => void;
  presentationID: string;
  setBlockArrowKeys: (block: boolean) => void;
};

export function PresentationTitleSlideComponent({
  slide,
  presentationID,
  setSlide,
  setBlockArrowKeys,
}: PresentationTitleSlideComponentProps) {
  const [loading, setLoading] = useState(false);

  const saveSlide = async (newTitle: string) => {
    setLoading(true);
    setSlide({
      slide_title: newTitle,
    });
    setLoading(false);
  };

  return (
    <div className="h-full m-0">
      <div className="absolute mx-12 mb-3 bottom-10 z-[21] text-background/90 cursor-text w-[90%]" id="presentation-title">
        <EditableTitle
          title={slide.slide_title}
          onSave={saveSlide}
          loading={loading}
          setBlockArrowKeys={setBlockArrowKeys}
          classNames="!text-text-background/90"
        />
      </div>
      <SlideImage presentationID={presentationID} setSlide={setSlide} image={slide.image} variant="full"/>
    </div>
  );
}
