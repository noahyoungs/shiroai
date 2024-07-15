import re
import xml.etree.ElementTree as ET
import base64
import aiohttp
import os 

from slides.mermaid.tall_shapes_lines_inference import predict_ideal_lines

HEADLESS_API_PATH = os.getenv('HEADLESS_API_PATH')

def break_string_into_lines(input_string, n):
    # replace \n and <br> with <br/>
    input_string = input_string.replace("\n", "<br/>")
    input_string = input_string.replace("<br>", "<br/>")
    
    if "<br/>" in input_string:
        return input_string

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

def process_tall_shapes(diagram):
    def replace_text(match, shape):
        node_text = match.group(2)
        if not "<br/>" in node_text:
            chars = len(node_text)
            words = len(node_text.split())
            N = predict_ideal_lines(shape, chars, words)
            modified_text = break_string_into_lines(node_text, N)
        else:
            modified_text = node_text
        return f'{match.group(1)}{modified_text}{match.group(3)}'

    patterns = [
        (r'(\(\(\(\s*")(.+?)("\s*\)\)\))', 'double_circle'), # Double circle nodes (((" ")))
        (r'(\(\(\s*")(.+?)("\s*\)\))', 'circle'),            # Circle nodes ((" "))
        (r'(\{\s*")(.+?)("\s*\})', 'diamond')                # Rhombus nodes {" "}
    ]

    for pattern, shape in patterns:
        diagram = re.sub(pattern, lambda match: replace_text(match, shape), diagram)

    diagram = re.sub(r'(<br/>\s*){2,}', '<br/>', diagram)
    
    return diagram

async def get_dimensions_from_service(diagram):
    async with aiohttp.ClientSession() as session:
        url = f"{HEADLESS_API_PATH}/mermaid-dimensions"
        async with session.post(url, json={"code": diagram}) as response:
            response_data = await response.json()
            if response.status == 200:
                return response_data['width'], response_data['height']
            else:
                raise ValueError(f"Failed to get dimensions: {response_data.get('message')}")

async def generate_svgs_from_service(diagram):
    async with aiohttp.ClientSession() as session:
        url = f"{HEADLESS_API_PATH}/mermaid"
        async with session.post(url, json={"code": diagram}) as response:
            response_data = await response.json()
            if response.status == 200:
                return response_data['lightSvg'], response_data['darkSvg']
            else:
                raise ValueError(f"Failed to generate SVGs: {response_data.get('message')}")

async def adjust_ar_with_line_breaks(diagram, target_ratio=2.4, max_iterations=10):
    iterations = 0
    aspect_ratio = 0
    adjusted_diagram = diagram
    setpoint = 2  # Start with the minimum number of lines

    width, height = await get_dimensions_from_service(diagram)
    aspect_ratio = width / height
    print(f"Initial Aspect Ratio: {aspect_ratio}")

    while iterations < max_iterations:
        if abs(aspect_ratio - target_ratio) < 0.25:
            break

        matches = re.findall(r'\"(.*?)\"', adjusted_diagram)
        new_diagram = adjusted_diagram

        for match in matches:
            new_text = break_string_into_lines(match, setpoint)
            new_diagram = new_diagram.replace(f'"{match}"', f'"{new_text}"')

        width, height = await get_dimensions_from_service(new_diagram)
        new_aspect_ratio = width / height
        print(f"Iteration {iterations + 1} (Setpoint: {setpoint}): New Aspect Ratio = {new_aspect_ratio}")

        if abs(new_aspect_ratio - target_ratio) <= abs(aspect_ratio - target_ratio):
            adjusted_diagram = new_diagram
            aspect_ratio = new_aspect_ratio
        else:
            print("New aspect ratio is worse, stopping adjustments.")
            break

        iterations += 1
        setpoint += 1

    return adjusted_diagram, aspect_ratio

async def adjust_ar_with_direction(diagram, target_ratio=2.4):
    first_line = diagram.split('\n')[0].strip()
    if not first_line.startswith('graph') and not first_line.startswith('flowchart'):
        raise ValueError("The diagram must start with 'graph' or 'flowchart'.")

    reverse = 'BT' in first_line or 'RL' in first_line

    diagram_td = diagram.replace(first_line, 'graph BT' if reverse else 'graph TD', 1)
    diagram_lr = diagram.replace(first_line, 'graph RL' if reverse else 'graph LR', 1)

    width_td, height_td = await get_dimensions_from_service(diagram_td)
    aspect_ratio_td = width_td / height_td

    width_lr, height_lr = await get_dimensions_from_service(diagram_lr)
    aspect_ratio_lr = width_lr / height_lr

    if abs(aspect_ratio_td - target_ratio) < 0.25 or abs(aspect_ratio_lr - target_ratio) < 0.25:
        if abs(aspect_ratio_td - target_ratio) < abs(aspect_ratio_lr - target_ratio):
            return diagram_td, aspect_ratio_td
        else:
            return diagram_lr, aspect_ratio_lr

    if aspect_ratio_td > target_ratio:
        diagram_td, aspect_ratio_td = await adjust_ar_with_line_breaks(diagram_td, target_ratio)
        
    if abs(aspect_ratio_td - target_ratio) < 0.25:
        return diagram_td, aspect_ratio_td

    if aspect_ratio_lr > target_ratio:
        diagram_lr, aspect_ratio_lr = await adjust_ar_with_line_breaks(diagram_lr, target_ratio)    
    
    if abs(aspect_ratio_td - target_ratio) < abs(aspect_ratio_lr - target_ratio):
        return diagram_td, aspect_ratio_td
    else:
        return diagram_lr, aspect_ratio_lr

def round_rectangles(diagram):
    # Pattern to match ["..."] but avoid [["..."]]
    # it requires that on the outer edges of [""] there is a whitespace or a word character or the end of the string
    pattern = re.compile(r'(?<=[\s\w])\["(.*?)"\](?=[\s\w]|$)')
    
    # Replace the matched pattern with ("...") using a lambda to retain the content
    diagram = pattern.sub(lambda match: f'("{match.group(1)}")', diagram)
    
    return diagram

async def process_diagram_to_svgs(diagram, adjust_ar=True):
    diagram = process_tall_shapes(diagram)
    if adjust_ar:
        diagram, _ = await adjust_ar_with_direction(diagram)
    diagram = round_rectangles(diagram)
    light_svg, dark_svg = await generate_svgs_from_service(diagram)
    return light_svg, dark_svg
