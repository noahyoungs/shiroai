"use strict";
// frontend/src/components/slides/view-only/view-only-markdown-slide.tsx
"use client";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.ViewOnlyMarkdownSlideComponent = ViewOnlyMarkdownSlideComponent;
const jsx_runtime_1 = require("react/jsx-runtime");
const markdown_to_jsx_1 = __importDefault(require("markdown-to-jsx"));
const view_only_title_1 = require("./view-only-title");
const cn_1 = require("../../../utils/cn");
function ViewOnlyMarkdownSlideComponent({ slide, allSources, }) {
    return ((0, jsx_runtime_1.jsxs)("div", { className: "p-12 pb-0 flex flex-col w-full overflow-scroll flex-grow", children: [(0, jsx_runtime_1.jsx)("div", { className: "flex-none", children: (0, jsx_runtime_1.jsx)(view_only_title_1.ViewOnlyTitle, { title: slide.slide_title }) }), (0, jsx_runtime_1.jsxs)(jsx_runtime_1.Fragment, { children: [(0, jsx_runtime_1.jsx)("div", { className: "flex-auto min-h-6" }), (0, jsx_runtime_1.jsx)("div", { className: (0, cn_1.cn)("flex justify-start w-full flex-shrink max-w-none prose dark:prose-invert", slide.slide_content.prose_class || "prose-sm"), children: typeof slide.slide_content.content === "string" ? ((0, jsx_runtime_1.jsx)(markdown_to_jsx_1.default, { options: {
                                //   renderRule(next, node, renderChildren, state) {
                                //     // @ts-ignore
                                //     if (node.type === RuleType.footnoteReference) {
                                //       const footnoteKeys = node.text.split(",^");
                                //       return (
                                //         <Footnote
                                //           footnoteKeys={footnoteKeys}
                                //           slide={slide}
                                //           allSources={allSources}
                                //         />
                                //       );
                                //     }
                                //     return next();
                                //   },
                                wrapper: ({ children }) => ((0, jsx_runtime_1.jsx)("div", { id: "prose-container", className: "px-1", children: children })),
                                forceWrapper: true,
                            }, children: slide.slide_content.content })) : ((0, jsx_runtime_1.jsx)("div", { className: "flex justify-center items-center h-[300px]", children: (0, jsx_runtime_1.jsxs)("p", { className: "text-center text-foreground dark:text-background", children: ["Error: Slide content is not a string ", (0, jsx_runtime_1.jsx)("br", {}), "Slide content is ", typeof slide.slide_content.content, " ", (0, jsx_runtime_1.jsx)("br", {}), "Slide content is", " ", JSON.stringify(slide.slide_content.content)] }) })) }), (0, jsx_runtime_1.jsx)("div", { className: "flex-auto min-h-12" })] })] }));
}
