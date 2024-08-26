"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.ViewOnlySectionHeaderSlideComponent = ViewOnlySectionHeaderSlideComponent;
const jsx_runtime_1 = require("react/jsx-runtime");
const view_only_slide_image_1 = require("./view-only-slide-image");
const view_only_title_1 = require("./view-only-title");
function ViewOnlySectionHeaderSlideComponent({ slide, classNames, }) {
    const isImageLeft = slide.image_position !== "right"; // Defaults to left if image_position is undefined or any other value except 'right'
    return ((0, jsx_runtime_1.jsx)("div", { className: "flex flex-row relative overflow-visible w-full aspect-video", children: isImageLeft ? ((0, jsx_runtime_1.jsxs)(jsx_runtime_1.Fragment, { children: [(0, jsx_runtime_1.jsx)("div", { className: "aspect-square h-full", children: (0, jsx_runtime_1.jsx)(view_only_slide_image_1.ViewOnlySlideImage, { image: slide.image, variant: slide.image_position }) }), (0, jsx_runtime_1.jsx)("div", { className: "flex-auto flex flex-col justify-center p-12", children: (0, jsx_runtime_1.jsx)(view_only_title_1.ViewOnlyTitle, { title: slide.slide_title, classNames: classNames }) })] })) : ((0, jsx_runtime_1.jsxs)(jsx_runtime_1.Fragment, { children: [(0, jsx_runtime_1.jsx)("div", { className: "flex-auto flex flex-col justify-center p-12", children: (0, jsx_runtime_1.jsx)(view_only_title_1.ViewOnlyTitle, { title: slide.slide_title, classNames: classNames }) }), (0, jsx_runtime_1.jsx)("div", { className: "aspect-square h-full overflow-hidden", children: (0, jsx_runtime_1.jsx)(view_only_slide_image_1.ViewOnlySlideImage, { image: slide.image, variant: slide.image_position }) })] })) }));
}
