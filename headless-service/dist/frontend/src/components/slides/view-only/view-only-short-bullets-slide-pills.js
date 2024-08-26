"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.ViewOnlyPillShortBulletsSlideComponent = ViewOnlyPillShortBulletsSlideComponent;
const jsx_runtime_1 = require("react/jsx-runtime");
const react_1 = require("@iconify/react");
const react_2 = __importDefault(require("react"));
const cn_1 = require("../../../utils/cn");
const view_only_title_1 = require("./view-only-title");
const BulletItem = ({ content, excerptText, source, icon, chevron, allBulletsShort, index, slide, }) => {
    return ((0, jsx_runtime_1.jsxs)("li", { className: "relative", children: [(0, jsx_runtime_1.jsx)("div", { className: (0, cn_1.cn)("flex items-center justify-between bg-background rounded-full py-1.5 pl-1.5 pr-6"), children: (0, jsx_runtime_1.jsxs)("div", { className: "flex flex-row flex-grow items-center", children: [(0, jsx_runtime_1.jsx)("div", { className: "flex flex-none items-center justify-center h-12 w-12 bg-blue-500 rounded-full text-white font-light overflow-hidden", children: (0, jsx_runtime_1.jsx)(react_1.Icon, { className: "text-[33px]", icon: !icon
                                    ? "tabler:file-unknown"
                                    : icon.source === "fluent"
                                        ? `fluent-emoji-high-contrast:${icon.name}`
                                        : `tabler:${icon.name}` }) }), (0, jsx_runtime_1.jsx)("span", { className: "text-foreground pl-4 text-base font-[550]", children: content })] }) }), chevron && ((0, jsx_runtime_1.jsx)("div", { className: (0, cn_1.cn)("absolute -translate-y-1", "right-1/2 translate-x-1/2"), children: (0, jsx_runtime_1.jsx)(react_1.Icon, { icon: "tabler:chevron-compact-down", className: "text-foreground/60 text-[33px]" }) }))] }));
};
function ViewOnlyPillShortBulletsSlideComponent({ slide, allSources, }) {
    const allBulletsShort = slide.slide_content.every((bullet) => bullet.content.length <= 50);
    return ((0, jsx_runtime_1.jsx)("div", { className: "p-12 w-full flex-grow flex flex-col", children: allBulletsShort ? ((0, jsx_runtime_1.jsxs)("div", { className: "flex flex-row w-full h-full px-24", children: [(0, jsx_runtime_1.jsx)("div", { className: "w-1/3 flex items-center justify-center", children: (0, jsx_runtime_1.jsx)(view_only_title_1.ViewOnlyTitle, { title: slide.slide_title }) }), (0, jsx_runtime_1.jsx)("div", { className: "w-2/3 flex justify-center flex-grow", children: (0, jsx_runtime_1.jsx)("ul", { className: "flex flex-col justify-center gap-6 h-full max-w-max", children: slide.slide_content.map((bullet, index) => {
                            var _a;
                            return ((0, jsx_runtime_1.jsx)(react_2.default.Fragment, { children: (0, jsx_runtime_1.jsx)(BulletItem, { content: bullet.content, excerptText: (_a = bullet.excerpt) === null || _a === void 0 ? void 0 : _a.text, source: allSources &&
                                        allSources.find((source) => { var _a; return source.id === ((_a = bullet.excerpt) === null || _a === void 0 ? void 0 : _a.source_id); }), icon: bullet.icon, chevron: slide.sequential &&
                                        index != slide.slide_content.length - 1, allBulletsShort: allBulletsShort, index: index, slide: slide }) }, bullet.id));
                        }) }) })] })) : ((0, jsx_runtime_1.jsxs)(jsx_runtime_1.Fragment, { children: [(0, jsx_runtime_1.jsx)("div", { className: "flex-none w-full", children: (0, jsx_runtime_1.jsx)(view_only_title_1.ViewOnlyTitle, { title: slide.slide_title }) }), (0, jsx_runtime_1.jsx)("div", { className: "flex justify-center w-full flex-grow", children: (0, jsx_runtime_1.jsx)("ul", { className: "flex flex-col justify-evenly gap-6 max-w-max my-8", children: slide.slide_content.map((bullet, index) => {
                            var _a;
                            return ((0, jsx_runtime_1.jsx)(react_2.default.Fragment, { children: (0, jsx_runtime_1.jsx)(BulletItem, { content: bullet.content, excerptText: (_a = bullet.excerpt) === null || _a === void 0 ? void 0 : _a.text, source: allSources &&
                                        allSources.find((source) => { var _a; return source.id === ((_a = bullet.excerpt) === null || _a === void 0 ? void 0 : _a.source_id); }), icon: bullet.icon, chevron: slide.sequential &&
                                        index != slide.slide_content.length - 1, allBulletsShort: allBulletsShort, index: index, slide: slide }) }, bullet.id));
                        }) }) })] })) }));
}
