import { SimpleMermaidSlide, Slide } from "@shared-utils/database-types";
import { useTheme } from "next-themes";
import DOMPurify from "dompurify";
import "@/components/slides/mermaid-styles.css";
import {
  Modal,
  ModalContent,
  ModalHeader,
  ModalBody,
  useDisclosure,
  Tooltip,
} from "@nextui-org/react";
import { Icon } from "@iconify/react";
import { ExcerptCard } from "../excerpt-card";
import { useState, useRef } from "react";
import { EditableTitle } from "./editable-title";

const SvgRenderer = ({ svgString }: { svgString: string }) => {
  const sanitizedSvgString = svgString;
  return (
    <div
      className="w-full flex flex-row justify-center max-h-[50vh]"
      id="mermaid-svg-container"
      dangerouslySetInnerHTML={{ __html: sanitizedSvgString }}
    />
  );
};

export function MermaidSources({
  excerpts,
  allSources,
}: {
  excerpts: any;
  allSources: any[];
}) {
  const [currentIndex, setCurrentIndex] = useState(0);

  const handlePrev = () => {
    if (currentIndex > 0) {
      setCurrentIndex(currentIndex - 1);
    }
  };

  const handleNext = () => {
    if (currentIndex < excerpts.length - 1) {
      setCurrentIndex(currentIndex + 1);
    }
  };

  if (!(excerpts?.length > 0)) return <div>No sources found</div>;
  else
    return (
      <>
        <h3 className="text-left text-lg">
          {excerpts.length > 1
            ? `Source ${currentIndex + 1} of ${excerpts.length}`
            : "Source"}
        </h3>
        <div className="flex flex-col gap-4 items-center">
          {excerpts.length > 1 && (
            <div className="flex items-center justify-between w-full">
              <Icon
                icon="tabler:chevron-compact-left"
                width="32"
                height="32"
                className={
                  currentIndex === 0
                    ? "text-foreground/30"
                    : "text-foreground/80  hover:text-foreground cursor-pointer"
                }
                onClick={handlePrev}
              />
              <ExcerptCard
                key={currentIndex}
                text={excerpts[currentIndex]?.text || ""}
                source={allSources.find(
                  (source) => source.id === excerpts[currentIndex]?.source_id
                )}
              />
              <Icon
                icon="tabler:chevron-compact-right"
                width="32"
                height="32"
                className={
                  currentIndex === excerpts.length - 1
                    ? "text-foreground/30"
                    : "text-foreground/80 hover:text-foreground cursor-pointer"
                }
                onClick={handleNext}
              />
            </div>
          )}
          {excerpts.length === 1 && (
            <ExcerptCard
              key={currentIndex}
              text={excerpts[currentIndex]?.text || ""}
              source={allSources.find(
                (source) => source.id === excerpts[currentIndex]?.source_id
              )}
            />
          )}
        </div>
      </>
    );
}

type SimpleMermaidSlideComponentProps = {
  presentationID: string;
  slide: SimpleMermaidSlide;
  setSlide: (slide: Partial<Slide>) => void;
  allSources?: any[];
  setBlockArrowKeys: (block: boolean) => void;
};
export function SimpleMermaidSlideComponent({
  presentationID,
  slide,
  setSlide,
  allSources,
  setBlockArrowKeys,
}: SimpleMermaidSlideComponentProps) {
  const { theme } = useTheme();
  const dark = theme === "dark";

  const { isOpen, onOpen, onOpenChange } = useDisclosure();
  const [titleLoading, setTitleLoading] = useState(false);

  const saveSlideTitle = async (newTitle: string) => {
    setTitleLoading(true);
    setSlide({
      slide_title: newTitle,
    });
    setTitleLoading(false);
  };

  return (
    <>
      <Modal
        isOpen={isOpen}
        onOpenChange={onOpenChange}
        closeButton={<Icon icon="tabler:x" width={40} height={40} />}
        classNames={{
          closeButton: "top-3 right-3 w-[40px] h-[40px] p-0.5",
        }}
        size="5xl"
        scrollBehavior="outside"
      >
        <ModalContent>
          {(onClose) => (
            <>
              <ModalHeader className="flex flex-col gap-10">
                Diagram Sources
              </ModalHeader>
              <ModalBody className="mb-8">
                {allSources && slide.slide_content.excerpts?.length && (
                  <MermaidSources
                    allSources={allSources}
                    excerpts={slide.slide_content.excerpts}
                  />
                )}
              </ModalBody>
            </>
          )}
        </ModalContent>
      </Modal>
      <div className="flex flex-col p-12 w-full flex-grow">
        <div className="flex-none">
          <EditableTitle
            title={slide.slide_title}
            onSave={saveSlideTitle}
            loading={titleLoading}
            setBlockArrowKeys={setBlockArrowKeys}
          />
        </div>

        {/* Vertical centering: */}
        <div className="flex-grow min-h-6"></div>
        <div
          className="flex-none"
          onClick={() => console.log(slide.slide_content.mermaid_code)}
        >
          <SvgRenderer
            svgString={
              dark
                ? slide.slide_content.dark_svg
                : slide.slide_content.light_svg
            }
          />
        </div>
        <div className="flex-grow min-h-1"></div>
      </div>
      <div className="absolute right-[5%] bottom-[5%]">
        <Tooltip content="Click to view diagram sources" color='primary' placement="left">
          <Icon
            icon="tabler:input-search"
            width={33}
            height={33}
            onClick={onOpen}
            className="text-primary-500 hover:text-primary-600"
          />
        </Tooltip>
      </div>
    </>
  );
}
