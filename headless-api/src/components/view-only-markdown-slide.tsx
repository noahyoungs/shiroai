"use client";
import Markdown, { RuleType } from "markdown-to-jsx";
import { ViewOnlyTitle } from "./view-only-title";
import { cn } from "@shared-utils/cn";
import { MarkdownSlide } from "@shared-utils/database-types";
import React from "react";

type ViewOnlyMarkdownSlideComponentProps = {
  slide: MarkdownSlide;
  allSources?: any[];
};

export function ViewOnlyMarkdownSlideComponent({
  slide,
  allSources,
}: ViewOnlyMarkdownSlideComponentProps) {
  // Check if the markdown content has a table using a regular expression
  const markdownContent = slide.slide_content.content;
  const hasTable = typeof markdownContent === "string" && /\|.*\|/.test(markdownContent);

  return (
    <div className="p-12 pb-0 flex flex-col w-full h-full">
      <div className="flex-none">
        <ViewOnlyTitle title={slide.slide_title} />
      </div>
      <>
        <div className="flex-auto min-h-6"></div>
        <div
          className={cn(
            "flex w-full flex-shrink max-w-none prose dark:prose-invert",
            hasTable ? "justify-center" : "justify-start", // Conditionally apply the justify-center class
            slide.slide_content.prose_class || "prose-sm"
          )}
        >
          {typeof markdownContent === "string" ? (
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
              {markdownContent}
            </Markdown>
          ) : (
            <div className="flex justify-center items-center h-[300px]">
              <p className="text-center text-foreground dark:text-background">
                Error: Slide content is not a string <br />
                Slide content is {typeof markdownContent} <br />
                Slide content is{" "}
                {JSON.stringify(markdownContent)}
              </p>
            </div>
          )}
        </div>
        <div className="flex-auto min-h-12"></div>
      </>
    </div>
  );
}