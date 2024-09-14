import {
  Tooltip,
  Modal,
  ModalContent,
  ModalHeader,
  ModalBody,
  ModalFooter,
} from "@nextui-org/react";
import { Icon } from "@iconify/react";
import { useEffect, useState, useCallback } from "react";
import { Slide } from "@shared-utils/database-types";
import { uuidv7 } from "uuidv7";
import { PersistentSlideList } from "@/utils/persistent-slides-list";
import { SlidesSyncStatus } from "@/components/slides-sync-status";

interface SlideControlsProps {
  slideList: PersistentSlideList;
  currentSlideID: string | null;
  setCurrentSlideID: (slideID: string) => void;
  pushingSlideStatus: { [key: string]: string };
  fetchingSlideStatus: { [key: string]: string };
  errors: { [key: string]: string };
  socketReady: boolean;
  blockSlideControls: boolean;
  setBlockSlideControls: (value: boolean) => void;
  slideUpdateTrigger: number;
  setSlideUpdateTrigger: (value: number) => void;
}

export default function SlideControls({
  slideList,
  currentSlideID,
  setCurrentSlideID,
  pushingSlideStatus,
  fetchingSlideStatus,
  errors,
  socketReady,
  blockSlideControls,
  setBlockSlideControls,
  slideUpdateTrigger,
  setSlideUpdateTrigger,
}: SlideControlsProps) {
  const currentSlide = currentSlideID
    ? slideList.getSlide(currentSlideID)
    : null;
  const isFirstSlide = currentSlide ? currentSlide.previous === null : false;
  const isLastSlide = currentSlide ? currentSlide.next === null : false;

  const navigateSlide = (direction: "previous" | "next") => {
    if (!currentSlideID || blockSlideControls) {
      console.log("No current slide ID found or editing");
      return;
    }
    console.log("Navigating slide", direction);
    const targetSlideID =
      direction === "previous"
        ? slideList.getSlide(currentSlideID).previous
        : slideList.getSlide(currentSlideID).next;

    if (targetSlideID) {
      console.log("Navigating to slide", targetSlideID);
      setCurrentSlideID(targetSlideID);
    } else {
      console.log("Cannot navigate to slide, no slide found.");
    }
  };

  useEffect(() => {
    if (blockSlideControls) {
      return;
    }

    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === "ArrowLeft") {
        navigateSlide("previous");
      } else if (event.key === "ArrowRight") {
        navigateSlide("next");
      }
    };

    window.addEventListener("keydown", handleKeyDown);

    return () => {
      window.removeEventListener("keydown", handleKeyDown);
    };
  }, [slideList, currentSlideID, setCurrentSlideID, blockSlideControls]);

  const handleDeleteClick = async () => {
    if (!currentSlideID) {
      throw new Error("No current slide ID found");
    }
    await slideList.hideSlide(currentSlideID);
    setSlideUpdateTrigger((prev: number) => prev + 1); // Trigger re-render
    navigateSlide("previous");
  };

  const handleLayoutChangeClick = async (newLayout: string) => {
    if (!currentSlideID) {
      throw new Error("No current slide ID found");
    }
    await slideList.updateSlides({
      slide_id: currentSlideID,
      layout: newLayout,
    });
    setSlideUpdateTrigger((prev: number) => prev + 1); // Trigger re-render
  };

  const handleSequentialChangeClick = async (newSequential: boolean) => {
    if (!currentSlideID) {
      throw new Error("No current slide ID found");
    }
    await slideList.updateSlides({
      slide_id: currentSlideID,
      sequential: newSequential,
    });
    setSlideUpdateTrigger((prev: number) => prev + 1); // Trigger re-render
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
      alert("You can only have up to 5 nodes.");
      return;
    }

    await slideList.updateSlides({
      slide_id: currentSlideID,
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
    setSlideUpdateTrigger((prev: number) => prev + 1); // Trigger re-render
  };

  const handleImagePositionChangeClick = async (newPosition: string) => {
    if (!currentSlideID) {
      throw new Error("No current slide ID found");
    }
    await slideList.updateSlides({
      slide_id: currentSlideID,
      image_position: newPosition,
    });
    setSlideUpdateTrigger((prev: number) => prev + 1); // Trigger re-render
  };

  return (
    <div className="flex flex-col flex-grow pt-6">
      <div className="flex flex-row items-center justify-between">
        <div className="flex flex-row mb-3 gap-4">
          {currentSlideID && socketReady ? (
            <SlidesSyncStatus
              pushingSlideStatus={pushingSlideStatus}
              fetchingSlideStatus={fetchingSlideStatus}
              errors={errors}
            />
          ) : (
            <div style={{ height: "30px" }}></div>
          )}
        </div>
        <div
          className="flex flex-row items-center justify-evenly gap-2 mb-3"
          style={{ minHeight: "30px" }}
        >
          {currentSlideID && socketReady ? (
            <>
              {currentSlide?.slide_type === "short_bullets_slide" && (
                <>
                  {currentSlide.sequential ? (
                    <Tooltip content="Remove Arrows" disableAnimation>
                      <Icon
                        icon="tabler:direction-sign-off"
                        width={30}
                        onClick={() =>
                          !blockSlideControls &&
                          handleSequentialChangeClick(false)
                        }
                        className={
                          blockSlideControls
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
                        onClick={() =>
                          !blockSlideControls &&
                          handleSequentialChangeClick(true)
                        }
                        className={
                          blockSlideControls
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
                      onClick={() =>
                        !blockSlideControls && handleAddBulletItemClick()
                      }
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
                        onClick={() =>
                          !blockSlideControls && handleLayoutChangeClick("grid")
                        }
                        className={
                          blockSlideControls
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
                        onClick={() =>
                          !blockSlideControls && handleLayoutChangeClick("list")
                        }
                        className={
                          blockSlideControls
                            ? "text-foreground/30"
                            : "text-foreground/70 hover:text-foreground"
                        }
                      />
                    </Tooltip>
                  )}
                </>
              )}
              {currentSlide?.slide_type === "section_header_slide" &&
                (currentSlide.image_position === "left" ? (
                  <Tooltip
                    content="Move Image to Right"
                    disableAnimation
                    isDisabled={blockSlideControls}
                  >
                    <Icon
                      icon="tabler:square-half"
                      width={30}
                      onClick={() =>
                        !blockSlideControls &&
                        handleImagePositionChangeClick("right")
                      }
                      className={
                        blockSlideControls
                          ? "text-foreground/30"
                          : "text-foreground/70 hover:text-foreground"
                      }
                    />
                  </Tooltip>
                ) : (
                  <Tooltip
                    content="Move Image to Left"
                    disableAnimation
                    isDisabled={blockSlideControls}
                  >
                    <Icon
                      icon="tabler:square-half"
                      width={30}
                      onClick={() =>
                        !blockSlideControls &&
                        handleImagePositionChangeClick("left")
                      }
                      className={
                        blockSlideControls
                          ? "text-foreground/30"
                          : "text-foreground/70 hover:text-foreground"
                      }
                      style={{ transform: "scaleX(-1)" }} // Flip horizontally
                    />
                  </Tooltip>
                ))}
              {currentSlide?.slide_type === "presentation_title_slide" ? (
                <Icon
                  icon="tabler:trash-x"
                  width={30}
                  className="text-danger/50"
                />
              ) : (
                <Tooltip
                  content="Delete Slide"
                  color="danger"
                  disableAnimation
                  isDisabled={blockSlideControls}
                >
                  <Icon
                    icon="tabler:trash-x"
                    width={30}
                    className={
                      blockSlideControls
                        ? "text-danger/30"
                        : "text-danger/80 hover:text-danger"
                    }
                    onClick={() => !blockSlideControls && handleDeleteClick()}
                  />
                </Tooltip>
              )}
              <Tooltip
                content="Previous Slide"
                disableAnimation
                isDisabled={isFirstSlide || blockSlideControls}
              >
                <Icon
                  icon="tabler:arrow-narrow-left"
                  width={30}
                  onClick={() =>
                    !blockSlideControls && navigateSlide("previous")
                  }
                  className={
                    isFirstSlide || blockSlideControls
                      ? "text-foreground/30"
                      : "text-foreground/80 hover:text-foreground"
                  }
                />
              </Tooltip>
              <Tooltip
                content="Next Slide"
                disableAnimation
                isDisabled={isLastSlide || blockSlideControls}
              >
                <Icon
                  icon="tabler:arrow-narrow-right"
                  width={30}
                  onClick={() => !blockSlideControls && navigateSlide("next")}
                  className={
                    isLastSlide || blockSlideControls
                      ? "text-foreground/30"
                      : "text-foreground/80 hover:text-foreground"
                  }
                />
              </Tooltip>
            </>
          ) : (
            <div style={{ height: "30px" }}></div> // Adjust width accordingly
          )}
        </div>
      </div>
    </div>
  );
}
