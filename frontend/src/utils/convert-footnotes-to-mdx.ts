import { Excerpt } from "@shared-utils/database-types";

export async function convertFootnotesToMDX(
    markdown: string,
    footnotes: Record<string, Excerpt>
  ) {
    console.log("Before conversion: ", markdown);
  
    if (
      !markdown ||
      !footnotes ||
      markdown.length === 0 ||
      typeof markdown !== "string"
    ) {
      return undefined;
    }
  
    const footnoteRegex = /\\\[(\d+)\\\]/g;
    const convertedMarkdown = markdown.replace(footnoteRegex, (match, key) => {
      if (footnotes.hasOwnProperty(key)) {
        return `<Footnote key={${key}} />`;
      }
      return match;
    });
  
    // Remove escaped backslashes and angle brackets
    let converted = convertedMarkdown.replace(/\\\\/g, '\\').replace(/\\</g, '<');
  
    console.log("After conversion: ", converted);
  
    return converted;
  }
