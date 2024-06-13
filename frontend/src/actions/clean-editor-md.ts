export function cleanMarkdown(
  markdown: string,
  enableLogging: boolean = false
): string {
  markdown = markdown.trim();
  if (!markdown || markdown.length === 0) {
    enableLogging && console.log("Can't clean markdown because markdown is empty");
    return "";
  }
  enableLogging && console.log("Cleaning markdown: ", markdown);

  let escaped = markdown.replace(/\\\[/g, "[");

  enableLogging && console.log("Escaped footnotes: ", escaped);

  // const combineFootnotes = (markdown: string) => {
  //   // Regular expression to match footnotes patterns with optional spaces
  //   const footnoteRegex = /(\[\^\d+\])\s*(\[\^\d+\])+/g;

  //   // Function to combine the footnotes
  //   const combine = (match: string) => {
  //     return match.replace(/\]\s*\[/g, ",").replace(/\[|\]/g, "");
  //   };

  //   // Replace the found footnote patterns with the combined format
  //   return markdown.replace(footnoteRegex, (match) => `[${combine(match)}]`);
  // };

  // let footnotesCombined = combineFootnotes(escaped);

  // enableLogging && console.log("Combined footnotes: ", footnotesCombined);

  // replace &#x20; with space
  escaped = escaped.replace(/&#x20;/g, " ");

  return escaped;
}
