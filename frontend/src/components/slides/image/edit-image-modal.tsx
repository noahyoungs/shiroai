// edit-image-modal.tsx
import { useState } from "react";
import { Icon } from "@iconify/react";
import { Image as ImageType } from "@/utils/slide-types";
import {
  Modal,
  ModalContent,
  ModalHeader,
  ModalBody,
  ModalFooter,
  useDisclosure,
  Tooltip,
  Button,
  Textarea,
  Autocomplete,
  AutocompleteItem,
  RadioGroup,
  Radio,
  Select,
  SelectItem,
  Spinner,
} from "@nextui-org/react";
import { stabilityStyles, dalleStyles } from "./style-preset-options";
import NextImage from "next/image";
import axios from "axios";
import { cn } from "@/utils/cn";

type SlideImageModalProps = {
  presentationID: string;
  setImage: (image: ImageType) => void;
  currentImage?: ImageType;
  isOpen: boolean;
  onOpenChange: (open: boolean) => void;
  currentPrompt: string;
  setCurrentPrompt: (prompt: string) => void;
  shape: "full" | "square";
};

export function EditImageModal({
  presentationID,
  setImage,
  currentImage,
  isOpen,
  onOpenChange,
  currentPrompt,
  setCurrentPrompt,
  shape,
}: SlideImageModalProps) {
  const [model, setModel] = useState(currentImage?.model || "sdxl");
  const [negativePrompt, setNegativePrompt] = useState(
    currentImage?.negative_prompt || ""
  );
  const [style, setStyle] = useState(currentImage?.style || "default");
  const [loading, setLoading] = useState(false);

  const generateImage = async () => {
    const styleToUpload: string =
      model !== "dalle"
        ? stabilityStyles.some(
            (stabilityStyle) => stabilityStyle.value === style
          )
          ? style
          : "default"
        : dalleStyles.some((dalleStyle) => dalleStyle.value === style)
        ? style
        : "default";

    setLoading(true);
    try {
      const response = await axios.post(
        `${process.env.NEXT_PUBLIC_REST_API_URL}/slides/generate_image`,
        {
          presentationID,
          prompt: currentPrompt,
          shape: shape,
          style_preset: styleToUpload,
          model_type: model,
          negative_prompt: model !== "dalle" ? negativePrompt : undefined,
        },
        {
          withCredentials: true,
        }
      );

      setImage(response.data);
    } catch (error) {
      console.error("Error generating image:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
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
              Edit Image
            </ModalHeader>
            <ModalBody>
              <RadioGroup
                label="Image Model"
                orientation="horizontal"
                description="Select the AI model to use for generating the image."
                value={model}
                onValueChange={setModel}
                isRequired
              >
                <Radio value="sdxl" description="powered by Stability AI">
                  Stable Diffusion XL
                </Radio>
                <Radio value="core" description="powered by Stability AI">
                  Stable Image Core
                </Radio>
                <Radio value="dalle" description="powered by OpenAI">
                  DALL·E 3{" "}
                </Radio>
              </RadioGroup>
              {model == "dalle" && (
                <p>
                  Note: DALL·E 3 will take the prompt below and
                  "automatically re-write it for safety reasons, and to add more
                  detail". For example, it will remove brand names and named public figures. Please use one of the other models to avoid this.
                </p>
              )}
              <Textarea
                label="Prompt"
                value={currentPrompt}
                onValueChange={setCurrentPrompt}
                description={
                  "Enter a detailed description of the image you'd like to see, including specific elements, colors, and styles."
                }
                fullWidth
                isRequired
              />
              <Textarea
                label="Negative Prompt"
                value={
                  model === "dalle" ? "Not supported by DALL·E" : negativePrompt
                }
                onValueChange={setNegativePrompt}
                placeholder="Ugly, looks bad, messy, etc."
                description="Specify any unwanted elements, colors, or styles to exclude from the generated image."
                fullWidth
                isDisabled={model === "dalle"}
              />
              {model === "dalle" ? (
                <Select
                  items={dalleStyles}
                  variant="flat"
                  label="Style"
                  labelPlacement="inside"
                  fullWidth
                  shouldCloseOnBlur
                  isClearable={false}
                  selectedKey={
                    dalleStyles.some((dalleStyle) => dalleStyle.value === style)
                      ? style
                      : "default"
                  }
                  onSelectionChange={setStyle}
                  selectionMode="single"
                  description="Specify a style preset that guides the image model towards a particular style."
                >
                  {(style) => (
                    <SelectItem key={style.value} textValue={style.name}>
                      <div className="flex gap-2 items-center">
                        <div className="rounded-lg overflow-hidden w-[60px] h-[60px] flex-none">
                          <NextImage
                            src={style.image}
                            alt={style.name}
                            width={240}
                            height={240}
                            className="transition-transform duration-300 hover:scale-[4.0]"
                            placeholder="blur"
                          />
                        </div>
                        <div className="flex flex-col">
                          <span className="text-small">{style.name}</span>
                          <span className="text-tiny text-default-400 text-wrap whitespace-normal">
                            {style.description}
                          </span>
                        </div>
                      </div>
                    </SelectItem>
                  )}
                </Select>
              ) : (
                <Autocomplete
                  defaultItems={stabilityStyles}
                  variant="flat"
                  label="Style"
                  placeholder="Select a style"
                  labelPlacement="inside"
                  fullWidth
                  shouldCloseOnBlur
                  isClearable={false}
                  selectedKey={
                    stabilityStyles.some(
                      (stabilityStyle) => stabilityStyle.value === style
                    )
                      ? style
                      : "default"
                  }
                  onSelectionChange={setStyle}
                  description="Specify a style preset that guides the image model towards a particular style."
                >
                  {(style) => (
                    <AutocompleteItem key={style.value} textValue={style.name}>
                      <div className="flex gap-2 items-center">
                        <div className="rounded-lg overflow-hidden w-[60px] h-[60px] flex-none">
                          <NextImage
                            src={style.image}
                            alt={style.name}
                            width={240}
                            height={240}
                            className="transition-transform duration-300 hover:scale-[4.0]"
                            placeholder="blur"
                          />
                        </div>
                        <div className="flex flex-col">
                          <span className="text-small">{style.name}</span>
                          <span className="text-tiny text-default-400 text-wrap whitespace-normal">
                            {style.description}
                          </span>
                        </div>
                      </div>
                    </AutocompleteItem>
                  )}
                </Autocomplete>
              )}
            </ModalBody>
            <ModalFooter>
              <Button color="danger" variant="light" onPress={onClose}>
                Cancel
              </Button>
              <Button
                color="primary"
                onPress={async () => {
                  await generateImage();
                  onClose();
                }}
                isLoading={loading}
              >
                Generate
              </Button>
            </ModalFooter>
          </>
        )}
      </ModalContent>
    </Modal>
  );
}
