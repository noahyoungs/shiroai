import React, { useState, useRef, useEffect } from "react";
import Markdown, { RuleType } from "markdown-to-jsx";
import { Tooltip, Skeleton } from "@nextui-org/react";
import { Icon } from "@iconify/react";
import { ForwardRefEditor } from "../mdx-editor/ForwardRefEditor";
import "@mdxeditor/editor/style.css";
import "@/components/mdx-editor/styles.css";
import { EditableTitle } from "./editable-title";
import { cleanMarkdown } from "@/actions/clean-editor-md";
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
import { MarkdownSlide, Slide } from "@/utils/slide-types";

type MarkdownSlideComponentProps = {
  slide: MarkdownSlide;
  setSlide: (slide: Partial<Slide>, splitSlides?: boolean) => void;
  allSources?: any[];
  presentationID: string;
  setBlockArrowKeys: (block: boolean) => void;
};

export function MarkdownSlideComponent({
  slide,
  setSlide,
  allSources,
  presentationID,
  setBlockArrowKeys,
}: MarkdownSlideComponentProps) {
  const [editingMarkdown, setEditingMarkdown] = useState(false);
  const [titleLoading, setTitleLoading] = useState(false);
  const [markdownLoading, setMarkdownLoading] = useState(false);
  const [hasTable, setHasTable] = useState(false);
  const editorRef = useRef<MDXEditorMethods>(null);
  const markdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    setBlockArrowKeys(editingMarkdown);
  }, [editingMarkdown, setBlockArrowKeys]);

  useEffect(() => {
    if (markdownRef.current) {
      const tableElement = markdownRef.current.querySelector("table");
      setHasTable(!!tableElement);
    }
  }, [slide.slide_content.content]);

  const saveSlideTitle = async (newTitle: string) => {
    setTitleLoading(true);
    setSlide({
      slide_title: newTitle,
    });
    setTitleLoading(false);
  };

  const saveSlideMarkdown = async () => {
    if (!editorRef.current) return;
    if (editorRef.current?.getMarkdown().trim() === "") {
      alert("Slide content cannot be empty");
      return;
    }
    setEditingMarkdown(false);
    setMarkdownLoading(true);
    setSlide(
      {
        ...slide,
        slide_content: {
          ...slide.slide_content,
          content: cleanMarkdown(editorRef.current?.getMarkdown()),
        },
      },
      true
    );
    setMarkdownLoading(false);
  };

  const handleContentClick = async (e: React.MouseEvent) => {
    if ((e.target as HTMLElement).closest(".footnote-container")) {
      return;
    }
    await setEditingMarkdown(true);
  };

  return (
    <div className="p-12 pb-0 flex flex-col relative w-full flex-grow overflow-scroll">
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
                <ButtonWithTooltip
                  onClick={() => setEditingMarkdown(false)}
                  title="Revert"
                >
                  <Icon
                    icon="tabler:circle-chevrons-left"
                    width="25"
                    height="25"
                    className="text-warning-500 hover:text-warning-600 ml-2 -mr-0.5"
                  />
                </ButtonWithTooltip>
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
            autoFocus
          />
        </div>
      ) : (
        <>
          <div className="flex-auto min-h-6"></div>
          <div
            onClick={handleContentClick}
            className={cn("flex items-center w-full", {
              "justify-center": hasTable,
            })}
            ref={markdownRef}
          >
            <Skeleton isLoaded={!markdownLoading} className="rounded-lg">
              {typeof slide.slide_content.content === "string" ? (
                <div className="flex flex-col">
                  <div
                    className={cn(
                      "flex justify-start w-full max-w-none prose dark:prose-invert",
                      slide.slide_content.prose_class || "prose-sm"
                    )}
                  >
                    <Markdown
                      options={{
                        renderRule(next, node, renderChildren, state) {
                          if (node.type === RuleType.footnoteReference) {
                            const footnoteKeys = node.text.split(",^");
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
                  </div>
                </div>
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
            </Skeleton>
          </div>
          <div className="flex-auto min-h-12"></div>
        </>
      )}
    </div>
  );
}
