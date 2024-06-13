import { SectionHeaderSlide } from "@/utils/slide-types";
import { SlideImage } from "@/components/slides/slide-image";
import { useState } from "react";
import { updateSlide } from "@/actions/slides-actions";
import { EditableTitle } from "@/components/slides/editable-title";

type SectionHeaderSlideComponentProps = {
  slide: SectionHeaderSlide;
  presentationID: string;
  fetchSlide: (slideID: string) => void;
  setBlockArrowKeys: (block: boolean) => void;
};

export function SectionHeaderSlideComponent({
  slide,
  presentationID,
  fetchSlide,
  setBlockArrowKeys,
}: SectionHeaderSlideComponentProps) {
  const [loading, setLoading] = useState(false);

  const saveSlide = async (newTitle: string) => {
    setLoading(true);
    await updateSlide(presentationID, {
      ...slide,
      slide_title: newTitle,
    });
    await fetchSlide(slide.id);
    setLoading(false);
  };

  const isImageLeft = slide.image_position !== "right"; // Defaults to left if image_position is undefined or any other value except 'right'

  return (
    <div className="flex flex-row relative overflow-hidden height-auto bg-foreground/5 text-foreground box-border bg-content1 outline-none shadow-medium rounded-large w-full aspect-video flex-none">
      {isImageLeft ? (
        <>
          <div className="aspect-square h-full">
            <SlideImage image={slide.image} />
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
            <SlideImage image={slide.image} />
          </div>
        </>
      )}
    </div>
  );
}
