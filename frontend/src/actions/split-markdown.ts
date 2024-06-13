
/**
 * Splits a Markdown string into two parts based on a specified breakpoint type.
 * 
 * @param markdown - The Markdown string to split.
 * @param breakpointType - The breakpoint type to use for splitting the Markdown. If not provided, the highest breakpoint type present in the text will be identified.
 * @param ratioThreshold - The threshold for the split ratio. If the split ratio is more extreme than the threshold, the next breakpoint type in the hierarchy will be tried.
 * @param enableLogging - Whether to enable logging for debugging purposes.
 * @returns An array containing the first part and second part of the split Markdown.
 */
export function splitMarkdown(
  markdown: string,
  breakpointType?: string,
  ratioThreshold: number = 0.1,
  enableLogging: boolean = false
): [string, string] {
  // Split the Markdown string into an array of lines
  let lines = markdown.split("\n");

  // Special handling for single-line text
  if (lines.length === 1) {
    lines = splitTextBySentence(lines[0]);
  }

  // Identify the highest breakpoint type present in the text if not provided
  if (!breakpointType) {
    breakpointType = identifyHighestBreakpointType(lines, enableLogging);
  }
  if (enableLogging) {
    console.log("Breakpoint Type:", breakpointType);
  }

  // Group the lines based on the breakpoint type
  const groups = groupLinesByBreakpoint(lines, breakpointType);
  if (enableLogging) {
    console.log("Groups:", groups);
  }

  // Calculate the special length for each group
  const specialLengths = calculateSpecialLengths(groups);
  if (enableLogging) {
    console.log("Special Lengths:", specialLengths);
  }

  // Calculate the total special length
  const totalSpecialLength = specialLengths.reduce(
    (sum, length) => sum + length,
    0
  );

  // Calculate the ideal split point
  const idealSplitPoint = Math.floor(totalSpecialLength / 2);

  // Find the split group index
  const splitGroupIndex = findSplitGroupIndex(specialLengths, idealSplitPoint);
  if (enableLogging) {
    console.log("Split Group Index:", splitGroupIndex);
  }

  // If only one group is found or the split ratio is more extreme than the threshold,
  // try the next breakpoint type in the hierarchy

  // log groups.length
  if (
    groups.length === 1 ||
    isSplitRatioExceeded(specialLengths, splitGroupIndex, ratioThreshold)
  ) {
    enableLogging && console.log("Split ratio exceeded");
    enableLogging && console.log("Breakpoint type:", breakpointType);
    const nextBreakpointType = getNextBreakpointType(breakpointType);
    enableLogging && console.log("Next breakpoint type:", nextBreakpointType);
    if (nextBreakpointType) {
      return splitMarkdown(markdown, nextBreakpointType, ratioThreshold, enableLogging);
    }
  }

  // is the line at splitGroupIndex a table?
  if (
    groups[splitGroupIndex].some(
      (line) => line.trim().startsWith("|") && line.trim().endsWith("|")
    )
  ) {
    // gather the entire table (groups[splitGroupIndex] and all groups before and after it that are table lines)
    const tableLines = groups[splitGroupIndex].filter(
      (line) => line.trim().startsWith("|") && line.trim().endsWith("|")
    );

    let firstTableGroupIndex = splitGroupIndex;
    let lastTableGroupIndex = splitGroupIndex;

    // Collect table lines before splitGroupIndex
    for (let i = splitGroupIndex - 1; i >= 0; i--) {
      const tableRowsInGroup = groups[i].filter(
        (line) => line.trim().startsWith("|") && line.trim().endsWith("|")
      );
      if (tableRowsInGroup.length > 0) {
        tableLines.unshift(...tableRowsInGroup);
        firstTableGroupIndex = i;
      } else {
        break;
      }
    }

    // Collect table lines after splitGroupIndex
    for (let i = splitGroupIndex + 1; i < groups.length; i++) {
      const tableRowsInGroup = groups[i].filter(
        (line) => line.trim().startsWith("|") && line.trim().endsWith("|")
      );
      if (tableRowsInGroup.length > 0) {
        tableLines.push(...tableRowsInGroup);
        lastTableGroupIndex = i;
      } else {
        break;
      }
    }

    // now tableLines should contain only the lines that are part of the table
    const tableToSplit = tableLines.join("\n");

    if (enableLogging) {
      console.log("Table to split:", tableToSplit);
    }

    // collect the lines that come before the table (if any)
    const linesBeforeTable = groups
      .slice(0, firstTableGroupIndex)
      .flatMap((group) => group);

    if (enableLogging) {
      console.log("Lines before table:", linesBeforeTable);
    }

    // collect the lines that come after the table (if any)
    const linesAfterTable = groups
      .slice(lastTableGroupIndex, groups.length)
      .flatMap((group) =>
        group.filter(
          (line) => !line.trim().startsWith("|") || !line.trim().endsWith("|")
        )
      );

    if (enableLogging) {
      console.log("Lines after table:", linesAfterTable);
    }

    // Split the tableToSplit using the splitMarkdownTable function
    const [table1, table2] = splitMarkdownTable(tableToSplit);

    // Combine the split tables with the lines before and after the table
    const firstPart = linesBeforeTable.join("\n") + "\n" + table1;
    const secondPart = table2 + "\n" + linesAfterTable.join("\n");

    return [firstPart.trim(), secondPart.trim()];
  } else {
    // Split the groups into the first part and second part
    const firstPart = joinGroups(groups.slice(0, splitGroupIndex));
    const secondPart = joinGroups(groups.slice(splitGroupIndex));

    return [firstPart, secondPart];
  }
}

