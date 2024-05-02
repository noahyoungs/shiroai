import { ShortBulletsSlide } from "@/utils/slide-types";
import { Tooltip } from "@nextui-org/react";
import { ExcerptCard } from "@/components/excerpt-card";
import { Icon } from "@iconify/react";
import React from "react";
import { Noto_Emoji } from 'next/font/google'
import { cn } from "@/utils/cn";

type ShortBulletsSlideComponentProps = {
  slide: ShortBulletsSlide;
  allSources?: any[];
};

const noto_emoji = Noto_Emoji({
  subsets: ['emoji'],
  variable: "--font-noto-emoji",
  display: "swap",
})

function BulletComponent({ content, excerptText, source, icon, chevron }: { content: string, excerptText: string, source?: any, icon: string, chevron?: boolean }) {
  return (
    <li>
      <div className="flex items-center bg-background rounded-full py-2 pl-2 pr-6">
        <div className="flex items-center justify-center h-12 w-12 bg-blue-500 rounded-full text-white font-light overflow-hidden">
          {
            <Icon className="text-[33px]" icon={icon} />
          }
        </div>
        <span className="text-foreground pl-4 text-base font-[550]">{content}</span>
        {source && (
          <Tooltip
            content={<ExcerptCard text={excerptText} source={source} />}
            placement="bottom"
            showArrow
            className="items-start p-4"
          >
            <div className="inline-block ml-2 text-primary cursor-pointer">
                    <Icon icon="tabler:input-search" width="20" height="20" />
                </div>
          </Tooltip>
        )}
      </div>
      {chevron && (
        <div className="absolute right-1/2 -translate-y-1">
          <Icon icon="tabler:chevron-compact-down" className="text-foreground/60 text-[33px]" />
        </div>
      )}
    </li>
  );
}

export function PillShortBulletsSlideComponent({ slide, allSources }: ShortBulletsSlideComponentProps) {
  // let icons = ["fluent-emoji:dog", "fluent-emoji:cooking", "fluent-emoji:automobile", "fluent-emoji:vertical-traffic-light", "fluent-emoji:sos-button", "fluent-emoji:flag-japan"]
  let icons = ["tabler:bed", "tabler:clock", "fluent-emoji-high-contrast:automobile", "fluent-emoji-high-contrast:vertical-traffic-light", "fluent-emoji-high-contrast:sos-button", "fluent-emoji-high-contrast:flag-japan"]

  let iconTexts= ["🐕", "🍳", "🚗", "🚦", "🆘", "🇯🇵"]

  return (
    <div className="p-12 flex flex-col relative overflow-hidden height-auto bg-foreground/5 dark:bg-foreground/10 text-foreground box-border bg-content1 outline-none shadow-medium rounded-large w-full aspect-video flex-none">
      <h1 className="self-start">{slide.slide_title}</h1>
      <div className="flex justify-center w-full flex-grow">
        <ul className="flex flex-col justify-center gap-6 h-full max-w-max">
          {slide.slide_content.map((bullet, index) => (
            <React.Fragment key={index}>
              <BulletComponent
                content={bullet.content}
                excerptText={bullet.excerpt.text}
                source={allSources && allSources.find((source) => source.id === bullet.excerpt.source_id)}
                icon={icons[index] || icons[0]}
                chevron={slide.sequential && index != slide.slide_content.length - 1}
              />
            </React.Fragment>
          ))}
        </ul>
      </div>
    </div>
  );
}