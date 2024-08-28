// frontend/src/components/slides/view-only/view-only-markdown-slide.tsx
"use client";
import Markdown, { RuleType } from "markdown-to-jsx";
import { ViewOnlyTitle } from "./view-only-title";
import { cn } from "../utils/cn";
import React from "react";
import { MarkdownSlide } from "../utils/slide-types";

type ViewOnlyMarkdownSlideComponentProps = {
  slide: MarkdownSlide;
  allSources?: any[];
};

export function ViewOnlyMarkdownSlideComponent({
  slide,
  allSources,
}: ViewOnlyMarkdownSlideComponentProps) {

  return (
    <div className="p-12 pb-0 flex flex-col w-full h-full">
      <div className="flex-none">
        <ViewOnlyTitle
          title={slide.slide_title}
        />
      </div>
      <>
        <div className="flex-auto min-h-6"></div>
        <div
          className={cn(
            "flex justify-start w-full flex-shrink max-w-none prose dark:prose-invert",
            slide.slide_content.prose_class || "prose-sm"
          )}
        >
            {typeof slide.slide_content.content === "string" ? (
              <Markdown
                options={{
                  renderRule(next, node, renderChildren, state) {
                    // @ts-ignore
                    if (node.type === RuleType.footnoteReference) {
                      // const footnoteKeys = node.text.split(",^");
                      return (
                        // <Footnote
                        //   footnoteKeys={footnoteKeys}
                        //   slide={slide}
                        //   allSources={allSources}
                        // />
                        <span></span>
                      );
                    }
                    return next();
                  },
                  wrapper: ({ children }) => (
                    <div id="prose-container" className="px-1">
                      {children}
                    </div>
                  ),
                  forceWrapper: true,
                }}
              >
                {slide.slide_content.content}
              </Markdown>
            ) : (
              <div className="flex justify-center items-center h-[300px]">
                <p className="text-center text-foreground dark:text-background">
                  Error: Slide content is not a string <br />
                  Slide content is {typeof slide.slide_content.content} <br />
                  Slide content is{" "}
                  {JSON.stringify(slide.slide_content.content)}
                </p>
              </div>
            )}
        </div>
        <div className="flex-auto min-h-12"></div>
      </>
    </div>
  );
}