function getNextBreakpointType(breakpointType: string): string | undefined {
  const breakpointTypes = [
    `|`,
    "# ",
    "## ",
    "### ",
    "#### ",
    "##### ",
    "###### ",
    "blank",
    "notbullet",
    "*",
    "*\t",
    "*\t\t",
    "*\t\t\t",
    "*\t\t\t\t",
  ];

  const currentIndex = breakpointTypes.indexOf(breakpointType);
  if (currentIndex !== -1 && currentIndex < breakpointTypes.length - 1) {
    return breakpointTypes[currentIndex + 1];
  }
  return undefined;
}

function splitMarkdownTable(table: string): [string, string] {
  // Step 1: Split the text by \n and run .trim() on every line/row
  const rows = table.split("\n").map((row) => row.trim());

  // Step 2: Parse the different types of rows according to the rules
  const headerRow = rows[0];
  const separatorRow = rows[1];
  const dataRows = rows.slice(2);

  // Step 3: Calculate the middle point of all the data rows
  const midIndex = Math.floor(dataRows.length / 2);

  // Step 4: Split the data rows into two halves by the middle index
  const dataRows1 = dataRows.slice(0, midIndex);
  const dataRows2 = dataRows.slice(midIndex);

  // Step 5: Put the header row and separator row on both halves and return both tables
  const table1 = [headerRow, separatorRow, ...dataRows1].join("\n");
  const table2 = [headerRow, separatorRow, ...dataRows2].join("\n");

  return [table1, table2];
}

function splitTextBySentence(text: string): string[] {
  return text.match(/[^.!?]+[.!?]+(\s|$)/g) || [];
}

