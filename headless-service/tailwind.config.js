const plugin = require('tailwindcss/plugin');
const round = (num) =>
  num
    .toFixed(7)
    .replace(/(\.[0-9]+?)0+$/, "$1")
    .replace(/\.0$/, "");
const rem = (px) => `${round(px / 16)}rem`;
const em = (px, base) => `${round(px / base)}em`;

module.exports = {
  content: [
    './src/**/*.{js,jsx,ts,tsx}',
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
  plugins: [
    require('@tailwindcss/typography'),
    plugin(function ({ addVariant, e }) {
      addVariant('nobg', ({ modifySelectors, separator }) => {
        modifySelectors(({ className }) => {
          return `.nobg .${e(`nobg${separator}${className}`)}`;
        });
      });
    }),
  ],
  darkMode: 'selector',
};
