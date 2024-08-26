import React, { useState } from "react";
import {
  Modal,
  ModalContent,
  ModalHeader,
  ModalBody,
  ModalFooter,
  Button,
  useDisclosure,
  Spacer,
  Tab,
  Tabs,
  Switch,
  Tooltip,
  Link,
} from "@nextui-org/react";
import { Icon } from "@iconify/react";
import axios from "axios";
import { Key } from "react";

export function ExportToPdfModal({ presentationId }: { presentationId: string }) {
  const { isOpen, onOpen, onOpenChange } = useDisclosure();
  const [theme, setTheme] = useState<Key>("light");
  const [isExporting, setIsExporting] = useState<boolean>(false);
  const [pdfUrl, setPdfUrl] = useState<string | null>(null);

  const handleExport = async () => {
    setIsExporting(true);
    try {
      const response = await axios.post(
        `${process.env.NEXT_PUBLIC_HEADLESS_API_PATH}/generate-pdf/${presentationId}/pdf`,
        { theme, footnotes: false },
      );
      const { s3Key }  = response.data;
      const href = `https://${process.env.NEXT_PUBLIC_CLOUDFRONT_DOMAIN}/${s3Key}`
      setPdfUrl(href);
    } catch (error) {
      console.error("Failed to export PDF:", error);
    } finally {
      setIsExporting(false);
    }
  };

  return (
    <>
      <Button
        color="primary"
        startContent={<Icon icon="tabler:file-type-pdf" width={25} />}
        className="flex-grow"
        onPress={onOpen}
      >
        Export to PDF
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
                Export to PDF
              </ModalHeader>
              <ModalBody>
                <p>Export your presentation to a PDF file for download.</p>
                <Spacer y={1} />
                <div className="flex flex-row items-center gap-3">
                  <p>Theme</p>
                  <Tabs
                    size="md"
                    aria-label="Theme"
                    onSelectionChange={(key: Key) => setTheme(key)}
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
                <Switch isDisabled>Include Sources/References</Switch>
              </ModalBody>
              <ModalFooter>
                <Button color="danger" variant="light" onPress={onClose}>
                  Close
                </Button>
                {pdfUrl ? (
                  <Button
                    as={Link}
                    href={pdfUrl}
                    color="success"
                    isExternal
                    download
                  >
                    Download
                  </Button>
                ) : (
                  <Button
                    color="primary"
                    onPress={async () => {
                      await handleExport();
                    }}
                    isLoading={isExporting}
                  >
                    Export
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
