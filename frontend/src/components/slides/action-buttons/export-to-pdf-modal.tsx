// frontend/src/components/slides/action-buttons/export-to-pdf-modal.tsx
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
  Tab,
  Tabs,
  Switch,
  Tooltip,
  Link,
} from "@nextui-org/react";
import { Icon } from "@iconify/react";
import { exportToPDF } from "@/actions/export-to-pdf";

export function ExportToPdfModal({ presentationId }: { presentationId: string }) {
  const { isOpen, onOpen, onOpenChange } = useDisclosure();
  const [theme, setTheme] = useState<Key>("light");
  const [isExporting, setIsExporting] = useState<boolean>(false);
  const [pdfUrl, setPdfUrl] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleExport = async () => {
    setIsExporting(true);
    setError(null); // Reset error state before exporting

    try {
      const result = await exportToPDF(presentationId, theme as 'dark' | 'light' | 'print', false);

      if (result.success) {
        setPdfUrl(result.href!);
      } else {
        throw new Error(result.error);
      }
    } catch (error: any) {
      console.error("Failed to export PDF:", error);
      setError(error.message);
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
                {error && (
                  <p className="text-red-500">Error: {error}</p>
                )}
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