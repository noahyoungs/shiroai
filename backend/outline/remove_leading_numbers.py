import re
import unittest

def remove_leading_numbers(text):
    # Adjusted regular expression to match leading numbers (including decimals) followed by a period and optional space,
    # ensuring the dot is not escaped by a backslash.
    pattern = r'^\d+(?:\.\d+)*\s+|^\d+(?<!\\)\.\s*'
    return re.sub(pattern, '', text)

class TestRemoveLeadingNumbers(unittest.TestCase):

    def test_remove_leading_numbers(self):
        test_cases = {
            "9. A healthy model": "A healthy model",
            "9 A healthy model": "A healthy model",
            "9.1 A healthy model": "A healthy model",
            "11 A healthy model": "A healthy model",
            "11.1 A healthy model": "A healthy model",
            "1234.5678 Some text": "Some text",
            "42. Another example": "Another example",
            "5.6.7 Complex example": "Complex example",
            "1234. Another complex example": "Another complex example",
            "No leading numbers": "No leading numbers",
            "": "",
            r"9\. Not a number": r"9\. Not a number",
            r"11\.1 Escaped dot example": r"11\.1 Escaped dot example",
            r"1234\.5678 Another escaped dot example": r"1234\.5678 Another escaped dot example",
            "My age is 9. Next year I will turn 10.": "My age is 9. Next year I will turn 10.",
            "8. My age is 9. Next year I will turn 10.": "My age is 9. Next year I will turn 10."
        }

        for input_text, expected_output in test_cases.items():
            with self.subTest(input_text=input_text, expected_output=expected_output):
                self.assertEqual(remove_leading_numbers(input_text), expected_output)

if __name__ == '__main__':
    unittest.main()