function identifyHighestBreakpointType(lines: string[], enableLogging: boolean): string {
  if (
    lines.some(
      (line) => line.trim().startsWith("|") && line.trim().endsWith("|")
    )
  ) {
    if (enableLogging) {
      console.log("Found a table");
    }
    return "|";
  } else if (lines.some((line) => line.startsWith("#"))) {
    if (enableLogging) {
      console.log("Found a line starting with #");
    }
    if (lines.some((line) => line.startsWith("# "))) {
      if (enableLogging) {
        console.log("Found a line starting with # ");
      }
      return "# ";
    } else if (lines.some((line) => line.startsWith("## "))) {
      if (enableLogging) {
        console.log("Found a line starting with ## ");
      }
      return "## ";
    } else if (lines.some((line) => line.startsWith("### "))) {
      if (enableLogging) {
        console.log("Found a line starting with ### ");
      }
      return "### ";
    } else if (lines.some((line) => line.startsWith("#### "))) {
      if (enableLogging) {
        console.log("Found a line starting with #### ");
      }
      return "#### ";
    } else if (lines.some((line) => line.startsWith("##### "))) {
      if (enableLogging) {
        console.log("Found a line starting with ##### ");
      }
      return "##### ";
    } else if (lines.some((line) => line.startsWith("###### "))) {
      if (enableLogging) {
        console.log("Found a line starting with ###### ");
      }
      return "###### ";
    }
  } else if (lines.some((line) => line.trim() === "")) {
    if (enableLogging) {
      console.log("Found an empty line");
    }
    return "blank";
  } else if (lines.some((line) => !isLineABulletPoint(line))) {
    if (enableLogging) {
      console.log("Found a line that is not a bullet point");
    }
    return "notbullet";
  } else if (lines.some((line) => isTopLevelBulletPoint(line))) {
    if (enableLogging) {
      console.log("Found a top-level bullet point");
    }
    return "*";
  } else if (lines.some((line) => isNestedBulletPoint(line, 1))) {
    if (enableLogging) {
      console.log("Found a nested bullet point at level 1");
    }
    return "*\t";
  } else if (lines.some((line) => isNestedBulletPoint(line, 2))) {
    if (enableLogging) {
      console.log("Found a nested bullet point at level 2");
    }
    return "*\t\t";
  } else if (lines.some((line) => isNestedBulletPoint(line, 3))) {
    if (enableLogging) {
      console.log("Found a nested bullet point at level 3");
    }
    return "*\t\t\t";
  } else if (lines.some((line) => isNestedBulletPoint(line, 4))) {
    if (enableLogging) {
      console.log("Found a nested bullet point at level 4");
    }
    return "*\t\t\t\t";
  }
  if (enableLogging) {
    console.log("No breakpoint type found");
  }
  return "";
}

function isLineABulletPoint(line: string): boolean {
  return (
    line.trim().startsWith("* ") ||
    line.trim().startsWith("- ") ||
    line.trim().match(/^\d+\. /) !== null
  );
}

function isTopLevelBulletPoint(line: string): boolean {
  return (
    isLineABulletPoint(line) && !line.startsWith("  ") && !line.startsWith("\t")
  );
}

function isNestedBulletPoint(line: string, level: number): boolean {
  const tabPrefix = "\t".repeat(level);
  const spacePrefix = " ".repeat(level * 2);
  return (
    isLineABulletPoint(line) &&
    (line.startsWith(tabPrefix) || line.startsWith(spacePrefix))
  );
}

function groupLinesByBreakpoint(
  lines: string[],
  breakpointType: string
): string[][] {
  const groups: string[][] = [];
  let currentGroup: string[] = [];

  for (const line of lines) {
    if (lineMatchesBreakpoint(line, breakpointType)) {
      if (currentGroup.length > 0) {
        groups.push(currentGroup);
        currentGroup = [];
      }
    }
    currentGroup.push(line);
  }

  if (currentGroup.length > 0) {
    groups.push(currentGroup);
  }

  return groups;
}

function lineMatchesBreakpoint(line: string, breakpointType: string): boolean {
  switch (breakpointType) {
    case "|":
      return line.trim().startsWith("|") && line.trim().endsWith("|");
    case "# ":
      return line.startsWith("# ");
    case "## ":
      return line.startsWith("## ");
    case "### ":
      return line.startsWith("### ");
    case "#### ":
      return line.startsWith("#### ");
    case "##### ":
      return line.startsWith("##### ");
    case "###### ":
      return line.startsWith("###### ");
    case "blank":
      return line.trim() === "";
    case "notbullet":
      return !isLineABulletPoint(line);
    case "*":
      return isTopLevelBulletPoint(line);
    case "*\t":
      return isNestedBulletPoint(line, 1);
    case "*\t\t":
      return isNestedBulletPoint(line, 2);
    case "*\t\t\t":
      return isNestedBulletPoint(line, 3);
    case "*\t\t\t\t":
      return isNestedBulletPoint(line, 4);
    default:
      return false;
  }
}

function calculateSpecialLengths(groups: string[][]): number[] {
  return groups.map((group) => {
    return group.reduce((sum, line) => sum + Math.ceil(line.length / 100), 0);
  });
}

function findSplitGroupIndex(
  specialLengths: number[],
  idealSplitPoint: number
): number {
  let closestGroupIndex = 0;
  let minDifference = Infinity;

  specialLengths.reduce((sum, length, index) => {
    const difference = Math.abs(sum - idealSplitPoint);
    if (difference < minDifference) {
      closestGroupIndex = index;
      minDifference = difference;
    }
    return sum + length;
  }, 0);

  return closestGroupIndex;
}

