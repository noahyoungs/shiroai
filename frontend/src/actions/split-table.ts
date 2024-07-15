function splitMarkdownTable(table: string): [string, string] {
    // Step 1: Split the text by \n and run .trim() on every line/row
    const rows = table.split('\n').map(row => row.trim());
  
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
    const table1 = [headerRow, separatorRow, ...dataRows1].join('\n');
    const table2 = [headerRow, separatorRow, ...dataRows2].join('\n');
  
    return [table1, table2];
  }
  
  // Test cases
  const testCases = [
    `
      | Header 1 | Header 2 | Header 3 | Header 4 |
      |----------|----------|----------|----------|
      | Row 1, Cell 1 | Row 1, Cell 2 | Row 1, Cell 3 | Row 1, Cell 4 |
      | Row 2, Cell 1 | Row 2, Cell 2 | Row 2, Cell 3 | Row 2, Cell 4 |
    `,
    `
      | A | B | C | D | E |
      |---|---|---|---|---|
      | 1 | 2 | 3 | 4 | 5 |
      | 6 | 7 | 8 | 9 | 10 |
      | 11 | 12 | 13 | 14 | 15 |
    `,
    `| Subgenre | Tempo Range (BPM) | Defining Musical Elements | Notable Artists/Examples |\n|----------|-------------------|---------------------------|-------------------------|\n| House | 115-135[^1] | - 4/4 drum patterns<br>- Soulful, funky basslines<br>- Repetitive vocal samples | Marshall Jefferson, Steve 'Silk' Hurley, Frankie Knuckles, Larry Heard[^1] |\n| Big Room House / EDM | 126-132[^2] | - Big progressive buildups<br>- Aggressive drops<br>- Commonly heard at festivals and concert-sized clubs | - |\n| Detroit Techno | 120-135[^3] | - Repetitive drum-machine led beats<br>- Futuristic, industrial-influenced sound<br>- Less emphasis on melody, more on repetition and electronic sounds | - |\n| Electro / Electro House | 125-130[^4] | - Heavy basslines<br>- Jackin' house beats<br>- Prominent drops<br>- Sampling and vocoder use | - |\n| Ghetto House | 115-130[^5], 150-165 (Juke)[^5] | - Lo-fi 4x4 or skipping house beats<br>- Synthesized tom-tom sounds<br>- Minimal analog synths<br>- Short, dirty-sounding vocal samples | - |\n| Handbag | 130-140[^6] | - Diva vocals<br>- House and breakbeats<br>- High-energy synths and strings | - |\n| Hard House / Hard Style | 150[^7] | - Speedy tempo<br>- Offbeat bass stabs, hoovers, horns, crowd cheering samples<br>- Drum roll-led drops | - |\n| Minimal / Minimal Techno | 125-130[^8] | - Stripped-down, raw Techno aesthetic<br>- Repetitive, minimal elements (short sounds, blips, beeps, percussion)<br>- Roland TR-808/909 drum machines | - |\n| Tech House | - | - Combination of House and Techno<br>- Raw Techno-styled kick, hi-hat, snare<br>- Soulful, jazzy House influences, minimal and dub elements | - |`,

  ];
  
  testCases.forEach((testCase, index) => {
    const [table1, table2] = splitMarkdownTable(testCase.trim());
  
    console.log(`Test Case ${index + 1}:`);
    console.log('Original Table:');
    console.log(testCase.trim());
    console.log('Table 1:');
    console.log(table1);
    console.log('Table 2:');
    console.log(table2);
    console.log('---');
  });