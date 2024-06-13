import re
import unittest

def break_string_into_lines(input_string, n):
    # Find the ideal split points by dividing the length of the input string by N
    ideal_split_points = [round(i * len(input_string) / n) for i in range(1, n)]
    
    # Find the indices of all spaces in the input string
    allowed_split_points = [i for i, char in enumerate(input_string) if char == " "]
    
    # Find the closest allowed split point to each ideal split point
    final_split_points = []
    for ideal in ideal_split_points:
        if not allowed_split_points:
            break
        closest = min(allowed_split_points, key=lambda x: abs(x - ideal))
        final_split_points.append(closest)
        allowed_split_points = [point for point in allowed_split_points if point > closest]

    # Split the lines at the final split points and fix the whitespace
    lines = []
    previous_index = 0
    for index in final_split_points:
        lines.append(input_string[previous_index:index].strip())
        previous_index = index
    lines.append(input_string[previous_index:].strip())

    return "<br/>".join(lines)

def process_tall_shapes(diagram, N):
    def replace_text(match):
        node_text = match.group(2)
        if not "<br/>" in node_text:
            modified_text = break_string_into_lines(node_text, N)
        else:
            modified_text = node_text
        return f'{match.group(1)}{modified_text}{match.group(3)}'

    # Patterns for circle, double circle, and rhombus nodes
    patterns = [
        r'(\(\(\(\s*")(.+?)("\s*\)\)\))', # Double circle nodes (((" ")))
        r'(\(\(\s*")(.+?)("\s*\)\))',     # Circle nodes ((" "))
        r'(\{\s*")(.+?)("\s*\})'          # Rhombus nodes {" "}
    ]

    for pattern in patterns:
        diagram = re.sub(pattern, replace_text, diagram)

    # Replace multiple sequences of <br/><br/> with a single <br/>
    diagram = re.sub(r'(<br/>\s*){2,}', '<br/>', diagram)

    return diagram

class TestProcessTallShapes(unittest.TestCase):
    def setUp(self):
        self.diagram = '''\
flowchart TD
    A["The Neurobiology of Adolescent Decision-Making"]
    B{"Differences in Cognitive Processes between Adolescents and Adults"}
    B -- "Adolescents' cognitive processes are not due to lack of logic or reasoning" --> C["Immaturity of psychosocial capacities in adolescents (impulse control, emotion regulation, delayed gratification, resistance to peer pressure)"]
    B -- "Adolescents and Adults" --> D["Adolescents' cognitive processes are not due to lack of logic or reasoning"]
    E["Interaction between Socioemotional Brain Network and Cognitive-Control Network"]
    F["Socioemotional network changes quickly and abruptly during puberty"]
    G["Cognitive-control network matures more gradually"]
    H["Imbalance in development of these two networks"]
    I["Heightened reward response to risky behaviors in adolescents"]
    E --> F --> H
    E --> G --> H
    H --> I
    J["Adolescents' Difficulty in Adjusting Beliefs to Negative Information"]
    K{"Adolescents' response to positive and negative information"}
    K -- "Negative Information" --> L["Adolescents have more difficulty adjusting beliefs in response to negative information"]
    K -- "Positive Information" --> M["Contributes to engagement in risky behaviors"]
    J --> K
    N((("Increased Adolescent Risk-Taking")))
    J --> N
    I --> N'''

    def test_process_tall_shapes(self):
        modified_diagram = process_tall_shapes(self.diagram, 4)
        print(modified_diagram)  # Debugging: print the modified diagram to see what changex
    
        expected = '''\
flowchart TD
    A["The Neurobiology of Adolescent Decision-Making"]
    B{"Differences in<br/>Cognitive<br/>Processes<br/>between<br/>Adolescents<br/>and Adults"}
    B -- "Adolescents' cognitive processes are not due to lack of logic or reasoning" --> C["Immaturity of psychosocial capacities in adolescents (impulse control, emotion regulation, delayed gratification, resistance to peer pressure)"]
    B -- "Adolescents and Adults" --> D["Adolescents' cognitive processes are not due to lack of logic or reasoning"]
    E["Interaction between Socioemotional Brain Network and Cognitive-Control Network"]
    F["Socioemotional network changes quickly and abruptly during puberty"]
    G["Cognitive-control network matures more gradually"]
    H["Imbalance in development of these two networks"]
    I["Heightened reward response to risky behaviors in adolescents"]
    E --> F --> H
    E --> G --> H
    H --> I
    J["Adolescents' Difficulty in Adjusting Beliefs to Negative Information"]
    K{"Adolescents'<br/>response to<br/>positive and<br/>negative<br/>information"}
    K -- "Negative Information" --> L["Adolescents have more difficulty adjusting beliefs in response to negative information"]
    K -- "Positive Information" --> M["Contributes to engagement in risky behaviors"]
    J --> K
    N((("<br/>Increased<br/>Adolescent<br/>Risk-Taking")))
    J --> N
    I --> N'''
        self.assertEqual(modified_diagram, expected)

if __name__ == '__main__':
    unittest.main()
