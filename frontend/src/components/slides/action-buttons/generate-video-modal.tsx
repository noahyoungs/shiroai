import React, { useRef, useState } from "react";
import {
  Modal,
  ModalContent,
  ModalHeader,
  ModalBody,
  ModalFooter,
  Button,
  useDisclosure,
  Spacer,
  Select,
  SelectItem,
  Tab,
  Tabs,
  Switch,
} from "@nextui-org/react";
import { Icon } from "@iconify/react";
import { generateVideo } from "@/actions/generate-video"; 
import { Key } from "@react-types/shared";

// Define a type for the audio refs
type AudioRefs = {
  [key: string]: React.RefObject<HTMLAudioElement>;
};

export function GenerateVideoModal({ presentationID }: { presentationID: string }) {
  const { isOpen, onOpen, onOpenChange } = useDisclosure();
  const [selectIsOpen, setSelectIsOpen] = useState(false);
  const [playingVoice, setPlayingVoice] = useState<string | null>(null); // State to track the currently playing voice
  const [theme, setTheme] = useState<"light" | "dark" | "print">("light"); // State for theme selection
  const [includeSources, setIncludeSources] = useState<boolean>(false); // State for including sources
  const [selectedVoice, setSelectedVoice] = useState<"Danielle" | "Gregory" | "Ruth">("Danielle"); // State for voice selection
  const [selectedResolution, setSelectedResolution] = useState<"1920x1080" | "1280x720">("1920x1080"); // State for resolution selection
  const [isGenerating, setIsGenerating] = useState<boolean>(false); // State for handling loading
  const [error, setError] = useState<string | null>(null); // State for handling errors
  const [videoUrl, setVideoUrl] = useState<string | null>(null); // State to store the generated video URL

  const resolutions = [{ key: "1920x1080", label: "1080p" }, { key: "1280x720", label: "720p" }];
  const voices = [{ key: "Danielle" }, { key: "Gregory" }, { key: "Ruth" }];

  // Initialize audio refs using TypeScript's Record type
  const audioRefs: AudioRefs = {
    Danielle: useRef<HTMLAudioElement>(null),
    Gregory: useRef<HTMLAudioElement>(null),
    Ruth: useRef<HTMLAudioElement>(null),
  };

  // Function to handle play/stop toggle
  const togglePlaySample = (voice: "Danielle" | "Gregory" | "Ruth") => {
    const audio = audioRefs[voice].current;

    if (!audio) return;

    if (playingVoice === voice) {
      // Stop the audio if it's currently playing
      audio.pause();
      audio.currentTime = 0;
      setPlayingVoice(null);
    } else {
      // Stop any currently playing audio
      Object.values(audioRefs).forEach((ref) => {
        if (ref.current && !ref.current.paused) {
          ref.current.pause();
          ref.current.currentTime = 0;
        }
      });

      // Play the selected voice sample
      audio.play().then(() => {
        setPlayingVoice(voice);
      }).catch((error) => {
        console.error("Error playing audio sample:", error);
      });

      // Set the event listener to reset the state when the audio ends
      audio.onended = () => setPlayingVoice(null);
    }
  };

  const handleGenerate = async () => {
    setIsGenerating(true);
    setError(null);

    try {
      const result = await generateVideo(presentationID, selectedResolution, theme, includeSources, selectedVoice);

      if (result.success) {
        setVideoUrl(result.href!);
      } else {
        throw new Error(result.error);
      }
    } catch (error: any) {
      console.error("Failed to generate video:", error);
      setError(error.message);
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <>
      <Button
        color="secondary"
        startContent={<Icon icon="tabler:video" width={25} />}
        className="flex-grow"
        onPress={onOpen}
      >
        Generate Video
      </Button>
      <Modal
        isOpen={isOpen}
        onOpenChange={onOpenChange}
        closeButton={<Icon icon="tabler:x" width={40} height={40} />}
        classNames={{
          closeButton: "top-3 right-3 w-[40px] h-[40px] p-0.5",
        }}
        size="3xl"
        scrollBehavior="outside"
      >
        <ModalContent>
          {(onClose) => (
            <>
              <ModalHeader className="flex flex-col gap-1">
                Generate Video
              </ModalHeader>
              <ModalBody>
                <p>
                  This action generates a narrated video of your presentation.
                  The video will include your slides and a narrated voiceover
                  based on the generated script.
                </p>
                {error && (
                  <p className="text-red-500">Error: {error}</p>
                )}
                <Spacer y={1} />
                <div className="flex flex-row items-center justify-start gap-3">
                <Select
                  label="Select a resolution"
                  className="max-w-xs"
                  description="Select the resolution for your video."
                  selectedKeys={new Set([selectedResolution])}
                  fullWidth
                  onSelectionChange={(keys: Set<Key> | "all") => {
                    if (keys === "all") throw new Error("Unexpected value");
                    setSelectedResolution(keys.values().next().value as "1980x1080" | "1280x720");
                  }}
                >
                  {resolutions.map((resolution) => (
                    <SelectItem key={resolution.key} textValue={resolution.label}>
                      {resolution.label}
                    </SelectItem>
                  ))}
                </Select>
                <Spacer y={1} />
                <Select
                  label="Select a voice"
                  className="max-w-xs"
                  description="Select an AI voice for your voiceover."
                  onClick={() => setSelectIsOpen(!selectIsOpen)}
                  isOpen={selectIsOpen}
                  disallowEmptySelection
                  selectedKeys={new Set([selectedVoice])}
                  onSelectionChange={(keys: Set<Key> | "all") => {
                    if (keys === "all") throw new Error("Unexpected value");
                    const value = keys.values().next().value;
                    setSelectedVoice(value as "Danielle" | "Gregory" | "Ruth");
                  }}
                  onOpenChange={(isOpen) => isOpen && setPlayingVoice(null)}
                >
                  {voices.map((voice) => (
                    <SelectItem key={voice.key} textValue={voice.key}>
                      <div className="flex flex-row gap-2 items-center" onClick={() => setSelectIsOpen(false)}>
                        <Button
                          color="primary"
                          isIconOnly
                          onClick={(event) => {
                            event.stopPropagation(); // Stop event propagation
                            togglePlaySample(voice.key as "Danielle" | "Gregory" | "Ruth");
                          }}
                        >
                          <Icon
                            icon={playingVoice === voice.key ? "tabler:player-stop" : "tabler:player-play"} // Toggle icon based on playing state
                            width={20}
                            className={playingVoice === voice.key ? "animate-pulse" : undefined}
                          />
                        </Button>
                        <p>{voice.key}</p>
                        {/* Audio element for the sample */}
                        <audio
                          ref={audioRefs[voice.key]}
                          src={`/audio/${voice.key.toLowerCase()}_sample.mp3`}
                        />
                      </div>
                    </SelectItem>
                  ))}
                </Select>
                </div>
                <Spacer y={1} />
                <div className="flex flex-row items-center gap-3">
                  <p>Theme</p>
                  <Tabs
                    size="md"
                    aria-label="Theme"
                    selectedKey={theme}
                    onSelectionChange={(key: any) => setTheme(key)}
                  >
                    <Tab
                      key="light"
                      title={
                        <div className="flex items-center space-x-2">
                          <Icon icon="tabler:sun" width={25} />
                          <span>Light</span>
                        </div>
                      }
                    />
                    <Tab
                      key="dark"
                      title={
                        <div className="flex items-center space-x-2">
                          <Icon icon="tabler:moon" width={25} />
                          <span>Dark</span>
                        </div>
                      }
                    />
                    <Tab
                      key="print"
                      title={
                        <div className="flex items-center space-x-2">
                          <Icon icon="tabler:printer" width={25} />
                          <span>Print Friendly</span>
                        </div>
                      }
                    />
                  </Tabs>
                </div>
                <Spacer y={1} />
                <div className="flex flex-row items-center gap-3">
                  <p>Include Sources/References</p>
                  <Switch
                    isSelected={includeSources}
                    onChange={() => setIncludeSources(!includeSources)}
                  />
                </div>
              </ModalBody>
              <ModalFooter>
                <Button color="danger" variant="light" onPress={onClose}>
                  Close
                </Button>
                {videoUrl ? (
                  <Button
                    as="a"
                    href={videoUrl}
                    color="success"
                    download
                  >
                    Download
                  </Button>
                ) : (
                  <Button
                    color="primary"
                    onPress={handleGenerate}
                    isLoading={isGenerating}
                  >
                    Generate
                  </Button>
                )}
              </ModalFooter>
            </>
          )}
        </ModalContent>
      </Modal>
    </>
  );
}
