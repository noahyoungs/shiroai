import React, { useState } from "react";
import { Key } from "@react-types/shared";
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
  Slider,
  Textarea,
} from "@nextui-org/react";
import { Icon } from "@iconify/react";
import { styles } from "@/utils/script-styles";
import humanizeDuration from "humanize-duration";
import { toast } from "sonner";
import { ToastProgress } from "@/components/toast-progress";

type AddScriptModalProps = {
  onGenerate: (style: number, customStyle?: string, maxChars?: number) => void;
};

export function AddScriptModal({ onGenerate }: AddScriptModalProps) {
  const { isOpen, onOpen, onOpenChange } = useDisclosure();
  const [selectedStyleKey, setSelectedStyleKey] = useState("0");
  const [customStyle, setCustomStyle] = useState("");
  const [maxLength, setMaxLength] = useState(500);

  const handleGenerate = () => {
    onGenerate(Number(selectedStyleKey), undefined, maxLength);
    toast(<ToastProgress progress_value={0} message="Generating presentation script..." />, {
      id: "script-gen",
      duration: Infinity,
    });
    onOpenChange();
  };

  const approxWords = Math.round(maxLength / 4.7);
  const approxSentences = Math.round(maxLength / 94);
  const approxSeconds = Math.round(maxLength / 12.6667);
  const humanizedSpeechDuration = humanizeDuration(approxSeconds * 1000, {
    units: ["m", "s"],
    round: true,
    conjunction: " and ",
  });

  return (
    <>
      <Button
        color="secondary"
        startContent={<Icon icon="tabler:script-plus" width={25} />}
        className="flex-grow"
        onPress={onOpen}
      >
        Add Script
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
                Add Script
              </ModalHeader>
              <ModalBody>
                <p>
                  This action adds a script to your presentation. The script can
                  be used to generate a narrated video of your presentation, or
                  you can use it as a reference while presenting.
                </p>
                <Spacer y={1} />
                {/* <p>Key: {selectedStyleKey} Type: {typeof selectedStyleKey}</p> */}
                <Select
                  label="Select a style"
                  items={styles}
                  fullWidth
                  onSelectionChange={(keys: Set<Key> | "all") => {
                    if (keys === "all") throw new Error("Unexpected value");
                    setSelectedStyleKey(keys.values().next().value as string);
                  }}
                  selectionMode="single"
                  selectedKeys={new Set([selectedStyleKey])}
                  disallowEmptySelection
                >
                  {(style) => (
                    <SelectItem key={style.key} textValue={style.name}>
                      <div className="flex flex-col gap-0.5 p-2">
                        <div className="flex flex-row gap-2">
                          <Icon icon={style.icon} className="w-6 h-6" />
                          <span className="font-semibold text-large mb-1 p-0">
                            {style.name}
                          </span>
                        </div>
                        {style.key !== "-1" ? (
                          <>
                            <span className="text-small text-default-500">
                              <strong>Tone:</strong> {style.tone}
                            </span>
                            <span className="text-small text-default-500">
                              <strong>Language:</strong> {style.language}
                            </span>
                          </>
                        ) : (
                          <span className="text-small text-default-500">
                            {style.description}
                          </span>
                        )}
                      </div>
                    </SelectItem>
                  )}
                </Select>
                {selectedStyleKey == "-1" && (
                  <Textarea
                    label="Define your Custom Style"
                    description="Add instructions to define your own style. You can specify writing tone, language, verbosity, etc."
                    fullWidth
                    value={customStyle}
                    onValueChange={setCustomStyle}
                  />
                )}
                <Spacer y={1} />
                <Slider
                  label="Max Character Length per Slide"
                  step={100}
                  maxValue={2000}
                  minValue={100}
                  defaultValue={500}
                  onChangeEnd={(length: number | number[]) => {
                    if (Array.isArray(length))
                      throw new Error("Unexpected value");
                    setMaxLength(length);
                  }}
                  size="lg"
                />
                <p className="text-default-500 text-small -mt-2">
                  Approximately {approxWords}{" "}
                  {approxWords === 1 ? "word" : "words"}, {approxSentences}{" "}
                  {approxSentences === 1 ? "sentence" : "sentences"}, or{" "}
                  {humanizedSpeechDuration} of speech per slide.
                </p>
              </ModalBody>
              <ModalFooter>
                <Button color="danger" variant="light" onPress={onClose}>
                  Close
                </Button>
                <Button
                  color="primary"
                  onPress={handleGenerate}
                >
                  Generate
                </Button>
              </ModalFooter>
            </>
          )}
        </ModalContent>
      </Modal>
    </>
  );
}
