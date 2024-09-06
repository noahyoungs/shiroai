// frontend/src/components/slides/view-only/view-only-short-bullets-slide-pills.tsx
import { ShortBulletsSlide, IconData } from "../../../utils/db-types";
import { Icon } from "@iconify/react";
import React from "react";
import { cn } from "../../../utils/cn";
import { ViewOnlyTitle } from "./view-only-title";

type BulletItemProps = {
  content: string;
  excerptText?: string | null;
  source?: any;
  icon: IconData;
  chevron?: boolean;
  allBulletsShort?: boolean;
  index: number;
  slide: ShortBulletsSlide;
};

const BulletItem: React.FC<BulletItemProps> = ({
  content,
  excerptText,
  source,
  icon,
  chevron,
  allBulletsShort,
  index,
  slide,
}) => {
  return (
    <li className="relative">
      <div
        className={cn(
          "flex items-center justify-between bg-background rounded-full py-1.5 pl-1.5 pr-6"
        )}
      >
        <div className="flex flex-row flex-grow items-center">
          <div className="flex flex-none items-center justify-center h-12 w-12 bg-blue-500 rounded-full text-white font-light overflow-hidden">
            <Icon
              className="text-[33px]"
              icon={
                !icon
                  ? "tabler:file-unknown"
                  : icon.source === "fluent"
                  ? `fluent-emoji-high-contrast:${icon.name}`
                  : `tabler:${icon.name}`
              }
            />
          </div>
          <span className="text-foreground pl-4 text-base font-[550]">
            {content}
          </span>
        </div>
      </div>
      {chevron && (
        <div
          className={cn("absolute -translate-y-1", "right-1/2 translate-x-1/2")}
        >
          <Icon
            icon="tabler:chevron-compact-down"
            className="text-foreground/60 text-[33px]"
          />
        </div>
      )}
    </li>
  );
};

export function ViewOnlyPillShortBulletsSlideComponent({
  slide,
  allSources,
}: {
  slide: ShortBulletsSlide;
  allSources?: any[];
}) {
  const allBulletsShort = slide.slide_content.every(
    (bullet) => bullet.content.length <= 50
  );

  return (
    <div className="p-12 w-full flex-grow flex flex-col">
      {allBulletsShort ? (
        <div className="flex flex-row w-full h-full px-24">
          <div className="w-1/3 flex items-center justify-center">
            <ViewOnlyTitle title={slide.slide_title} />
          </div>
          <div className="w-2/3 flex justify-center flex-grow">
            <ul className="flex flex-col justify-center gap-6 h-full max-w-max">
              {slide.slide_content.map((bullet, index) => (
                <React.Fragment key={bullet.id}>
                  <BulletItem
                    content={bullet.content}
                    excerptText={bullet.excerpt?.text}
                    source={
                      allSources &&
                      allSources.find(
                        (source) => source.id === bullet.excerpt?.source_id
                      )
                    }
                    icon={bullet.icon}
                    chevron={
                      slide.sequential &&
                      index != slide.slide_content.length - 1
                    }
                    allBulletsShort={allBulletsShort}
                    index={index}
                    slide={slide}
                  />
                </React.Fragment>
              ))}
            </ul>
          </div>
        </div>
      ) : (
        <>
          <div className="flex-none w-full">
            <ViewOnlyTitle title={slide.slide_title} />
          </div>
          <div className="flex justify-center w-full flex-grow">
            <ul className="flex flex-col justify-evenly gap-6 max-w-max my-8">
              {slide.slide_content.map((bullet, index) => (
                <React.Fragment key={bullet.id}>
                  <BulletItem
                    content={bullet.content}
                    excerptText={bullet.excerpt?.text}
                    source={
                      allSources &&
                      allSources.find(
                        (source) => source.id === bullet.excerpt?.source_id
                      )
                    }
                    icon={bullet.icon}
                    chevron={
                      slide.sequential &&
                      index != slide.slide_content.length - 1
                    }
                    allBulletsShort={allBulletsShort}
                    index={index}
                    slide={slide}
                  />
                </React.Fragment>
              ))}
            </ul>
          </div>
        </>
      )}
    </div>
  );
}
