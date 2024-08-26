// src/components/slides/image/editable-slide-image.tsx
import NextImage from "next/image";
import { useEffect, useState } from "react";
import { Image as ImageType } from "@/utils/slide-types";
import { Icon } from "@iconify/react";
import { cn } from "@/utils/cn";
import { Slide } from "@/utils/slide-types";
import {
  Image as NextUIImage,
  Tooltip,
  useDisclosure,
} from "@nextui-org/react";
import { EditImageModal } from "./edit-image-modal";
import { ImageUploadModal } from "./image-upload-modal";
import axios from "axios";


const generateImage = async (
  presentationID: string,
  prompt: string,
  shape: string,
  style: string,
  model: string,
) => {
  
  const response = await axios.post(
    `${process.env.NEXT_PUBLIC_REST_API_URL}/slides/generate_image`,
    {
      presentationID,
      prompt,
      shape,
      style_preset: style,
      model_type: model,
    },
    {
      withCredentials: true,
    }
  );

  return response.data;
};

type SlideImageProps = {
  presentationID: string;
  setSlide: (slide: Partial<Slide>) => void;
  image?: ImageType;
  variant?: "left" | "right" | "full";
};

export function SlideImage({
  presentationID,
  setSlide,
  image,
  variant = "left",
}: SlideImageProps) {

  const imageUrl = image?.s3_key ? `https://${process.env.NEXT_PUBLIC_CLOUDFRONT_DOMAIN}/${image.s3_key}` : undefined;

  const [editing, setEditing] = useState(false);
  const [currentImage, setCurrentImage] = useState(image);
  const [loading, setLoading] = useState(false);

  const tempWidth = variant === "full" ? 1920 : 1080;
  const tempHeight = 1080;

  if (!image) {
    return null; // or return a placeholder or error message
  }

  const roundedClass =
    variant === "full"
      ? "rounded-[12px]"
      : variant === "left"
      ? "rounded-none rounded-l-[12px]"
      : variant === "right"
      ? "rounded-none rounded-r-[12px]"
      : "";

  const {
    isOpen: isEditModalOpen,
    onOpen: onEditModalOpen,
    onOpenChange: onEditModalOpenChange,
  } = useDisclosure();
  const {
    isOpen: isUploadModalOpen,
    onOpen: onUploadModalOpen,
    onOpenChange: onUploadModalOpenChange,
  } = useDisclosure();
  const [currentPrompt, setCurrentPrompt] = useState<string>(
    image.prompt || ""
  );

  const setImage = (newImage: Partial<ImageType>) => {
    setCurrentImage((prev) => ({ ...prev, ...newImage }));
    setSlide({ image: { ...currentImage, ...newImage } });
    newImage.prompt && setCurrentPrompt(newImage.prompt);
  };

  const handleReload = async () => {
    if (!currentImage?.prompt) {
      throw new Error("Prompt is required to regenerate image");
    }
    setLoading(true);
    try {
      const newImage = await generateImage(
        presentationID,
        currentImage.prompt,
        variant === "full" ? "full" : "square",
        currentImage?.style || "default",
        currentImage?.model || "sdxl",
      );
      setImage(newImage);
    } catch (error) {
      console.error("Error regenerating image:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <EditImageModal
        presentationID={presentationID}
        setImage={setImage}
        key={image.s3_key}
        currentImage={currentImage}
        isOpen={isEditModalOpen}
        onOpenChange={onEditModalOpenChange}
        currentPrompt={currentPrompt}
        setCurrentPrompt={setCurrentPrompt}
        shape={variant === "full" ? "full" : "square"}
      />
      <ImageUploadModal
        presentationID={presentationID}
        setImage={setImage}
        isOpen={isUploadModalOpen}
        onOpenChange={onUploadModalOpenChange}
        shape={variant === "full" ? "full" : "square"}
      />
      <Tooltip
        isOpen={editing}
        content={
          <div className="flex flex-row py-1">
            <Tooltip
              content="Regenerate Image"
              placement="bottom"
              offset={15}
              color="default"
            >
              <div>
                <Icon
                  icon="tabler:reload"
                  width="25"
                  height="25"
                  className={cn(
                    "text-foreground/70 hover:text-foreground mx-0.5",
                    loading && "animate-spin"
                  )}
                  onClick={handleReload}
                />
              </div>
            </Tooltip>
            <Tooltip
              content="Image AI Tools"
              placement="bottom"
              offset={15}
              color="default"
            >
              <Icon
                icon="tabler:ai"
                width="25"
                height="25"
                className="text-foreground/70 hover:text-foreground mx-0.5 scale-150"
                onClick={onEditModalOpen}
              />
            </Tooltip>
            <Tooltip
              content="Upload Image"
              placement="bottom"
              offset={15}
              color="default"
            >
              <Icon
                icon="tabler:upload"
                width="25"
                height="25"
                className="text-foreground/70 hover:text-foreground ml-0.5 mr-1"
                onClick={onUploadModalOpen}
              />
            </Tooltip>
          </div>
        }
        placement="left"
        offset={15}
        onMouseDown={(e) => e.preventDefault()}
        className="border-2 border-foreground"
      >
        <div
          tabIndex={0} // Make the div focusable
          onClick={() => setEditing(true)} // Set editing to true on click
          onBlur={() => setEditing(false)}
          className={cn(
            "relative h-full",
            roundedClass,
            editing && "cursor-pointer ring-4 ring-primary"
          )}
        >
          <NextUIImage
            src={imageUrl}
            alt={currentImage?.prompt}
            width={currentImage?.width || tempWidth}
            height={currentImage?.height || tempHeight}
            classNames={{
              img: cn("object-cover w-full h-full", roundedClass),
              wrapper: cn(roundedClass, "w-full h-full"),
            }}
            // fallbackSrc={variant === "full" ? "/1920placeholder.jpeg" : "/1080placeholder.jpeg"}
          />
          {variant == "full" && (
            <div className={cn("absolute inset-0 rounded-[15px]")}>
              <div
                className={cn(
                  "absolute inset-0 bg-gradient-to-t from-foreground/80 via-transparent to-transparent z-20 rounded-[15px]"
                )}
              ></div>
            </div>
          )}
        </div>
      </Tooltip>
    </>
  );
}