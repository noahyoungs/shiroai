"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.ViewOnlyBoxesShortBulletsSlideComponent = void 0;
const jsx_runtime_1 = require("react/jsx-runtime");
const react_1 = require("@iconify/react");
const cn_1 = require("../../../utils/cn");
const view_only_title_1 = require("./view-only-title");
const BulletItem = ({ bullet, index, allSources, slide }) => {
    return ((0, jsx_runtime_1.jsxs)("div", { className: (0, cn_1.cn)("relative flex flex-col items-start bg-background rounded-3xl p-6 h-full w-full justify-between"), children: [(0, jsx_runtime_1.jsx)("div", { className: "flex items-center justify-center h-14 w-14 bg-blue-500 rounded-full text-white font-light overflow-hidden flex-shrink-0", children: (0, jsx_runtime_1.jsx)(react_1.Icon, { className: "text-[33px]", icon: !bullet.icon
                        ? "tabler:file-unknown"
                        : bullet.icon.source === "fluent"
                            ? `fluent-emoji-high-contrast:${bullet.icon.name}`
                            : `tabler:${bullet.icon.name}` }) }), (0, jsx_runtime_1.jsxs)("div", { className: "text-start flex-none", children: [bullet.content.includes(":") ? ((0, jsx_runtime_1.jsx)(jsx_runtime_1.Fragment, { children: bullet.content
                            .split(":")
                            .map((part, partIndex) => ((0, jsx_runtime_1.jsx)("p", { className: (0, cn_1.cn)("text-foreground font-[550] overflow-hidden text-ellipsis mb-1", partIndex === 0
                                ? "text-lg leading-tight"
                                : "text-sm font-normal"), style: {
                                display: "-webkit-box",
                                WebkitLineClamp: partIndex === 0 ? 2 : 3,
                                WebkitBoxOrient: "vertical",
                            }, children: part.trim() }, String(partIndex)))) })) : ((0, jsx_runtime_1.jsx)("p", { className: "text-foreground text-lg font-[550] leading-tight", style: {
                            display: "-webkit-box",
                            WebkitLineClamp: 4,
                            WebkitBoxOrient: "vertical",
                        }, children: bullet.content })), slide.sequential && index !== slide.slide_content.length - 1 && ((0, jsx_runtime_1.jsx)("div", { className: "absolute top-1/2 -right-8 -translate-y-[16.5px]", children: (0, jsx_runtime_1.jsx)(react_1.Icon, { className: "text-[33px] text-foreground/70 ", icon: "tabler:chevron-compact-right" }) }))] })] }, index));
};
const renderSlideContent = (slide, allSources) => {
    switch (slide.slide_content.length) {
        case 2:
            return ((0, jsx_runtime_1.jsxs)("div", { className: "grid grid-rows-2 gap-8 h-full", children: [(0, jsx_runtime_1.jsx)("div", { className: "row-span-1 col-span-full my-auto", children: (0, jsx_runtime_1.jsx)(view_only_title_1.ViewOnlyTitle, { title: slide.slide_title }) }), (0, jsx_runtime_1.jsx)("div", { className: "grid grid-cols-2 gap-8 h-full row-span-1", children: slide.slide_content.map((bullet, index) => ((0, jsx_runtime_1.jsx)(BulletItem, { bullet: bullet, index: index, allSources: allSources, slide: slide }, bullet.id))) })] }));
        case 3:
            return ((0, jsx_runtime_1.jsxs)("div", { className: "grid grid-rows-2 gap-8 h-full", children: [(0, jsx_runtime_1.jsx)("div", { className: "row-span-1 col-span-full my-auto", children: (0, jsx_runtime_1.jsx)(view_only_title_1.ViewOnlyTitle, { title: slide.slide_title }) }), (0, jsx_runtime_1.jsx)("div", { className: "grid grid-cols-3 gap-8 h-full row-span-1", children: slide.slide_content.map((bullet, index) => ((0, jsx_runtime_1.jsx)(BulletItem, { bullet: bullet, index: index, allSources: allSources, slide: slide }, bullet.id))) })] }));
        case 4:
            return ((0, jsx_runtime_1.jsxs)("div", { className: "grid grid-cols-3 gap-8 h-full", children: [(0, jsx_runtime_1.jsx)("div", { className: "col-span-1 flex flex-col justify-center", children: (0, jsx_runtime_1.jsx)(view_only_title_1.ViewOnlyTitle, { title: slide.slide_title }) }), (0, jsx_runtime_1.jsx)("div", { className: "col-span-2 grid grid-cols-2 grid-rows-2 gap-8", children: slide.slide_content.map((bullet, index) => ((0, jsx_runtime_1.jsx)(BulletItem, { bullet: bullet, index: index, allSources: allSources, slide: slide }, bullet.id))) })] }));
        case 5:
            return ((0, jsx_runtime_1.jsxs)("div", { className: "grid grid-rows-2 grid-cols-3 gap-8 h-full", children: [(0, jsx_runtime_1.jsx)("div", { className: "col-span-1 row-span-1 my-auto", children: (0, jsx_runtime_1.jsx)(view_only_title_1.ViewOnlyTitle, { title: slide.slide_title }) }), slide.slide_content.map((bullet, index) => ((0, jsx_runtime_1.jsx)(BulletItem, { bullet: bullet, index: index, allSources: allSources, slide: slide }, bullet.id)))] }));
        default:
            return null;
    }
};
const ViewOnlyBoxesShortBulletsSlideComponent = ({ slide, allSources }) => {
    const testSlideContent = slide.slide_content.slice(0, 5);
    return ((0, jsx_runtime_1.jsx)("div", { className: "p-12 w-full flex-grow", children: (0, jsx_runtime_1.jsx)("div", { className: "flex justify-center w-full h-full", children: renderSlideContent(Object.assign(Object.assign({}, slide), { slide_content: testSlideContent }), allSources) }) }));
};
exports.ViewOnlyBoxesShortBulletsSlideComponent = ViewOnlyBoxesShortBulletsSlideComponent;
