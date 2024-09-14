import {
  Spinner,
  Spacer,
  Button,
  ScrollShadow,
  Card,
  Tabs,
  Tab,
  CardBody,
  Textarea,
} from "@nextui-org/react";
import { useRouter } from "next/navigation";
import { Icon } from "@iconify/react";
import { Slide } from "@shared-utils/database-types";
import { useEffect, useState, useCallback, useRef } from "react";
import { SlideThumbnailBar } from "@/components/slide-thumbnail-bar";
import { SlideComponent } from "@/components/slides/slide-component";
import { uuidv7 } from "uuidv7";
import { PersistentSlideList } from "@/utils/persistent-slides-list";
import { ActionButtonBar } from "@/components/slides/action-buttons/action-button-bar";
import SlideControls from "@/components/slides/slide-controls";
import { ScriptSpeakerNotesTabs } from "@/components/slides/script-speaker-notes-tabs";
import { set } from "lodash";

interface InterfaceProps {
  slideList: PersistentSlideList;
  currentSlideID: string | null;
  setCurrentSlideID: (slideID: string) => void;
  allSources: any[];
  presentationID: string;
  pushingSlideStatus: { [key: string]: string };
  fetchingSlideStatus: { [key: string]: string };
  errors: { [key: string]: string };
  socketReady: boolean;
  generateScriptNotes: (
    target: "script" | "notes",
    style: number,
    customStyle?: string,
    maxChars?: number
  ) => void;
}

export default function Interface({
  slideList,
  currentSlideID,
  setCurrentSlideID,
  allSources,
  presentationID,
  pushingSlideStatus,
  fetchingSlideStatus,
  errors,
  socketReady,
  generateScriptNotes,
}: InterfaceProps) {
  const router = useRouter();

  const [blockSlideControls, setBlockSlideControls] = useState(false);
  const [slideUpdateTrigger, setSlideUpdateTrigger] = useState(0); // State to trigger re-render
  const [scriptNotesUpdateTrigger, setScriptNotesUpdateTrigger] = useState(0);

  const currentSlide = currentSlideID
    ? slideList.getSlide(currentSlideID)
    : null;

  return (
    <div className="flex flex-col h-full flex-auto overflow-visible">
      <SlideControls
        slideList={slideList}
        currentSlideID={currentSlideID}
        setCurrentSlideID={setCurrentSlideID}
        pushingSlideStatus={pushingSlideStatus}
        fetchingSlideStatus={fetchingSlideStatus}
        errors={errors}
        socketReady={socketReady}
        blockSlideControls={blockSlideControls}
        setBlockSlideControls={setBlockSlideControls}
        slideUpdateTrigger={slideUpdateTrigger}
        setSlideUpdateTrigger={setSlideUpdateTrigger}
      />
      <ScrollShadow
        className="flex-grow overflow-visible overflow-y-scroll px-1 pt-1"
        size={30}
      >
        {currentSlideID && currentSlide && (
          <>
            <div className="relative">
              {!socketReady && (
                <div
                  className="absolute inset-0 bg-gray-500 bg-opacity-50 z-[100] rounded-xl"
                  onClick={(e) => e.stopPropagation()}
                  onFocus={(e) => e.stopPropagation()}
                />
              )}
              {/* min height maintains aspect ratio of slide */}
              <div className="flex overflow-clip text-foreground bg-foreground/5 box-border rounded-[15px] w-full flex-none ring-1 ring-foreground/30 min-h-[54vw] xl:min-h-[35.5vw] p-0">
                <SlideComponent
                  key={slideUpdateTrigger} // Ensure re-render by updating key
                  presentationID={presentationID}
                  slide={currentSlide}
                  setSlide={(slide: Partial<Slide>, splitSlides = false) =>
                    slideList.updateSlides(
                      { ...slide, slide_id: currentSlideID },
                      false,
                      splitSlides
                    )
                  }
                  allSources={allSources}
                  setBlockArrowKeys={setBlockSlideControls}
                />
              </div>
            </div>
            <Spacer y={4} />
            <ScriptSpeakerNotesTabs
              currentSlide={currentSlide}
              currentSlideID={currentSlideID}
              slideList={slideList}
              key={scriptNotesUpdateTrigger}
            />
          </>
        )}
      </ScrollShadow>
      <div className="flex flex-col mt-4 gap-2">
        <ActionButtonBar
          presentationId={presentationID}
          generateScriptNotes={generateScriptNotes}
        />
        <SlideThumbnailBar
          slides={slideList.convertToArray()}
          currentSlideID={currentSlideID}
          setCurrentSlideID={setCurrentSlideID}
          blockSlideSwitching={blockSlideControls}
        />
      </div>
    </div>
  );
}
