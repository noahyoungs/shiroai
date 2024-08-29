// frontend/src/components/slides/view-only/view-only-slide-image.tsx
import React from "react";
import { cn } from "../utils/cn";
import { Image as ImageType } from "../utils/slide-types";

type ViewOnlySlideImageProps = {
  image?: ImageType;
  variant?: "left" | "right" | "full";
  signedUrlSuffix?: string;
};

export function ViewOnlySlideImage({
  image,
  variant = "left",
  signedUrlSuffix = "",
}: ViewOnlySlideImageProps) {

  const imageUrl = image?.s3_key ? `https://${process.env.CLOUDFRONT_DOMAIN}/${image.s3_key}${signedUrlSuffix}` : undefined;

  const tempWidth = variant === "full" ? 1920 : 1080;
  const tempHeight = 1080;

  if (!image) {
    return null; // or return a placeholder or error message
  }

  return (
    <div
      className={"relative"}
    >
      <div className="relative h-screen">
      <img
        src={imageUrl}
        alt={image.prompt}
        width={image?.width || tempWidth}
        height={image?.height || tempHeight}
        className="absolute inset-0 w-full h-full object-cover"
      />
      </div>
      {variant === "full" && (
        <div className={cn("absolute inset-0")}>
          <div
            className={cn(
              "absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-transparent z-20"
            )}
          ></div>
        </div>
      )}
    </div>
  );
}
