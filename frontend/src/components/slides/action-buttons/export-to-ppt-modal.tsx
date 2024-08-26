import React from "react";
import { Modal, ModalContent, ModalHeader, ModalBody, ModalFooter, Button, useDisclosure } from "@nextui-org/react";
import { Icon } from "@iconify/react";

export function ExportToPptModal() {
  const { isOpen, onOpen, onOpenChange } = useDisclosure();

  return (
    <>
      <Button
        color="primary"
        startContent={<Icon icon="tabler:file-type-ppt" width={25} />}
        className="flex-grow"
        onPress={onOpen}
      >
        Export to PPTX
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
              <ModalHeader className="flex flex-col gap-1">Export to PPTX</ModalHeader>
              <ModalBody></ModalBody>
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
