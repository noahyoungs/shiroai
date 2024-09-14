//image-upload-modal.tsx
import React, { useState } from "react";
import Cropper, { Area } from "react-easy-crop";
import Dropzone from "react-dropzone";
import { getCroppedImg } from "@/utils/crop-image";
import {
  Modal,
  ModalContent,
  ModalHeader,
  ModalBody,
  ModalFooter,
  Button,
  Card,
  CardBody,
} from "@nextui-org/react";
import { Icon } from "@iconify/react";
import { Slide } from "@shared-utils/database-types";
import { set } from "lodash";
import { Image as ImageType } from "@shared-utils/database-types";


type ImageUploadModalProps = {
  presentationID: string;
  setImage: (image: ImageType) => void;
  isOpen: boolean;
  onOpenChange: (open: boolean) => void;
  shape: "full" | "square";
};

export function ImageUploadModal({
  presentationID,
  setImage,
  isOpen,
  onOpenChange,
  shape,
}: ImageUploadModalProps) {
  const [uploadBufferImage, setUploadBufferImage] = useState<File | null>(null);
  const [croppedArea, setCroppedArea] = useState<Area | null>(null);
  const [crop, setCrop] = useState({ x: 0, y: 0 });
  const [zoom, setZoom] = useState(1);
  const [uploading, setUploading] = useState(false);

  const onDrop = (acceptedFiles: File[]) => {
    setUploadBufferImage(acceptedFiles[0]);
  };

  const handleCropComplete = (
    croppedAreaPercentage: Area,
    croppedAreaPixels: Area
  ) => {
    setCroppedArea(croppedAreaPixels);
  };

  const handleUpload = async () => {
    if (uploadBufferImage && croppedArea) {
      setUploading(true);
      const croppedImage = await getCroppedImg(uploadBufferImage, croppedArea);
      const formData = new FormData();
      formData.append("file", croppedImage);
      formData.append("presentationID", presentationID);
      formData.append("shape", shape);

      try {
        const response = await fetch("/api/upload_image", {
          method: "POST",
          body: formData,
        });

        if (!response.ok) {
          throw new Error("Upload failed");
        }

        const data = await response.json();
        console.log("Upload successful. Data:", data);
        data.type = "user";
        setImage(data);
        setUploading(false);
        setUploadBufferImage(null);
      } catch (error) {
        console.error("Error uploading image:", error);
        // Handle error (e.g., show an error message to the user)
      }
    }
  };

  return (
    <Modal
      isOpen={isOpen}
      onOpenChange={onOpenChange}
      closeButton={<Icon icon="tabler:x" width={40} height={40} />}
      classNames={{
        base: "h-[80vh]",
        closeButton: "top-3 right-3 w-[40px] h-[40px] p-0.5",
      }}
      size="3xl"
      scrollBehavior="inside"
      disableAnimation
    >
      <ModalContent>
        {(onClose) => (
          <>
            <ModalHeader className="flex flex-col gap-1">
              {uploadBufferImage ? 'Crop' : 'Upload'} Image
            </ModalHeader>
            <ModalBody>
              {uploadBufferImage ? (
                <div className="relative h-[80vh]">
                  <Cropper
                    image={URL.createObjectURL(uploadBufferImage)}
                    crop={crop}
                    zoom={zoom}
                    aspect={shape === "full" ? 16 / 9 : 1}
                    onCropChange={setCrop}
                    onCropComplete={handleCropComplete}
                    onZoomChange={setZoom}
                  />
                </div>
              ) : (
                <div className="flex flex-col justify-center items-center h-[75vh]">
                  <Dropzone onDrop={onDrop} accept={{'image/*': ['.jpeg', '.jpg', '.png', '.webp']}} maxFiles={1}>
                    {({ getRootProps, getInputProps }) => (
                      <div
                        {...getRootProps()}
                        className="flex justify-center items-center"
                      >
                        <input {...getInputProps()} />
                        <Card className="bg-content2 rounded-lg overflow-hidden border shadow-inner">
                          <CardBody className="p-12 flex flex-col items-center ">
                            <div className="flex space-x-4 mb-4">
                              <Icon
                                icon="tabler:drag-drop-2"
                                width={40}
                                height={40}
                                className="text-foreground/50"
                              />
                              <Icon
                                icon="tabler:upload"
                                width={40}
                                height={40}
                                className="text-foreground/50"
                              />
                            </div>
                            <p className="text-foreground text-center">
                              Drag 'n' drop an image here, or click to select an image
                            </p>
                          </CardBody>
                        </Card>
                      </div>
                    )}
                  </Dropzone>
                </div>
              )}
            </ModalBody>

            <ModalFooter>
              <Button color="danger" variant="light" onPress={onClose}>
                Close
              </Button>
              {uploadBufferImage && (
                <>
                  <Button
                    color="warning"
                    variant="ghost"
                    onPress={() => setUploadBufferImage(null)}
                  >
                    Clear
                  </Button>
                  <Button
                    color="primary"
                    onPress={async () => {
                      await handleUpload();
                      onClose();
                    }}
                    isLoading={uploading}
                  >
                    Upload
                  </Button>
                </>
              )}
            </ModalFooter>
          </>
        )}
      </ModalContent>
    </Modal>
  );
}
