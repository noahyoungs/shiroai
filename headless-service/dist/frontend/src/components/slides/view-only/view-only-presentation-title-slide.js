"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.ViewOnlyPresentationTitleSlideComponent = ViewOnlyPresentationTitleSlideComponent;
const jsx_runtime_1 = require("react/jsx-runtime");
const view_only_slide_image_1 = require("./view-only-slide-image");
const view_only_title_1 = require("./view-only-title");
function ViewOnlyPresentationTitleSlideComponent({ slide, classNames, }) {
    return ((0, jsx_runtime_1.jsxs)("div", { className: "relative overflow-visible w-full h-full aspect-video", children: [(0, jsx_runtime_1.jsx)("div", { className: "absolute mx-12 mb-3 bottom-10 z-[21] text-background/90 w-[90%]", id: "presentation-title", children: (0, jsx_runtime_1.jsx)(view_only_title_1.ViewOnlyTitle, { title: slide.slide_title, classNames: "!text-text-background/90" }) }), (0, jsx_runtime_1.jsx)(view_only_slide_image_1.ViewOnlySlideImage, { image: slide.image, variant: "full" })] }));
}
