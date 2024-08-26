// headless-service/src/utils/split-markdown.ts
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
  