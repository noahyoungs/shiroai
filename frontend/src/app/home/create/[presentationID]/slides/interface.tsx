"use client";

import { Spinner, Spacer, Button, ScrollShadow, Card } from "@nextui-org/react";
import { useRouter } from "next/navigation";
import { Icon } from "@iconify/react";
import { Slide } from "@/utils/slide-types";
import { useEffect, useState, useCallback } from "react";
import { SlideThumbnailBar } from "@/components/slide-thumbnail-bar";
import { SlideComponent } from "@/components/slides/slide-component";
import { updateSlide } from "@/actions/slides-actions";
import { Tooltip } from "@nextui-org/tooltip";
import { Skeleton } from "@nextui-org/react";
import { uuidv7 } from "uuidv7";

interface InterfaceProps {
  slides: Slide[];
  currentSlideID: string | null;
  setCurrentSlideID: (slideID: string) => void;
  allSources: any[];
  block: boolean;
  presentationID: string;
  redirectPath: string;
  fetchSlide: (slideID: string) => void;
}

export default function Interface({
  slides,
  currentSlideID,
  setCurrentSlideID,
  allSources,
  block,
  presentationID,
  redirectPath,
  fetchSlide,
}: InterfaceProps) {
  const router = useRouter();

  const [editing, setEditing] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [currentSlide, setCurrentSlide] = useState<Slide | undefined>();

  useEffect(() => {
    setCurrentSlide(slides.find((slide) => slide.id === currentSlideID));
  }, [currentSlideID, slides]);

  useEffect(() => {
    if (editing) {
      return;
    }

    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === "ArrowLeft") {
        const currentIndex = slides.findIndex(
          (slide) => slide.id === currentSlideID
        );
        if (currentIndex > 0) {
          setCurrentSlideID(slides[currentIndex - 1].id);
        }
      } else if (event.key === "ArrowRight") {
        const currentIndex = slides.findIndex(
          (slide) => slide.id === currentSlideID
        );
        if (currentIndex < slides.length - 1) {
          setCurrentSlideID(slides[currentIndex + 1].id);
        }
      }
    };

    window.addEventListener("keydown", handleKeyDown);

    return () => {
      window.removeEventListener("keydown", handleKeyDown);
    };
  }, [slides, currentSlideID, setCurrentSlideID, editing]);

  const handleArrowLeftClick = () => {
    const currentIndex = slides.findIndex(
      (slide) => slide.id === currentSlideID
    );
    if (currentIndex > 0) {
      setCurrentSlideID(slides[currentIndex - 1].id);
    }
  };

  const handleArrowRightClick = () => {
    const currentIndex = slides.findIndex(
      (slide) => slide.id === currentSlideID
    );
    if (currentIndex < slides.length - 1) {
      setCurrentSlideID(slides[currentIndex + 1].id);
    }
  };

  const handleDeleteClick = async () => {
    if (!currentSlideID) {
      throw new Error("No current slide ID found");
    }
    setRefreshing(true);
    await updateSlide(presentationID, { id: currentSlideID, hidden: true });
    await fetchSlide(currentSlideID);
    const currentIndex = slides.findIndex(
      (slide) => slide.id === currentSlideID
    );
    if (currentIndex > 0) {
      setCurrentSlideID(slides[currentIndex - 1].id);
    }
    setRefreshing(false);
  };

  const handleLayoutChangeClick = async (newLayout: string) => {
    if (!currentSlideID) {
      throw new Error("No current slide ID found");
    }
    setRefreshing(true);
    await updateSlide(presentationID, {
      id: currentSlideID,
      layout: newLayout,
    });
    await fetchSlide(currentSlideID);
    setRefreshing(false);
  };

  const handleSequentialChangeClick = async (newSequential: boolean) => {
    if (!currentSlideID) {
      throw new Error("No current slide ID found");
    }
    setRefreshing(true);
    await updateSlide(presentationID, {
      id: currentSlideID,
      sequential: newSequential,
    });
    await fetchSlide(currentSlideID);
    setRefreshing(false);
  };

  const handleAddBulletItemClick = async () => {
    if (!currentSlideID) {
      throw new Error("No current slide ID found");
    }
    if (currentSlide?.slide_type !== "short_bullets_slide") {
      throw new Error("Current slide is not a short bullets slide");
    }
    if (currentSlide.slide_content.length >= 5) {
      return;
    }
    setRefreshing(true);
    await updateSlide(presentationID, {
      id: currentSlideID,
      slide_content: [
        ...currentSlide.slide_content,
        {
          content: "Click to edit",
          excerpt: null,
          icon: {
            name: "circle",
            source: "tabler",
          },
          id: uuidv7(),
        },
      ],
    });
    await fetchSlide(currentSlideID);
    setRefreshing(false);
  }

  const handleImagePositionChangeClick = async (newPosition: string) => {
    if (!currentSlideID) {
      throw new Error("No current slide ID found");
    }
    setRefreshing(true);
    await updateSlide(presentationID, {
      id: currentSlideID,
      image_position: newPosition,
    });
    await fetchSlide(currentSlideID);
    setRefreshing(false);
  };

  const currentIndex = slides.findIndex((slide) => slide.id === currentSlideID);
  const isFirstSlide = currentIndex === 0;
  const isLastSlide = currentIndex === slides.length - 1;

  return (
    <div className="flex flex-col h-full flex-auto pt-6">
    {currentSlideID && (
      <div className="flex flex-row items-center justify-between">
        <h3>Current Slide</h3>
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
              onClick={() => !editing && handleArrowLeftClick()}
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
              onClick={() => !editing && handleArrowRightClick()}
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
    {currentSlideID && (
      <Skeleton isLoaded={!refreshing} className="rounded-large">
        {currentSlide && (
          <SlideComponent
            presentationID={presentationID}
            slide={currentSlide}
            allSources={allSources}
            fetchSlide={fetchSlide}
            setBlockArrowKeys={setEditing}
          />
        )}
      </Skeleton>
    )}
    <Spacer y={4} />
    {/* Thumbnail Bar */}
    <SlideThumbnailBar
      slides={slides}
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
