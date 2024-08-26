import React from "react";
import {
  Modal,
  ModalContent,
  ModalHeader,
  ModalBody,
  ModalFooter,
  Button,
  useDisclosure,
  Spacer,
  Textarea,
  Select,
  SelectItem,
} from "@nextui-org/react";
import { Icon } from "@iconify/react";

export function GenerateVideoModal() {
  const { isOpen, onOpen, onOpenChange } = useDisclosure();

  const voices = ["Danielle", "Gregory", "Ruth"];

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
                <Spacer y={1} />
                <Select label="Select a voice" className="max-w-xs" description="Select an AI voice for your voiceover.">
                  {voices.map((voice) => (
                    <SelectItem key={voice}>{voice}</SelectItem>
                  ))}
                </Select>
              </ModalBody>
              <ModalFooter>
                <Button color="danger" variant="light" onPress={onClose}>
                  Close
                </Button>
                <Button color="primary" onPress={onClose}>
                  Action
                </Button>
              </ModalFooter>
            </>
          )}
        </ModalContent>
      </Modal>
    </>
  );
}
