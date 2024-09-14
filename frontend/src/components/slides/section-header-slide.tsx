// section-header-slide.tsx
import { SectionHeaderSlide, Slide } from "@shared-utils/database-types";
import { SlideImage } from "@/components/slides/image/editable-slide-image";
import { useState } from "react";
import { EditableTitle } from "@/components/slides/editable-title";

type SectionHeaderSlideComponentProps = {
  slide: SectionHeaderSlide;
  setSlide: (slide: Partial<Slide>) => void;
  presentationID: string;
  setBlockArrowKeys: (block: boolean) => void;
};

export function SectionHeaderSlideComponent({
  slide,
  presentationID,
  setSlide,
  setBlockArrowKeys,
}: SectionHeaderSlideComponentProps) {
  const [loading, setLoading] = useState(false);

  const saveSlide = async (newTitle: string) => {
    setLoading(true);
    setSlide({
      slide_title: newTitle,
    });
    setLoading(false);
  };

  const isImageLeft = slide.image_position !== "right"; // Defaults to left if image_position is undefined or any other value except 'right'

  return (
    <div className="flex flex-row relative overflow-visible aspect-video w-full">
      {isImageLeft ? (
        <>
          <div className="aspect-square h-full">
            <SlideImage
              setSlide={setSlide}
              presentationID={presentationID}
              image={slide.image}
              variant={slide.image_position}
            />
          </div>
          <div className="flex-auto flex flex-col justify-center p-12">
            <EditableTitle
              title={slide.slide_title}
              onSave={saveSlide}
              loading={loading}
              setBlockArrowKeys={setBlockArrowKeys}
            />
          </div>
        </>
      ) : (
        <>
          <div className="flex-auto flex flex-col justify-center p-12">
            <EditableTitle
              title={slide.slide_title}
              onSave={saveSlide}
              loading={loading}
              setBlockArrowKeys={setBlockArrowKeys}
            />
          </div>
          <div className="aspect-square h-full">
            <SlideImage
              setSlide={setSlide}
              presentationID={presentationID}
              image={slide.image}
              variant={slide.image_position}
            />
          </div>
        </>
      )}
    </div>
  );
}