function joinGroups(groups: string[][]): string {
  return groups.map((group) => group.join("\n").trim()).join("\n");
}

function isSplitRatioExceeded(
  specialLengths: number[],
  splitGroupIndex: number,
  ratioThreshold: number
): boolean {
  const totalSpecialLength = specialLengths.reduce(
    (sum, length) => sum + length,
    0
  );
  const firstPartLength = specialLengths
    .slice(0, splitGroupIndex)
    .reduce((sum, length) => sum + length, 0);
  const secondPartLength = totalSpecialLength - firstPartLength;

  const ratio =
    Math.min(firstPartLength, secondPartLength) /
    Math.max(firstPartLength, secondPartLength);
  return ratio < ratioThreshold;
}

// const markdown = `
// * The diversity of BPM ranges in EDM subgenres is a key factor that contributes to the unique character and energy of each genre.\\[^1]\n  * Hard Trance typically has a BPM range of 140 to 180, creating an intense and driving energy.\\[^1]\n  * Hi NRG generally has a BPM between 120 and 140, with a common BPM of 127, giving it a high-energy and upbeat feel.\\[^2]\n  * Industrial music can have a wide range of BPMs, allowing for a more experimental and unconventional sound.\\[^3]\n  * New Beat is commonly found in the 100-115 BPM range, resulting in a slower, more hypnotic and atmospheric vibe.\\[^4]\n  * Techno music typically falls within the 120 to 150 BPM range, providing a steady, rhythmic foundation for the genre.\\[^5]\n* The BPM of an EDM track can significantly influence the overall mood and experience for the audience.\\[^1]\n  * Faster BPM ranges, such as in Hard Trance, can create a more intense and energetic atmosphere, perfect for high-energy dance floors.\\[^1]\n  * Slower BPM ranges, like in New Beat, can induce a more trance-like and introspective state, allowing the audience to get lost in the music.\\[^4]\n  * The versatility of BPM ranges across EDM subgenres enables artists to cater to a wide variety of listener preferences and moods.\\[^1]\n* Exploring the different BPM ranges in EDM subgenres can help listeners discover new and unique musical experiences.\\[^1]\n  * By understanding how the BPM contributes to the character of each genre, listeners can better appreciate the diversity and nuances within the broader EDM landscape.\\[^1]\n  * Encouraging the audience to experiment with different subgenres and their associated BPM ranges can lead to a deeper understanding and appreciation of the richness of EDM.\\[^1]
// `;

// const markdown = `
// ## Ambient Subgenres\n\n* **Ambient Dub**: A subgenre of ambient music that combines elements of dub music, characterized by its use of echo, reverb, and other studio effects.\\[^1]\n* **Dark Ambient**: A subgenre of ambient music that is characterized by its atmospheric, often unsettling, and sometimes disturbing sound, often evoking a sense of unease or tension.\\[^1]\n* **Space Music**: A subgenre of ambient music that is characterized by its expansive, celestial, and otherworldly sound, often evoking a sense of vastness and exploration.\\[^1]\n\n## Bass Music Subgenres\n\n1. **Future Bass**: A subgenre of bass music that is characterized by its use of pitched-down vocal samples, glitchy and syncopated rhythms, and a focus on low-end frequencies.\\[^2]\n2. **UK Bass**:\n   * A subgenre of bass music that originated in the UK, characterized by its heavy, distorted basslines and syncopated rhythms.\\[^2]\n   * Includes subgenres like Jungle Terror and Midtempo Bass.\\[^2]\n3. **Trap (EDM)**: A subgenre of bass music that is characterized by its use of heavy, distorted basslines, syncopated rhythms, and hip-hop-influenced production techniques.\\[^2]&#x20;
// `

// const markdown = `
// - Electro emerged in the early 1980s as a fusion of synth-pop, funk, and boogie[^1]\n    - Also called electro-funk or electro-boogie[^1]\nRandom sentence in the middle\n    - Pioneers include Ryuichi Sakamoto, Afrika Bambaataa, Zapp, D.Train, and Sinnamon[^1]\n- Electro was influenced by early hip hop, rap, and German/Japanese electropop like Kraftwerk and Yellow Magic Orchestra[^2]\n    - Iconic drum machines like the Roland TR-808 and Yamaha DX7 became key components of the electro sound[^2]\n- As the electronic sound developed, instruments like the bass guitar and drums were replaced by synthesizers and drum machines[^3]`

