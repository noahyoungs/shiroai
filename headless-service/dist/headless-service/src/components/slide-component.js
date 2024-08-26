"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.SlideComponent = void 0;
const jsx_runtime_1 = require("react/jsx-runtime");
// View Only
const view_only_presentation_title_slide_1 = require("/Users/noahyoungs/VSCode/ai-presenter-v2/frontend/src/components/slides/view-only/view-only-presentation-title-slide");
const view_only_section_header_slide_1 = require("/Users/noahyoungs/VSCode/ai-presenter-v2/frontend/src/components/slides/view-only/view-only-section-header-slide");
const view_only_mermaid_diagram_slide_1 = require("/Users/noahyoungs/VSCode/ai-presenter-v2/frontend/src/components/slides/view-only/view-only-mermaid-diagram-slide");
const view_only_markdown_slide_1 = require("/Users/noahyoungs/VSCode/ai-presenter-v2/frontend/src/components/slides/view-only/view-only-markdown-slide");
const view_only_short_bullets_slide_pills_1 = require("/Users/noahyoungs/VSCode/ai-presenter-v2/frontend/src/components/slides/view-only/view-only-short-bullets-slide-pills");
const view_only_short_bullets_slide_boxes_1 = require("/Users/noahyoungs/VSCode/ai-presenter-v2/frontend/src/components/slides/view-only/view-only-short-bullets-slide-boxes");
const SlideComponent = (props) => {
    const { slide, allSources } = props;
    switch (slide.slide_type) {
        case "short_bullets_slide":
            return slide.layout === "list" ? ((0, jsx_runtime_1.jsx)(view_only_short_bullets_slide_pills_1.ViewOnlyPillShortBulletsSlideComponent, { slide: slide, allSources: allSources })) : ((0, jsx_runtime_1.jsx)(view_only_short_bullets_slide_boxes_1.ViewOnlyBoxesShortBulletsSlideComponent, { slide: slide, allSources: allSources }));
        case "markdown_slide":
            return ((0, jsx_runtime_1.jsx)(view_only_markdown_slide_1.ViewOnlyMarkdownSlideComponent, { slide: slide, allSources: allSources }));
        case "simple_mermaid_slide":
            return ((0, jsx_runtime_1.jsx)(view_only_mermaid_diagram_slide_1.ViewOnlySimpleMermaidSlideComponent, { slide: slide, allSources: allSources }));
        case "section_header_slide":
            return (0, jsx_runtime_1.jsx)(view_only_section_header_slide_1.ViewOnlySectionHeaderSlideComponent, { slide: slide });
        case "presentation_title_slide":
            return (0, jsx_runtime_1.jsx)(view_only_presentation_title_slide_1.ViewOnlyPresentationTitleSlideComponent, { slide: slide });
        default:
            return (0, jsx_runtime_1.jsxs)("div", { children: ["Slide type not supported: ", JSON.stringify(slide)] });
    }
};
exports.SlideComponent = SlideComponent;
