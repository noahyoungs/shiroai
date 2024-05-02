//long-bullets-slide.tsx
import { LongBulletsSlide } from "@/utils/slide-types";
import Markdown from "markdown-to-jsx";
import { ExcerptCard } from "@/components/excerpt-card";
import { Tooltip, Skeleton } from "@nextui-org/react";
import { Icon } from "@iconify/react";
import { ForwardRefEditor } from "../mdx-editor/ForwardRefEditor";
import "@mdxeditor/editor/style.css";
import "@/components/mdx-editor/styles.css";
import { useState, useRef } from "react";
import { MDXEditorMethods } from "@mdxeditor/editor";
import { EditableTitle } from "./editable-title";
import { updateSlide } from "@/actions/slides-actions";

type LongBulletsSlideComponentProps = {
  slide: LongBulletsSlide;
  allSources?: any[];
  fetchSlide: (slideID: string) => void;
  presentationID: string;
};

export function LongBulletsSlideComponent({
  slide,
  allSources,
  fetchSlide,
  presentationID,
}: LongBulletsSlideComponentProps) {
  type FootnoteProps = {
    number: string;
    children: string;
  };

  function Footnote({ children }: FootnoteProps) {
    const excerpt = slide.slide_content.footnotes[children];
    return (
      allSources && (
        <Tooltip
          content={
            <ExcerptCard
              text={excerpt.text}
              source={allSources.find(
                (source) => source.id === excerpt.source_id
              )}
            />
          }
          placement="bottom"
          showArrow
          className="items-start p-4"
        >
          <div className="inline-block px-1 text-primary">
            <Icon icon="tabler:input-search" width="20" height="20" />
          </div>
        </Tooltip>
      )
    );
  }

  const [editingMarkdown, setEditingMarkdown] = useState(false);
  const [titleLoading, setTitleLoading] = useState(false);
  const [markdownLoading, setMarkdownLoading] = useState(false);

  const ref = useRef<MDXEditorMethods>(null);

  // for title
  const saveSlideTitle = async (newTitle: string) => {
    setTitleLoading(true);
    await updateSlide(presentationID, {
      ...slide,
      slide_title: newTitle,
    });
    await fetchSlide(slide.id);
    setTitleLoading(false);
  };

  const saveSlideMarkdown = async () => {
    if (!ref.current) return;
    setEditingMarkdown(false);
    setMarkdownLoading(true);
    await updateSlide(presentationID, {
      ...slide,
      slide_content: {
        ...slide.slide_content,
        content: ref.current?.getMarkdown(),
      },
    });
    await fetchSlide(slide.id);
    setMarkdownLoading(false);
  };

  return (
    <div className="p-12 pb-0 flex flex-col relative overflow-hidden height-auto text-foreground dark:bg-foreground/10 bg-foreground/5 box-border bg-content1 outline-none shadow-medium rounded-large w-full aspect-video flex-none">
      {/* <h1 className="self-start mb-0">{slide.slide_title}</h1> */}
      <EditableTitle
        title={slide.slide_title}
        onSave={saveSlideTitle}
        loading={titleLoading}
      />
      {editingMarkdown ? (
        <div className="slide-markdown relative border-[1.8px] border-black rounded-medium">
          <ForwardRefEditor
            ref={ref}
            markdown={slide.slide_content.content}
            onChange={console.log}
            saveSlideMarkdown={saveSlideMarkdown}
          />
        </div>
      ) : (
        <>
          <div className="flex-auto"></div>
          <div className="flex justify-center w-full flex-none slide-markdown">
            <Skeleton isLoaded={!markdownLoading}>
              <Markdown
                options={{
                  overrides: {
                    sup: {
                      component: Footnote,
                      props: {},
                    },
                  },
                }}
                onClick={() => setEditingMarkdown(true)}
              >
                {slide.slide_content.content}
              </Markdown>
            </Skeleton>
          </div>
          <div className="flex-auto"></div>
        </>
      )}
    </div>
  );
}