// const markdown = `
// ## Origins\n\n* House music originated in Chicago in the 1980s, pioneered by artists like Marshall Jefferson, Steve 'Silk' Hurley, Frankie Knuckles, and Larry Heard\\[^1]\n* It was influenced by earlier genres like disco, soul, and funk, and characterized by a steady 4/4 beat and use of drum machines like the Roland TR-808 and TR-909\\[^1]\n\n## Subgenres\n\n### Deep House\n\n* Soulful, jazzy sound with a focus on groove and melody\\[^1]\n* Characterized by lush, atmospheric pads and intricate percussion\\[^1]\n\n### Acid House\n\n* Defined by the distinctive \"acid\" sound of the Roland TB-303 bassline\\[^1]\n* Typically features a hypnotic, repetitive quality and a raw, lo-fi aesthetic\\[^1]\n\n### Progressive House\n\n* Melodic, evolving sound with longer song structures and a focus on buildups and drops\\[^2]\n* Often incorporates elements of trance and techno\\[^2]\n\n### Soulful House\n\n* Infuses house music with elements of soul and R\\&B\\[^1]\n* Characterized by soulful vocals, lush harmonies, and  a smooth, groovy feel\\[^1]
// `;

// const markdown = `
// In the depths of the Amazon rainforest, a peculiar species of butterfly, known as the Morpho butterfly, flutters gracefully among the lush foliage, its iridescent blue wings catching the dappled sunlight that filters through the dense canopy above. These magnificent creatures, with wingspans reaching up to eight inches, have captured the imagination of scientists and nature enthusiasts alike, not only for their stunning beauty but also for their unique ability to navigate through the complex maze of the rainforest using a sophisticated system of visual and sensory cues. The Morpho butterfly's wings are covered in countless tiny scales, each one a miniature marvel of evolutionary engineering, designed to reflect and scatter light in such a way that creates the illusion of a shimmering, almost ethereal blue color that seems to shift and change with every flutter. This mesmerizing display serves not only to attract potential mates but also to confuse and deter predators, who may struggle to focus on the constantly shifting patterns of light and color. However, the Morpho butterfly's true secret lies not in its wings but in its eyes, which are among the most advanced in the insect world, capable of detecting subtle changes in light, color, and motion that allow the butterfly to navigate the intricate web of the rainforest canopy with unparalleled skill and precision. Scientists have studied these remarkable creatures for decades, hoping to unlock the secrets of their visual prowess and perhaps even apply those lessons to the development of new technologies, from more efficient solar panels to more advanced camera systems. Yet for all our scientific progress, the Morpho butterfly remains a creature of mystery and wonder, a living testament to the incredible complexity and beauty of the natural world, and a reminder of how much we still have to learn from the countless marvels that surround us.`

// const markdown = `
// - Hello World!
//   - This is a nested bullet point
//   - This is another nested bullet point
//   - This is another nested bullet point
//   - This is another nested bullet point
//   - This is another nested bullet point
//   - This is another nested bullet point
//   - This is another nested bullet point
//   - This is another nested bullet point
//   - This is another nested bullet point
//   - This is another nested bullet point
//   - This is another nested bullet point
//   - This is another nested bullet point
// `

// const markdown = `
// - Hello World!
// - Hello World!
//   - This is a nested bullet point
//   - This is another nested bullet point
//   - This is another nested bullet point
//   - This is another nested bullet point
//   - This is another nested bullet point
//   - This is another nested bullet point
//   - This is another nested bullet point
//   - This is another nested bullet point
//   - This is another nested bullet point
//   - This is another nested bullet point
//   - This is another nested bullet point
//   - This is another nested bullet point
//   - This is another nested bullet point
//   - This is another nested bullet point
//   - This is another nested bullet point
//   - This is another nested bullet point
//   - This is another nested bullet point
//   - This is another nested bullet point
//   - This is another nested bullet point
//   - This is another nested bullet point
//   - This is another nested bullet point
//   - This is another nested bullet point
//   - This is another nested bullet point
//   - This is another nested bullet point
//   - This is another nested bullet point
//   - This is another nested bullet point
// `

