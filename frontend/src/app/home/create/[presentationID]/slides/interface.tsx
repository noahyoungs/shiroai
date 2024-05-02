// interface.tsx
"use client";

import { Spinner, Spacer, Button, ScrollShadow, Card } from "@nextui-org/react";
import { useRouter } from "next/navigation";
import { Icon } from "@iconify/react";
import { Slide } from "@/utils/slide-types";
import { useEffect } from "react";
import { SlideThumbnailBar } from "@/components/slide-thumbnail-bar";
import { SlideComponent } from "@/components/slides/slide-component";

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

    useEffect(() => {
        const handleKeyDown = (event: KeyboardEvent) => {
            if (event.key === "ArrowLeft") {
                const currentIndex = slides.findIndex((slide) => slide.id === currentSlideID);
                if (currentIndex > 0) {
                    setCurrentSlideID(slides[currentIndex - 1].id);
                }
            } else if (event.key === "ArrowRight") {
                const currentIndex = slides.findIndex((slide) => slide.id === currentSlideID);
                if (currentIndex < slides.length - 1) {
                    setCurrentSlideID(slides[currentIndex + 1].id);
                }
            }
        };

        window.addEventListener("keydown", handleKeyDown);

        return () => {
            window.removeEventListener("keydown", handleKeyDown);
        };
    }, [slides, currentSlideID, setCurrentSlideID]);

    return (
        <div className="flex flex-col h-full flex-auto pt-6">
            {/* Sticky title at top */}
            {currentSlideID && (
                <SlideComponent
                    presentationID={presentationID}
                    slide={slides.find((slide) => slide.id === currentSlideID)!}
                    allSources={allSources}
                    fetchSlide={fetchSlide}
                />
            )}
            <Spacer y={4} />
            {/* Thumbnail Bar */}
            <SlideThumbnailBar
                slides={slides}
                currentSlideID={currentSlideID}
                setCurrentSlideID={setCurrentSlideID}
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