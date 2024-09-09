import { useState, useCallback, useEffect } from "react";
import { Tabs, Tab, Textarea } from "@nextui-org/react";
import { Slide } from "@/utils/slide-types";
import { PersistentSlideList } from "@/utils/persistent-slides-list";
import { debounce } from "lodash";
import { Icon } from "@iconify/react";

interface ScriptSpeakerNotesTabsProps {
  currentSlide: Slide | null;
  currentSlideID: string | null;
  slideList: PersistentSlideList;
}

export const ScriptSpeakerNotesTabs = ({
  currentSlide,
  currentSlideID,
  slideList,
}: ScriptSpeakerNotesTabsProps) => {
  const [script, setScript] = useState(currentSlide?.script || "");
  const [speakerNotes, setSpeakerNotes] = useState(
    currentSlide?.speaker_notes || ""
  );

  useEffect(() => {
    setScript(currentSlide?.script || "");
    setSpeakerNotes(currentSlide?.speaker_notes || "");
  }, [currentSlide?.id]);

  const updateSlideScript = useCallback(
    debounce((value) => {
      if (currentSlideID) {
        slideList.updateSlides({ script: value, slide_id: currentSlideID }, false);
      }
    }, 300),
    [currentSlideID, slideList]
  );

  const updateSlideNotes = useCallback(
    debounce((value) => {
      if (currentSlideID) {
        slideList.updateSlides(
          { speaker_notes: value, slide_id: currentSlideID },
          false
        );
      }
    }, 300),
    [currentSlideID, slideList]
  );

  const handleScriptChange = (e) => {
    const value = e.target.value;
    setScript(value);
    updateSlideScript(value);
  };

  const handleNotesChange = (e) => {
    const value = e.target.value;
    setSpeakerNotes(value);
    updateSlideNotes(value);
  };

  return (
    <Tabs
      aria-label="Additional Slide Text"
      placement="start"
      className="-mx-1 mb-4"
      classNames={{ panel: "flex-grow", tabContent: "flex-grow" }}
    >
      <Tab
        key="script"
        title={
          <div className="flex items-center space-x-2">
            <Icon icon="tabler:script" className="w-6 h-6" />
            <span>Script</span>
          </div>
        }
      >
        <Textarea
          placeholder="Enter your script here"
          value={script}
          onChange={handleScriptChange}
          fullWidth
          variant="faded"
          minRows={3}
          disableAnimation
        />
      </Tab>
      <Tab
        title={
          <div className="flex items-center space-x-2">
            <Icon icon="tabler:podium" className="w-6 h-6" />
            <span>Speaker Notes</span>
          </div>
        }
      >
        <Textarea
          placeholder="Enter your speaker notes here"
          value={speakerNotes}
          onChange={handleNotesChange}
          fullWidth
          variant="faded"
          minRows={3}
          disableAnimation
        />
      </Tab>
    </Tabs>
  );
};
