import { Spinner, Spacer, Button, ScrollShadow, Card } from "@nextui-org/react";
import { useRouter } from "next/navigation";
import { Icon } from "@iconify/react";
import { Slide } from "@/utils/slide-types";
import { useEffect, useState, useCallback } from "react";
import { SlideThumbnailBar } from "@/components/slide-thumbnail-bar";
import { SlideComponent } from "@/components/slides/slide-component";
import { updateSlides } from "@/actions/slides-actions";
import { Tooltip } from "@nextui-org/tooltip";
import { Skeleton } from "@nextui-org/react";
import { uuidv7 } from "uuidv7";
import { PersistentSlideList } from "@/utils/persistent-slides-list";

interface InterfaceProps {
  slideList: PersistentSlideList;
  currentSlideID: string | null;
  setCurrentSlideID: (slideID: string) => void;
  allSources: any[];
  block: boolean;
  presentationID: string;
  redirectPath: string;
}

export default function Interface({
  slideList,
  currentSlideID,
  setCurrentSlideID,
  allSources,
  block,
  presentationID,
  redirectPath,
}: InterfaceProps) {
  const router = useRouter();

  const [editing, setEditing] = useState(false);
  const [slideUpdateTrigger, setSlideUpdateTrigger] = useState(0); // State to trigger re-render

  const currentSlide = currentSlideID ? slideList.getSlide(currentSlideID) : null;
  const isFirstSlide = currentSlide ? currentSlide.previous === null : false;
  const isLastSlide = currentSlide ? currentSlide.next === null : false;

  console.log("Current Slide ID", currentSlideID)

  const navigateSlide = (direction: 'previous' | 'next') => {
    if (!currentSlideID || editing) {
      console.log("No current slide ID found or editing");
      return;
    }
    console.log("Navigating slide", direction);
    const targetSlideID = direction === 'previous' 
      ? slideList.getSlide(currentSlideID).previous 
      : slideList.getSlide(currentSlideID).next;
  
    if (targetSlideID) {
      console.log("Navigating to slide", targetSlideID)
      setCurrentSlideID(targetSlideID);
    } else {
      console.log("Cannot navigate to slide, no slide found.");
    }
  };
  
  useEffect(() => {
    if (editing) {
      return;
    }
  
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === "ArrowLeft") {
        navigateSlide('previous');
      } else if (event.key === "ArrowRight") {
        navigateSlide('next');
      }
    };
  
    window.addEventListener("keydown", handleKeyDown);
  
    return () => {
      window.removeEventListener("keydown", handleKeyDown);
    };
  }, [slideList, currentSlideID, setCurrentSlideID, editing]);


  const handleDeleteClick = async () => {
    if (!currentSlideID) {
      throw new Error("No current slide ID found");
    }
    await slideList.hideSlide(currentSlideID);
    setSlideUpdateTrigger(prev => prev + 1); // Trigger re-render
    navigateSlide('previous');
  };

  const handleLayoutChangeClick = async (newLayout: string) => {
    if (!currentSlideID) {
      throw new Error("No current slide ID found");
    }
    await slideList.updateSlides({
      id: currentSlideID,
      layout: newLayout,
    });
    setSlideUpdateTrigger(prev => prev + 1); // Trigger re-render
  };

  const handleSequentialChangeClick = async (newSequential: boolean) => {
    if (!currentSlideID) {
      throw new Error("No current slide ID found");
    }
    await slideList.updateSlides({
      id: currentSlideID,
      sequential: newSequential,
    });
    setSlideUpdateTrigger(prev => prev + 1); // Trigger re-render
  };

  const handleAddBulletItemClick = async () => {
    if (!currentSlideID) {
      throw new Error("No current slide ID found");
    }

    if (!currentSlide) {
      throw new Error("Current slide not found");
    }

    if (currentSlide.slide_type !== "short_bullets_slide") {
      throw new Error("Current slide is not compatible.");
    }
    if (currentSlide.slide_content.length >= 5) {
      alert("You can only have up to 5 nodes.")
      return;
    }

    await slideList.updateSlides({
      id: currentSlideID,
      slide_content: [
        ...currentSlide.slide_content,
        {
          content: "Click to edit",
          excerpt: null,
          icon: {
            name: "edit",
            source: "tabler",
          },
          id: uuidv7(),
        },
      ],
    });
    setSlideUpdateTrigger(prev => prev + 1); // Trigger re-render
  }

  const handleImagePositionChangeClick = async (newPosition: string) => {
    if (!currentSlideID) {
      throw new Error("No current slide ID found");
    }
    await slideList.updateSlides({
      id: currentSlideID,
      image_position: newPosition,
    });
    setSlideUpdateTrigger(prev => prev + 1); // Trigger re-render
  };

  return (
    <div className="flex flex-col h-full flex-auto pt-6">
    {currentSlideID && (
      <div className="flex flex-row items-center justify-between">
        <div className="flex flex-row mb-3 gap-4">
        <h3 className="mb-0">Current Slide</h3>
        {/* {slideList.getSaving() && (
          <Spinner
            color="primary"
            size="sm"
          />
        )} */}
        </div>
        <div className="flex flex-row items-center justify-evenly gap-2 mb-3">
          {currentSlide?.slide_type === "short_bullets_slide" && (
            <>
              {currentSlide.sequential ? (
                <Tooltip content="Remove Arrows" disableAnimation>
                  <Icon
                    icon="tabler:direction-sign-off"
                    width={30}
                    onClick={() => !editing && handleSequentialChangeClick(false)}
                    className={
                      editing
                        ? "text-foreground/30"
                        : "text-foreground/70 hover:text-foreground"
                    }
                  />
                </Tooltip>
              ) : (
                <Tooltip content="Add Arrows" disableAnimation>
                  <Icon
                    icon="tabler:direction-sign"
                    width={30}
                    onClick={() => !editing && handleSequentialChangeClick(true)}
                    className={
                      editing
                        ? "text-foreground/30"
                        : "text-foreground/70 hover:text-foreground"
                    }
                  />
                </Tooltip>
              )}
              <Tooltip content="Add Node" disableAnimation>
                <Icon
                  icon="tabler:square-plus-2"
                  width={30}
                  onClick={() => !editing && handleAddBulletItemClick()}
                  className={
                    currentSlide.slide_content.length >= 5
                      ? "text-foreground/30"
                      : "text-foreground/70 hover:text-foreground"
                  }
                />
              </Tooltip>
              {currentSlide.layout === "list" ? (
                <Tooltip content="Switch to Grid Layout" disableAnimation>
                  <Icon
                    icon="tabler:layout-grid"
                    width={30}
                    onClick={() => !editing && handleLayoutChangeClick("grid")}
                    className={
                      editing
                        ? "text-foreground/30"
                        : "text-foreground/70 hover:text-foreground"
                    }
                  />
                </Tooltip>
              ) : (
                <Tooltip content="Switch to List Layout" disableAnimation>
                  <Icon
                    icon="tabler:layout-list"
                    width={30}
                    onClick={() => !editing && handleLayoutChangeClick("list")}
                    className={
                      editing
                        ? "text-foreground/30"
                        : "text-foreground/70 hover:text-foreground"
                    }
                  />
                </Tooltip>
              )}
            </>
          )}
          {currentSlide?.slide_type === "section_header_slide" && (
            currentSlide.image_position === "left" ? (
              <Tooltip content="Move Image to Right" disableAnimation isDisabled={editing}>
                <Icon
                  icon="tabler:square-half"
                  width={30}
                  onClick={() => !editing && handleImagePositionChangeClick("right")}
                  className={
                    editing
                      ? "text-foreground/30"
                      : "text-foreground/70 hover:text-foreground"
                  }
                />
              </Tooltip>
            ) : (
              <Tooltip content="Move Image to Left" disableAnimation isDisabled={editing}>
                <Icon
                  icon="tabler:square-half"
                  width={30}
                  onClick={() => !editing && handleImagePositionChangeClick("left")}
                  className={
                    editing
                      ? "text-foreground/30"
                      : "text-foreground/70 hover:text-foreground"
                  }
                  style={{ transform: "scaleX(-1)" }} // Flip horizontally
                />
              </Tooltip>
            )
          )}
          {currentSlide?.slide_type === "presentation_title_slide" ? (
            <Icon
              icon="tabler:trash-x"
              width={30}
              className="text-danger/50"
            />
          ) : (
            <Tooltip content="Delete Slide" color="danger" disableAnimation isDisabled={editing}>
              <Icon
                icon="tabler:trash-x"
                width={30}
                className={
                  editing
                    ? "text-danger/30"
                    : "text-danger/80 hover:text-danger"
                }
                onClick={() => !editing && handleDeleteClick()}
              />
            </Tooltip>
          )}
          <Tooltip content="Previous Slide" disableAnimation isDisabled={isFirstSlide || editing}>
            <Icon
              icon="tabler:arrow-narrow-left"
              width={30}
              onClick={() => !editing && navigateSlide('previous')}
              className={
                isFirstSlide || editing
                  ? "text-foreground/30"
                  : "text-foreground/80 hover:text-foreground"
              }
            />
          </Tooltip>
          <Tooltip content="Next Slide" disableAnimation isDisabled={isLastSlide || editing}>
            <Icon
              icon="tabler:arrow-narrow-right"
              width={30}
              onClick={() => !editing && navigateSlide('next')}
              className={
                isLastSlide || editing
                  ? "text-foreground/30"
                  : "text-foreground/80 hover:text-foreground"
              }
            />
          </Tooltip>
        </div>
      </div>
    )}
    {currentSlideID && currentSlide && (
        <SlideComponent
          key={slideUpdateTrigger} // Ensure re-render by updating key
          presentationID={presentationID}
          slide={currentSlide}
          setSlide={(slide: Partial<Slide>) => slideList.updateSlides( {...slide, id: currentSlideID} )}
          allSources={allSources}
          setBlockArrowKeys={setEditing}
        />
    )}
    <Spacer y={4} />
    <SlideThumbnailBar
      slides={slideList.convertToArray()}
      currentSlideID={currentSlideID}
      setCurrentSlideID={setCurrentSlideID}
      blockSlideSwitching={editing}
    />
    <div className="flex-auto"></div>
    <Button
      color="primary"
      className="min-h-[64px] flex flex-row rounded-b-none text-base"
      isDisabled={block}
      onClick={() => {
        !block && router.push(redirectPath);
      }}
    >
      <span>Proceed to the next step</span>
      <Icon icon="tabler:arrow-narrow-right" width={30} />
    </Button>
  </div>
  
  );
}
