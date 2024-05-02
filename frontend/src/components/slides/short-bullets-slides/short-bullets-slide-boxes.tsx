import { ShortBulletsSlide } from "@/utils/slide-types";
import { Tooltip } from "@nextui-org/react";
import { ExcerptCard } from "@/components/excerpt-card";
import { Icon } from "@iconify/react";
import React from "react";
import { Noto_Emoji } from 'next/font/google';
import { cn } from "@/utils/cn";

type ShortBulletsSlideComponentProps = {
  slide: ShortBulletsSlide;
  allSources: any[];
};

const noto_emoji = Noto_Emoji({
  subsets: ['emoji'],
  variable: "--font-noto-emoji",
  display: "swap",
});

export function BoxesShortBulletsSlideComponent({ slide, allSources }: ShortBulletsSlideComponentProps) {
  let icons = ["tabler:bed", "tabler:clock", "fluent-emoji:automobile", "fluent-emoji:vertical-traffic-light", "fluent-emoji:sos-button", "fluent-emoji:flag-japan"]
  return (
    <div className="mt-8 p-12 flex flex-col relative overflow-hidden height-auto bg-foreground/5 dark:bg-foreground/10 text-foreground box-border bg-content1 outline-none shadow-medium rounded-large w-full aspect-video flex-none">
      <div className="flex justify-center w-full h-full">
        {slide.slide_content.slice(0, 5).length == 4 && <h1 className="self-start my-auto mr-16 w-[40%]">{slide.slide_title}</h1>}
        <div className={cn("grid grid-rows-2 gap-8 h-full", slide.slide_content.slice(0, 5).length != 4 ? "grid-cols-3" : "grid-cols-2")}>
          {slide.slide_content.slice(0, 5).length != 4 && <h1 className="self-start my-auto mr-8">{slide.slide_title}</h1>}
          {slide.slide_content.slice(0, 5).length != 4 && Array.from({ length: 5 - slide.slide_content.slice(0, 5).length }, (_, index) => (
            <div key={index}></div> // Empty div to keep the grid layout
          ))}
          {slide.slide_content.slice(0, 5).map((bullet, index) => (
            <Tooltip
              content={<ExcerptCard text={bullet.excerpt.text} source={allSources.find((source) => source.id === bullet.excerpt.source_id)} />}
              placement="bottom"
              showArrow
              className="items-start p-4"
            >
              <div key={index} className="relative flex flex-col items-start bg-background rounded-3xl p-6 h-full w-full justify-between">
                <div className="flex items-center justify-center h-16 w-16 bg-blue-500 rounded-full text-white font-light overflow-hidden mb-4 flex-shrink-0">
                  <Icon className="text-[33px]" icon={icons[index]} />
                </div>
                <div className="text-start overflow-hidden flex-none">
                  {bullet.content.includes(":") ? (
                    <>
                      {bullet.content.split(":").map((part, index) => (
                        <p
                          key={index}
                          className={cn(
                            "text-foreground font-[550] overflow-hidden text-ellipsis mb-1",
                            index === 0 ? "text-lg leading-tight" : "text-sm font-normal"
                          )}
                          style={{
                            display: "-webkit-box",
                            WebkitLineClamp: index === 0 ? 2 : 3,
                            WebkitBoxOrient: "vertical",
                          }}
                        >
                          {part.trim()}
                        </p>
                      ))}
                    </>
                  ) : (
                    <p
                      className="text-foreground text-lg font-[550] overflow-hidden text-ellipsis"
                      style={{
                        display: "-webkit-box",
                        WebkitLineClamp: 3,
                        WebkitBoxOrient: "vertical",
                      }}
                    >
                      {bullet.content}
                    </p>
                  )
                  }
                  {slide.sequential && index !== slide.slide_content.length - 1 && (
                    <div className="absolute top-1/2 -right-8 -translate-y-[16.5px]">
                      <Icon className="text-[33px] text-foreground/70 " icon="tabler:chevron-compact-right" />
                    </div>
                  )}
                </div>
              </div>
            </Tooltip>
          ))}
        </div>
      </div>
    </div>
  );
}