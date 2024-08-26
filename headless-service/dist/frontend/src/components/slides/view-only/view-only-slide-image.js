"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.ViewOnlySlideImage = ViewOnlySlideImage;
const jsx_runtime_1 = require("react/jsx-runtime");
const cn_1 = require("../../../utils/cn");
const react_1 = require("@nextui-org/react");
function ViewOnlySlideImage({ image, variant = "left", }) {
    const imageUrl = (image === null || image === void 0 ? void 0 : image.s3_key) ? `https://${process.env.NEXT_PUBLIC_CLOUDFRONT_DOMAIN}/${image.s3_key}` : undefined;
    const tempWidth = variant === "full" ? 1920 : 1080;
    const tempHeight = 1080;
    if (!image) {
        return null; // or return a placeholder or error message
    }
    const roundedClass = variant === "full"
        ? "rounded-[12px]"
        : variant === "left"
            ? "rounded-none rounded-l-[12px]"
            : variant === "right"
                ? "rounded-none rounded-r-[12px]"
                : "";
    return ((0, jsx_runtime_1.jsxs)("div", { className: (0, cn_1.cn)("relative", roundedClass), children: [(0, jsx_runtime_1.jsx)(react_1.Image, { src: imageUrl, alt: image.prompt, width: (image === null || image === void 0 ? void 0 : image.width) || tempWidth, height: (image === null || image === void 0 ? void 0 : image.height) || tempHeight, classNames: {
                    img: (0, cn_1.cn)(roundedClass),
                    wrapper: (0, cn_1.cn)(roundedClass, "w-full"),
                } }), variant === "full" && ((0, jsx_runtime_1.jsx)("div", { className: (0, cn_1.cn)("absolute inset-0 rounded-[15px]"), children: (0, jsx_runtime_1.jsx)("div", { className: (0, cn_1.cn)("absolute inset-0 bg-gradient-to-t from-foreground/80 via-transparent to-transparent z-20 rounded-[15px]") }) }))] }));
}
