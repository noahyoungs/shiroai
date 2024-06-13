import { Tooltip } from "@nextui-org/react";
import { Icon } from "@iconify/react";
import { ExcerptCard } from "@/components/excerpt-card";
import { useState } from "react";
import { Slide } from "@/utils/slide-types";

type FootnoteProps = {
  footnoteKeys: string[];
  slide: Slide;
  allSources?: any[];
};

export function Footnote({ footnoteKeys, slide, allSources }: FootnoteProps) {
  const [currentIndex, setCurrentIndex] = useState(0);

  if (!slide.slide_content.footnotes) return null;

  const excerpts = footnoteKeys.map(
    (key) => slide.slide_content.footnotes[Number(key)]
  );

  const currentExcerpt = excerpts[currentIndex];

  const handlePrev = () => {
    if (currentIndex > 0) {
      setCurrentIndex(currentIndex - 1);
    }
  };

  const handleNext = () => {
    if (currentIndex < excerpts.length - 1) {
      setCurrentIndex(currentIndex + 1);
    }
  };

  return (
    <>
      {allSources && (
        <Tooltip
          content={
            <>
              <h3 className="text-left text-lg">
                {excerpts.length > 1
                  ? `Source ${currentIndex + 1} of ${excerpts.length}`
                  : "Source"}
              </h3>
              <div className="flex flex-col gap-4 items-center">
                {excerpts.length > 1 && (
                  <div className="flex items-center justify-between w-full">
                    <Icon
                      icon="tabler:chevron-compact-left"
                      width="32"
                      height="32"
                      className={
                        currentIndex === 0
                          ? "text-foreground/30"
                          : "text-foreground/80  hover:text-foreground cursor-pointer"
                      }
                      onClick={handlePrev}
                    />
                    <ExcerptCard
                      key={currentIndex}
                      text={currentExcerpt?.text || ""}
                      source={allSources.find(
                        (source) => source.id === currentExcerpt?.source_id
                      )}
                    />
                    <Icon
                      icon="tabler:chevron-compact-right"
                      width="32"
                      height="32"
                      className={
                        currentIndex === excerpts.length - 1
                          ? "text-foreground/30"
                          : "text-foreground/80 hover:text-foreground cursor-pointer"
                      }
                      onClick={handleNext}
                    />
                  </div>
                )}
                {excerpts.length === 1 && (
                  <ExcerptCard
                    key={currentIndex}
                    text={currentExcerpt?.text || ""}
                    source={allSources.find(
                      (source) => source.id === currentExcerpt?.source_id
                    )}
                  />
                )}
              </div>
            </>
          }
          placement="bottom"
          showArrow
          className="items-start p-4 footnote-container"
        >
          <div className="px-1 text-primary inline-block align-middle">
            <Icon icon="tabler:input-search" width="20" height="20" />
          </div>
        </Tooltip>
      )}
    </>
  );
}
