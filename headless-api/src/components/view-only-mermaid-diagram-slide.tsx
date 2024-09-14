import { SimpleMermaidSlide } from "@shared-utils/database-types";
// import "../mermaid-styles.css";
import { ViewOnlyTitle } from "./view-only-title";

const SvgRenderer = ({ svgString }: { svgString: string }) => {
  const sanitizedSvgString = svgString;
  return (
    <div
      className="w-full flex flex-row justify-center max-h-[50vh]"
      id="mermaid-svg-container"
      dangerouslySetInnerHTML={{ __html: sanitizedSvgString }}
    />
  );
};

type ViewOnlySimpleMermaidSlideComponentProps = {
  slide: SimpleMermaidSlide;
  allSources?: any[];
  dark? : boolean;
};

export function ViewOnlySimpleMermaidSlideComponent({
  slide,
  allSources,
  dark = false,
}: ViewOnlySimpleMermaidSlideComponentProps) {

  return (
    <>
      <div className="flex flex-col p-12 w-full h-full">
        <div className="flex-none">
          <ViewOnlyTitle title={slide.slide_title} />
        </div>

        {/* Vertical centering: */}
        <div className="flex-grow min-h-6"></div>
          <div
            className="flex-none"
            onClick={() => console.log(slide.slide_content.mermaid_code)}
          >
            <SvgRenderer
              svgString={
                dark
                  ? slide.slide_content.dark_svg
                  : slide.slide_content.light_svg
              }
            />
          </div>

          <div className="flex-grow min-h-1"></div>
        </div>
    </>
  );
}
