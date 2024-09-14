import { ShortBulletsSlide } from "@shared-utils/database-types";
import React from "react";
import { Icon } from '@iconify-icon/react';
import { cn } from "@shared-utils/cn";
import { ViewOnlyTitle } from "./view-only-title";

type BulletItemProps = {
  bullet: any;
  index: number;
  allSources?: any[];
  slide: ShortBulletsSlide;
};

const BulletItem: React.FC<BulletItemProps> = ({ bullet, index, allSources, slide }) => {
  return (
    <div
      key={index}
      className={cn(
        "relative flex flex-col items-start bg-white dark:bg-black nobg:ring-1 nobg:ring-black rounded-3xl p-6 h-full w-full justify-between"
      )}
    >
      <div className="flex items-center justify-center h-14 w-14 bg-blue-500 rounded-full text-white font-light overflow-hidden flex-shrink-0">
        <Icon
          icon={
            !bullet.icon
              ? "tabler:file-unknown"
              : bullet.icon.source === "fluent"
              ? `fluent-emoji-high-contrast:${bullet.icon.name}`
              : `tabler:${bullet.icon.name}`
          }
          // @ts-ignore
          class="text-[33px]"
        />
      </div>
      <div className="text-start flex-none">
        {bullet.content.includes(":") ? (
          <>
            {bullet.content
              .split(":")
              .map((part: string, partIndex: number) => (
                <p
                  key={String(partIndex)}
                  className={cn(
                    "text-foreground font-[550] overflow-hidden text-ellipsis mb-1",
                    partIndex === 0
                      ? "text-lg leading-tight"
                      : "text-sm font-normal"
                  )}
                  style={{
                    display: "-webkit-box",
                    WebkitLineClamp: partIndex === 0 ? 2 : 3,
                    WebkitBoxOrient: "vertical",
                  }}
                >
                  {part.trim()}
                </p>
              ))}
          </>
        ) : (
          <p
            className="text-foreground text-lg font-[550] leading-tight"
            style={{
              display: "-webkit-box",
              WebkitLineClamp: 4,
              WebkitBoxOrient: "vertical",
            }}
          >
            {bullet.content}
          </p>
        )}
        {slide.sequential && index !== slide.slide_content.length - 1 && (
          <div className="absolute top-1/2 -right-8 -translate-y-[16.5px]">
            <Icon
              // @ts-ignore
              class="text-[33px] text-black/70 dark:text-white/70"
              icon="tabler:chevron-compact-right"
            />
          </div>
        )}
      </div>
    </div>
  );
};

const renderSlideContent = (
  slide: ShortBulletsSlide,
  allSources: any[] | undefined
) => {
  switch (slide.slide_content.length) {
    case 2:
      return (
        <div className="grid grid-rows-2 gap-8 h-full">
          <div className="row-span-1 col-span-full my-auto">
            <ViewOnlyTitle
              title={slide.slide_title}
            />
          </div>
          <div className="grid grid-cols-2 gap-8 h-full row-span-1">
            {slide.slide_content.map((bullet, index) => (
              <BulletItem
                key={bullet.id}
                bullet={bullet}
                index={index}
                allSources={allSources}
                slide={slide}
              />
            ))}
          </div>
        </div>
      );
    case 3:
      return (
        <div className="grid grid-rows-2 gap-8 h-full">
          <div className="row-span-1 col-span-full my-auto">
            <ViewOnlyTitle
              title={slide.slide_title}
            />
          </div>
          <div className="grid grid-cols-3 gap-8 h-full row-span-1">
            {slide.slide_content.map((bullet, index) => (
              <BulletItem
                key={bullet.id}
                bullet={bullet}
                index={index}
                allSources={allSources}
                slide={slide}
              />
            ))}
          </div>
        </div>
      );
    case 4:
      return (
        <div className="grid grid-cols-3 gap-8 h-full">
          <div className="col-span-1 flex flex-col justify-center">
            <ViewOnlyTitle
              title={slide.slide_title}
            />
          </div>
          <div className="col-span-2 grid grid-cols-2 grid-rows-2 gap-8">
            {slide.slide_content.map((bullet, index) => (
              <BulletItem
                key={bullet.id}
                bullet={bullet}
                index={index}
                allSources={allSources}
                slide={slide}
              />
            ))}
          </div>
        </div>
      );
    case 5:
      return (
        <div className="grid grid-rows-2 grid-cols-3 gap-8 h-full">
          <div className="col-span-1 row-span-1 my-auto">
            <ViewOnlyTitle
              title={slide.slide_title}
            />
          </div>
          {slide.slide_content.map((bullet, index) => (
            <BulletItem
              key={bullet.id}
              bullet={bullet}
              index={index}
              allSources={allSources}
              slide={slide}
            />
          ))}
        </div>
      );
    default:
      return null;
  }
};

type ShortBulletsSlideComponentProps = {
  slide: ShortBulletsSlide;
  allSources?: any[];
};

export const ViewOnlyBoxesShortBulletsSlideComponent: React.FC<
  ShortBulletsSlideComponentProps
> = ({ slide, allSources }) => {
  const testSlideContent = slide.slide_content.slice(0, 5);

  return (
    <div className="p-12 w-full h-full">
      <div className="flex justify-center w-full h-full">
        {renderSlideContent(
          { ...slide, slide_content: testSlideContent },
          allSources
        )}
      </div>
    </div>
  );
};