// const markdown = `| Subgenre | Tempo Range (BPM) | Defining Musical Elements | Notable Artists/Examples |\n|----------|-------------------|---------------------------|-------------------------|\n| House | 115-135[^1] | - 4/4 drum patterns<br>- Soulful, funky basslines<br>- Repetitive vocal samples | Marshall Jefferson, Steve 'Silk' Hurley, Frankie Knuckles, Larry Heard[^1] |\n| Big Room House / EDM | 126-132[^2] | - Big progressive buildups<br>- Aggressive drops<br>- Commonly heard at festivals and concert-sized clubs | - |\n| Detroit Techno | 120-135[^3] | - Repetitive drum-machine led beats<br>- Futuristic, industrial-influenced sound<br>- Less emphasis on melody, more on repetition and electronic sounds | - |\n| Electro / Electro House | 125-130[^4] | - Heavy basslines<br>- Jackin' house beats<br>- Prominent drops<br>- Sampling and vocoder use | - |\n| Ghetto House | 115-130[^5], 150-165 (Juke)[^5] | - Lo-fi 4x4 or skipping house beats<br>- Synthesized tom-tom sounds<br>- Minimal analog synths<br>- Short, dirty-sounding vocal samples | - |\n| Handbag | 130-140[^6] | - Diva vocals<br>- House and breakbeats<br>- High-energy synths and strings | - |\n| Hard House / Hard Style | 150[^7] | - Speedy tempo<br>- Offbeat bass stabs, hoovers, horns, crowd cheering samples<br>- Drum roll-led drops | - |\n| Minimal / Minimal Techno | 125-130[^8] | - Stripped-down, raw Techno aesthetic<br>- Repetitive, minimal elements (short sounds, blips, beeps, percussion)<br>- Roland TR-808/909 drum machines | - |\n| Tech House | - | - Combination of House and Techno<br>- Raw Techno-styled kick, hi-hat, snare<br>- Soulful, jazzy House influences, minimal and dub elements | - |\n\nLorem Ipsum dolor sit amet`;

// const markdown = `
// | Header 1 | Header 2 | Header 3 | Header 4 |
// |----------|----------|----------|----------|
// | Row 1, Cell 1 | Row 1, Cell 2 | Row 1, Cell 3 | Row 1, Cell 4 |
// | Row 2, Cell 1 | Row 2, Cell 2 | Row 2, Cell 3 | Row 2, Cell 4 |`;

// const markdown = `## Key Use Cases
// ### Intelligent Virtual Assistants
// - GPT-4o can power interactive virtual assistants that understand and respond to natural language, images, and audio[^3]
// - These assistants can help with tasks like:
//   - Answering questions
//   - Providing instructions
//   - Generating content
//   - Automating workflows[^3]

// ### Multimedia Content Creation
// - GPT-4o can generate text, images, and audio to create multimedia content[^1,^3]
// - Potential use cases include:
//   - Automated video production
//   - Generative art and music
//   - Multimodal storytelling[^1,^3]

// ### Workflow Automation
// - GPT-4o's capabilities can be integrated into business workflows to automate tasks[^3]
// - Examples include:
//   - Generating reports and summaries
//   - Automating customer service interactions
//   - Streamlining document processing[^3]`

// const markdown = `## Finding the Right Medication and Dosage\n\n* ADHD medications affect each person differently[^1]\n* The first ADHD medication tried may not be the right one[^1]\n* Providers may need to try different medications and doses to find what works[^1,^2]\n* Finding the Right Medication and Dosage\n* ADHD medications affect each person differently[^1]\n* The first ADHD medication tried may not be the right one[^1]\n* Providers may need to try different medications and doses to find what works[^1,^2]\n* Finding the Right Medication and Dosage\n* ADHD medications affect each person differently[^1]\n* The first ADHD medication tried may not be the right one[^1]\n* Providers may need to try different medications and doses to find what works[^1,^2]\n* Finding the Right Medication and Dosage\n* ADHD medications affect each person differently[^1]\n* The first ADHD medication tried may not be the right one[^1]\n* Providers may need to try different medications and doses to find what works[^1,^2]`

// const [firstPart, secondPart] = splitMarkdown(markdown.trim(), undefined, 0.1, true);

// console.log("First Part:");
// console.log(firstPart);
// console.log("---");
// console.log("Second Part:");
// console.log(secondPart);
