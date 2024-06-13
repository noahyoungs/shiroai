import { MarkdownTableSlide } from "@/utils/slide-types";
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

type MarkdownTableSlideComponentProps = {
  slide: MarkdownTableSlide;
  allSources?: any[];
  fetchSlide: (slideID: string) => void;
  presentationID: string;
  setBlockArrowKeys: (block: boolean) => void;
};

export function MarkdownTableSlideComponent({
  slide,
  allSources,
  fetchSlide,
  presentationID,
  setBlockArrowKeys,
}: MarkdownTableSlideComponentProps) {
  const [editingMarkdown, setEditingMarkdown] = useState(false);
  const [titleLoading, setTitleLoading] = useState(false);
  const [markdownLoading, setMarkdownLoading] = useState(false);
  const [unescapedMarkdown, setUnescapedMarkdown] = useState("");
  const editorRef = useRef<MDXEditorMethods>(null);

  useEffect(() => {
    if (slide.slide_content && slide.slide_content.table) {
  
      let escaped = slide.slide_content.table.replace(/\\\[/g, "[");

      const combineFootnotes = (markdown) => {
        // Regular expression to match footnotes patterns with optional spaces
        const footnoteRegex = /(\[\^\d+\])\s*(\[\^\d+\])+/g;
      
        // Function to combine the footnotes
        const combine = (match) => {
          return match.replace(/\]\s*\[/g, ',').replace(/\[|\]/g, '');
        };
      
        // Replace the found footnote patterns with the combined format
        return markdown.replace(footnoteRegex, (match) => `[${combine(match)}]`);
      };
      
      console.log("Before: ", escaped);

      let footnotesCombined = combineFootnotes(escaped)

      console.log("After: ", footnotesCombined);
  
      setUnescapedMarkdown(footnotesCombined);
    }
  }, [slide.slide_content.table]);

  useEffect(() => {
    setBlockArrowKeys(editingMarkdown);
  }, [editingMarkdown, setBlockArrowKeys]);

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

  // for markdown
  const saveSlideMarkdown = async () => {
    if (!editorRef.current) return;
    setEditingMarkdown(false);
    // if (editorRef.current.getMarkdown() == slide.slide_content.table) {
    //     console.log("No changes made to the markdown")
    //     return;
    // }
    setEditingMarkdown(false);
    setMarkdownLoading(true);
    await updateSlide(presentationID, {
      ...slide,
      slide_content: {
        ...slide.slide_content,
        table: editorRef.current?.getMarkdown(),
      },
    });
    await fetchSlide(slide.id);
    setMarkdownLoading(false);
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
            "relative border-[1.8px] border-black rounded-medium max-w-none flex-shrink",
            "prose prose-sm"
          )}
        >
          <ForwardRefEditor
            ref={editorRef}
            markdown={slide.slide_content.table}
            saveSlideMarkdown={saveSlideMarkdown}
            className="dark-theme dark-editor"
            toolbarContents={
              <div
                onMouseDown={(e) => e.preventDefault()}
                className="flex flex-row"
              >
                <UndoRedo />
                <BoldItalicUnderlineToggles />
                <ListsToggle />
                <InsertTable />
                <ButtonWithTooltip onClick={saveSlideMarkdown} title="Save">
                  <Icon
                    icon="tabler:circle-check"
                    width="25"
                    height="25"
                    className="text-success-500"
                  />
                </ButtonWithTooltip>
              </div>
            }
            onBlur={() => saveSlideMarkdown()}
          />
        </div>
      ) : (
        <>
          <div className="flex-auto"></div>
          <div
            className={cn(
              "flex justify-center w-full flex-shrink max-w-none prose dark:prose-invert",
              slide.slide_content.prose_class || "prose-sm"
              // "prose-xs"
            )}
          >
            <Skeleton isLoaded={!markdownLoading} className="rounded-lg">
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
                  wrapper: ({ children }) => <div id="prose-container">{children}</div>,
                  forceWrapper: true,
                }}
                onClick={async () => await setEditingMarkdown(true)}
              >
                {unescapedMarkdown}
              </Markdown>
            </Skeleton>
          </div>
          <div className="flex-auto"></div>
        </>
      )}
    </div>
  );
}
