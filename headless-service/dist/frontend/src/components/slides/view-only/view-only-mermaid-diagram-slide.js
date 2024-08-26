"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.ViewOnlySimpleMermaidSlideComponent = ViewOnlySimpleMermaidSlideComponent;
const jsx_runtime_1 = require("react/jsx-runtime");
const next_themes_1 = require("next-themes");
require("../mermaid-styles.css");
const view_only_title_1 = require("./view-only-title");
const SvgRenderer = ({ svgString }) => {
    const sanitizedSvgString = svgString;
    return ((0, jsx_runtime_1.jsx)("div", { className: "w-full flex flex-row justify-center max-h-[50vh]", id: "mermaid-svg-container", dangerouslySetInnerHTML: { __html: sanitizedSvgString } }));
};
function ViewOnlySimpleMermaidSlideComponent({ slide, allSources, }) {
    const { theme } = (0, next_themes_1.useTheme)();
    const dark = theme === "dark";
    return ((0, jsx_runtime_1.jsx)(jsx_runtime_1.Fragment, { children: (0, jsx_runtime_1.jsxs)("div", { className: "flex flex-col p-12 w-full flex-grow", children: [(0, jsx_runtime_1.jsx)("div", { className: "flex-none", children: (0, jsx_runtime_1.jsx)(view_only_title_1.ViewOnlyTitle, { title: slide.slide_title }) }), (0, jsx_runtime_1.jsx)("div", { className: "flex-grow min-h-6" }), (0, jsx_runtime_1.jsx)("div", { className: "flex-none", onClick: () => console.log(slide.slide_content.mermaid_code), children: (0, jsx_runtime_1.jsx)(SvgRenderer, { svgString: dark
                            ? slide.slide_content.dark_svg
                            : slide.slide_content.light_svg }) }), (0, jsx_runtime_1.jsx)("div", { className: "flex-grow min-h-1" })] }) }));
}
