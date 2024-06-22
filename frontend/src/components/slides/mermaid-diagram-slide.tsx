import { SimpleMermaidSlide, Slide } from "@/utils/slide-types";
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
import { useState } from "react";

const SvgRenderer = ({ svgString }: { svgString: string }) => {
  // const sanitizedSvgString = DOMPurify.sanitize(svgString, {
  //     USE_PROFILES: { svg: true, svgFilters: true },
  //     ADD_ATTR: ['xmlns', 'xmlns:xlink'],
  //     ADD_TAGS: ['foreignObject', 'br']
  //   });
  const sanitizedSvgString = svgString;

  return (
    <div
      className="w-full flex flex-row justify-center max-h-[50vh]"
      id="mermaid-svg-container"
      dangerouslySetInnerHTML={{ __html: sanitizedSvgString }}
    />
  );
};

// IMPORTANT: Sources and Excerpts are different. Each excerpt has a source id. The source needs to be matched to get the source name and icon, etc.
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

  console.log(`Length of excerpts: ${excerpts?.length}`);
  console.log(`Length of allSources: ${allSources?.length}`)
  if (!(excerpts?.length > 0)) return <div>No sources found</div>;
  else return (
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
      <div className="p-12 flex flex-col relative overflow-hidden height-auto text-foreground bg-foreground/5 dark:bg-foreground/10 box-border bg-content1 outline-none shadow-medium rounded-[15px] w-full aspect-videow-full aspect-video flex-none">
        <h1 className="self-start mb-0">{slide.slide_title}</h1>
        {/* Vertical centering: */}
        <div className="flex flex-col h-full pt-5">
          <div className="flex-grow"></div>
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
          <div className="flex-grow"></div>
        </div>
        <div className="ml-auto">
          <Icon
            icon="tabler:input-search"
            width={33}
            height={33}
            onClick={onOpen}
            className="text-primary-500 hover:text-primary-600"
          />
        </div>
      </div>
    </>
  );
}
