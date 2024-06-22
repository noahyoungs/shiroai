import * as React from "react";

const PhotoReloadIcon = ({ className, ...props }) => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    width={24}
    height={24}
    fill="none"
    className={className}
    role="img"
    viewBox="0 0 24 24"
    {...props}
  >
    <path
      stroke="currentColor"
      strokeLinecap="round"
      strokeLinejoin="round"
      strokeWidth={2}
      d="M15 8h.01M13 21H6a3 3 0 0 1-3-3V6a3 3 0 0 1 3-3h12a3 3 0 0 1 3 3v7"
    />
    <path
      stroke="currentColor"
      strokeLinecap="round"
      strokeLinejoin="round"
      strokeWidth={2}
      d="m3 16 5-5c.928-.893 2.072-.893 3 0l3 3M14 14l1-1c.928-.893 2.072-.893 3 0M21.545 20.867a3.108 3.108 0 0 1-1.345.943 3.22 3.22 0 0 1-1.657.14 3.157 3.157 0 0 1-1.494-.704 2.99 2.99 0 0 1-.906-1.345 2.896 2.896 0 0 1-.056-1.603c.132-.53.411-1.014.807-1.402a3.14 3.14 0 0 1 1.442-.8c1.516-.375 3.085.377 3.664 1.78"
    />
    <path
      stroke="currentColor"
      strokeLinecap="round"
      strokeLinejoin="round"
      strokeWidth={2}
      d="M22 16v2h-2"
    />
  </svg>
);

export default PhotoReloadIcon;
