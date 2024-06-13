# clean_markdown.py
import unittest
import re

def combine_footnotes(markdown: str) -> str:
    footnote_regex = re.compile(r"(\[\^\d+\])(\s*,?\s*(\[\^\d+\]))*")

    def combine(match: re.Match) -> str:
        footnotes = match.group(0)
        footnote_numbers = re.findall(r'\[\^(\d+)\]', footnotes)
        combined_footnotes = ','.join(f'^{num}' for num in footnote_numbers)
        return f"[{combined_footnotes}]"

    return footnote_regex.sub(combine, markdown)

def clean_markdown(markdown: str, title: str) -> str:
    markdown = markdown.strip()
    title_markdown = f"# {title}"
    markdown_lines = markdown.split("\n")
    
    if markdown_lines and title_markdown in markdown_lines[0]:
        markdown = "\n".join(markdown_lines[1:])

    markdown = markdown.replace("<br>", "<br/>")
    markdown = combine_footnotes(markdown)

    lines = markdown.split("\n")
    cleaned_lines = []
    for i, line in enumerate(lines):
        if line.startswith("#"):
            # Add a blank line before and after the heading
            if i > 0 and lines[i-1].strip() != "":
                cleaned_lines.append("")
            cleaned_lines.append(line)
            if i < len(lines) - 1 and lines[i+1].strip() != "":
                cleaned_lines.append("")
        else:
            cleaned_lines.append(line)

    cleaned_lines = "\n".join(cleaned_lines).strip()
    return cleaned_lines

class TestCleanMarkdown(unittest.TestCase):
    def test_remove_title(self):
        title = "My Title"
        markdown = f"# {title}\nThis is the content."
        expected_output = "This is the content."
        self.assertEqual(clean_markdown(markdown, title), expected_output)

    def test_replace_br_tags(self):
        markdown = "Line 1<br>Line 2"
        expected_output = "Line 1<br/>Line 2"
        self.assertEqual(clean_markdown(markdown, ""), expected_output)

    def test_combine_footnotes(self):
        markdown = "This is a test.[^1][^2]"
        expected_output = "This is a test.[^1,^2]"
        self.assertEqual(clean_markdown(markdown, ""), expected_output)

    def test_full_clean_markdown(self):
        title = "My Title"
        markdown = f"# {title}\nThis is a test.[^1][^2]<br>Another line.[^3] [^4]"
        expected_output = "This is a test.[^1,^2]<br/>Another line.[^3,^4]"
        self.assertEqual(clean_markdown(markdown, title), expected_output)
        
    def test_clean_markdown_table_with_br(self):
        markdown = """\
# My Table            

| Column 1 | Column 2 |
|----------|----------|
| Row 1    | Value 1<br>Value 2 |"""
        expected_output = """\
| Column 1 | Column 2 |
|----------|----------|
| Row 1    | Value 1<br/>Value 2 |"""
        self.assertEqual(clean_markdown(markdown, "My Table"), expected_output)

    def test_heading_spacing(self):
        markdown = """\
## Challenges in Ensuring Aircraft Safety

- Whistleblowers like Paredes wanted to "help the company do better" and ensure aircraft safety[^5]
- However, they faced difficulties in getting their concerns addressed, with Paredes feeling "threatened" and "retaliated against"[^6]
- The suicide note of whistleblower John Barnett included the line "Whistleblowers protection is f—– up too!", highlighting the inadequacies of whistleblower protections[^7]
## Emotional Toll and Fears

- The deaths of fellow whistleblowers have been deeply impactful, with Paredes saying "It's discouraging to lose people – not just friends, but friends who are with you in this battle"[^8]
- Paredes' mother has been "scared" about the situation, reflecting the personal and emotional toll on whistleblowers and their families[^9]"""
        
        expected_output = """\
## Challenges in Ensuring Aircraft Safety

- Whistleblowers like Paredes wanted to "help the company do better" and ensure aircraft safety[^5]
- However, they faced difficulties in getting their concerns addressed, with Paredes feeling "threatened" and "retaliated against"[^6]
- The suicide note of whistleblower John Barnett included the line "Whistleblowers protection is f—– up too!", highlighting the inadequacies of whistleblower protections[^7]

## Emotional Toll and Fears

- The deaths of fellow whistleblowers have been deeply impactful, with Paredes saying "It's discouraging to lose people – not just friends, but friends who are with you in this battle"[^8]
- Paredes' mother has been "scared" about the situation, reflecting the personal and emotional toll on whistleblowers and their families[^9]"""

        self.assertEqual(clean_markdown(markdown, "foo"), expected_output)
    
    maxDiff = None

if __name__ == "__main__":
    unittest.main()
    