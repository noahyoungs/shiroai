//markdown-slide.tsx
"use client";
import Markdown, { RuleType } from "markdown-to-jsx";
import { Tooltip, Skeleton } from "@nextui-org/react";
import { Icon } from "@iconify/react";
import { ForwardRefEditor } from "../mdx-editor/ForwardRefEditor";
import "@mdxeditor/editor/style.css";
import "@/components/mdx-editor/styles.css";
import { useState, useRef, useEffect } from "react";
import { EditableTitle } from "./editable-title";
import { updateSlide } from "@/actions/slides-actions";
import {
  UndoRedo,
  BoldItalicUnderlineToggles,
  ButtonWithTooltip,
  ListsToggle,
  type MDXEditorMethods,
  InsertTable,
} from "@mdxeditor/editor";
import { cn } from "@/utils/cn";
import { Footnote } from "@/components/footnote";
import React from "react";
import { MarkdownSlide } from "@/utils/slide-types";


type MarkdownSlideComponentProps = {
  slide: MarkdownSlide;
  allSources?: any[];
  fetchSlide: (slideID: string) => void;
  presentationID: string;
  setBlockArrowKeys: (block: boolean) => void;
};

export function MarkdownSlideComponent({
  slide,
  allSources,
  fetchSlide,
  presentationID,
  setBlockArrowKeys,
}: MarkdownSlideComponentProps) {
  const [editingMarkdown, setEditingMarkdown] = useState(false);
  const [titleLoading, setTitleLoading] = useState(false);
  const [markdownLoading, setMarkdownLoading] = useState(false);
  const editorRef = useRef<MDXEditorMethods>(null);

  useEffect(() => {
    setBlockArrowKeys(editingMarkdown);
  }, [editingMarkdown, setBlockArrowKeys]);

  // for title
  const saveSlideTitle = async (newTitle: string) => {
    setTitleLoading(true);
    await updateSlide(presentationID, {
      id: slide.id,
      slide_title: newTitle,
    });
    await fetchSlide(slide.id);
    setTitleLoading(false);
  };

  // for markdown
  const saveSlideMarkdown = async () => {
    if (!editorRef.current) return;
    if (editorRef.current?.getMarkdown().trim() === '') {
      alert("Slide content cannot be empty");
      return;
    }
    setEditingMarkdown(false);
    // if (editorRef.current.getMarkdown() == slide.slide_content.table) {
    //     console.log("No changes made to the markdown")
    //     return;
    // }
    setEditingMarkdown(false);
    setMarkdownLoading(true);
    await updateSlide(presentationID, {
      id: slide.id,
      slide_content: {
        ...slide.slide_content,
        content: editorRef.current?.getMarkdown(),
      },
    });
    await fetchSlide(slide.id);
    setMarkdownLoading(false);
  };

  const handleContentClick = async (e: React.MouseEvent) => {
    // Prevent triggering setEditingMarkdown when clicking inside Footnote
    if ((e.target as HTMLElement).closest(".footnote-container")) {
      return;
    }
    await setEditingMarkdown(true);
  };

  return (
    <div className="p-12 pb-0 flex flex-col relative text-foreground dark:bg-foreground/10 bg-foreground/5 box-border bg-content1 outline-none shadow-medium rounded-large w-full flex-none aspect-video overflow-scroll">
      <div className="flex-none">
        <EditableTitle
          title={slide.slide_title}
          onSave={saveSlideTitle}
          loading={titleLoading}
          setBlockArrowKeys={setBlockArrowKeys}
        />
      </div>

      {editingMarkdown ? (
        <div
          className={cn(
            "relative ring-[1.8px] ring-foreground rounded-medium max-w-none flex-shrink",
            "prose prose-sm dark:prose-invert dark:dark-theme mt-8"
          )}
        >
          <ForwardRefEditor
            ref={editorRef}
            markdown={slide.slide_content.content}
            className="dark-editor dark-theme"
            toolbarContents={
              <div
                onMouseDown={(e) => e.preventDefault()}
                className="flex flex-row"
              >
                <UndoRedo />
                <BoldItalicUnderlineToggles />
                <ListsToggle />
                <InsertTable />
                {/* Revert Button */}
                <ButtonWithTooltip onClick={() => setEditingMarkdown(false)} title="Revert">
                  <Icon
                    icon="tabler:circle-chevrons-left"
                    width="25"
                    height="25"
                    className="text-warning-500 hover:text-warning-600 ml-2 -mr-0.5"
                  />
                </ButtonWithTooltip>
                {/* Save Button */}
                <ButtonWithTooltip onClick={saveSlideMarkdown} title="Save">
                  <Icon
                    icon="tabler:circle-check"
                    width="25"
                    height="25"
                    className="text-success-500 hover:text-success-600 mr-2"
                  />
                </ButtonWithTooltip>
              </div>
            }
            onBlur={() => saveSlideMarkdown()}
          />
        </div>
      ) : (
        <>
          <div className="flex-auto min-h-3"></div>
          <div
            className={cn(
              "flex justify-start w-full flex-shrink max-w-none prose prose-table:w-full dark:prose-invert",
              slide.slide_content.prose_class || "prose-sm"
              // "prose-xs"
            )}
            onClick={handleContentClick}
          >
            <Skeleton isLoaded={!markdownLoading} className="rounded-lg">
              <Markdown
                options={{
                  renderRule(next, node, renderChildren, state) {
                    // @ts-ignore
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
                  wrapper: ({ children }) => <div id="prose-container" className="px-1">{children}</div>,
                  forceWrapper: true,
                }}
              >
                {slide.slide_content.content}
              </Markdown>
            </Skeleton>
          </div>
          <div className="flex-auto min-h-3"></div>
        </>
      )}
    </div>
  );
}
