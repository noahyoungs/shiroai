//long-bullets-slide.tsx
import { LongBulletsSlide } from "@/utils/slide-types";
import Markdown, { RuleType } from "markdown-to-jsx";
import "@/components/mdx-editor/styles.css";
import { cn } from "@/utils/cn";
import { Footnote } from "@/components/footnote";

type LongBulletsSlideComponentProps = {
  slide: LongBulletsSlide;
  allSources?: any[];
  proseClass: string;
};

export function StaticLongBulletsSlideComponent({
  slide,
  allSources,
  proseClass = "prose-2xl",
}: LongBulletsSlideComponentProps) {
  let cleanedMarkdown = "";
  if (slide.slide_content && slide.slide_content.content) {
    // console.log("Before: ", slide.slide_content.content);

    let escaped = slide.slide_content.content.replace(/\\\[/g, "[");

    // Find all footnotes and replace them
    const regex = /(_.*?_|\b)(\[\^(\d+)\](?:\s*\[\^(\d+)\])*)/g;
    cleanedMarkdown = escaped.replace(regex, (match, prefix, fullMatch) => {
      const footnotes = fullMatch.match(/\[\^(\d+)\]/g);
      if (footnotes) {
        const uniqueFootnotes = [...new Set(footnotes)];
        const footnoteNumbers = uniqueFootnotes.map(
          (footnote) => footnote.match(/\d+/)[0]
        );
        const combinedFootnote = `[^${footnoteNumbers.join(",^")}]`;
        return prefix + combinedFootnote;
      }
      return match;
    });
  }

  return (
    <div className="p-12 pb-0 flex flex-col relative text-foreground dark:bg-foreground/10 bg-foreground/5 box-border bg-content1 outline-none shadow-medium rounded-large w-full flex-none aspect-video overflow-scroll">
      <div className="flex-none">
        <div className="border-b-medium border-transparent rounded-none">
          <div
            className={
              "pb-[8px] box-border text-4xl font-bold [overflow-wrap:anywhere]"
            }
          >
            {slide.slide_title}
          </div>
        </div>
      </div>

      <div className="flex-auto"></div>
      <div
        className={cn(
          "flex justify-center w-full flex-shrink max-w-none prose",
          proseClass
        )}
      >
        <Markdown
          options={{
            renderRule(next, node, renderChildren, state) {
              if (node.type === RuleType.footnoteReference) {
                // console.log(node);
                const footnoteKeys = node.text.split(",^");
                // console.log("footnoteKeys:", footnoteKeys);
                return (
                  <Footnote
                    footnoteKeys={footnoteKeys}
                    slide={slide}
                    allSources={allSources}
                  />
                );
              }
              return next();
            },
          }}
        >
          {cleanedMarkdown}
        </Markdown>
      </div>
      <div className="flex-auto"></div>
    </div>
  );
}
