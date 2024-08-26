import React from "react";
import { Image as ImageType } from "../../../utils/slide-types";
import { cn } from "../../../utils/cn";
import { Image as NextUIImage } from "@nextui-org/react";

type ViewOnlySlideImageProps = {
  image?: ImageType;
  variant?: "left" | "right" | "full";
  thumbnail?: boolean;
};

export function ViewOnlySlideImage({
  image,
  variant = "left",
  thumbnail = false,
}: ViewOnlySlideImageProps) {
  let imageUrl: string | undefined;

  if (image?.s3_key) {
    const s3KeyParts = image.s3_key.split('.');
    if (thumbnail) {
      const extension = s3KeyParts.pop();
      const baseName = s3KeyParts.join('.');
      imageUrl = `https://${process.env.NEXT_PUBLIC_CLOUDFRONT_DOMAIN}/${baseName}_thumbnail.${extension}`;
    } else {
      imageUrl = `https://${process.env.NEXT_PUBLIC_CLOUDFRONT_DOMAIN}/${image.s3_key}`;
    }
  }

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

  return (
    <div
      className={cn(
        "relative",
        roundedClass
      )}
    >
      <NextUIImage
        src={imageUrl}
        alt={image.prompt}
        width={image?.width || tempWidth}
        height={image?.height || tempHeight}
        classNames={{
          img: cn(roundedClass),
          wrapper: cn(roundedClass, "w-full"),
        }}
      />
      {variant === "full" && (
        <div className={cn("absolute inset-0 rounded-[15px]")}>
          <div
            className={cn(
              "absolute inset-0 bg-gradient-to-t from-foreground/80 via-transparent to-transparent z-20 rounded-[15px]"
            )}
          ></div>
        </div>
      )}
    </div>
  );
}