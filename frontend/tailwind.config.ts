import type { Config } from "tailwindcss";
import { nextui } from "@nextui-org/react";

const round = (num: number) =>
  num
    .toFixed(7)
    .replace(/(\.[0-9]+?)0+$/, "$1")
    .replace(/\.0$/, "");
const rem = (px: number) => `${round(px / 16)}rem`;
const em = (px: number, base: number) => `${round(px / base)}em`;

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
    "../node_modules/@nextui-org/theme/dist/**/*.{js,ts,jsx,tsx}", // monorepo root node_modules
  ],
  theme: {
    extend: {
      typography: {
        '2xl': {
          css: [
            {
              h1: {
                fontSize: em(36, 24),
              },
              h2: {
                fontSize: em(30, 24),
              },
              h3: {
                fontSize: rem(24),
              }
            }
          ],
        },
      },
    },
  },
  darkMode: "class",
  plugins: [
    nextui(),
    require("@tailwindcss/line-clamp"),
    require("@tailwindcss/typography"),
  ],
};
export default config;
