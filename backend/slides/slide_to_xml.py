from slides.slide_models import Slide, Topic
from typing import List

slide_type_descriptions = {
    'short_bullets_slide': 'Icon Node Slide (This slide type has a title and 2-5 nodes, each with an icon and a short text description (<=80 chars). The nodes can be arranged in a list or a grid, and arrows can be displayed between the nodes to indicate sequentiality. The layout and arrangement of the title and nodes are determined by the content and number of nodes.)',
    'markdown_slide': 'Markdown Slide (A slide with a title and markdown content. The title is displayed above the markdown content. The markdown content typically includes either headings and bullet points or a table. Images are not supported. Icons are not supported, but emojis can be used.)',
    'section_header_slide': 'Section Header Slide (A slide with a section title and an image. The image can be positioned on the left or right side of the slide.)',
    'presentation_title_slide': 'Presentation Title Slide (A slide with the presentation title and an image. The image is displayed as the background of the entire slide, and the title is overlaid on top of it.)',
    'simple_mermaid_slide': 'Mermaid Diagram Slide (A slide with a title and a mermaid diagram. The title is displayed right above the mermaid diagram.)',
}

slide_type_descriptions_script = {
    'short_bullets_slide': 'Icon Node Slide (This slide type has a title and 2-5 nodes, each with an icon and a short text description)',
    'markdown_slide': 'Markdown Slide (A slide with a title and markdown content. The title is displayed above the markdown content.)',
    'section_header_slide': 'Section Header Slide (A slide with a section title and an image.) This slide marks the beginning of a new section in the presentation.',
    'presentation_title_slide': 'Presentation Title Slide (A slide with the presentation title and an image. The image is displayed as the background of the entire slide, and the title is overlaid on top of it.)',
    'simple_mermaid_slide': 'Mermaid Diagram Slide (A slide with a title and a mermaid diagram. The title is displayed right above the mermaid diagram.)',
}

def slide_content_to_xml(current_slide: Slide, all_topics: List[Topic]):
    topic_titles_d = {topic.id: topic.title for topic in all_topics}
    
    if current_slide.slide_type == 'presentation_title_slide':
        subtopic = "N/A"
    elif current_slide.slide_type == 'section_header_slide':
        subtopic = current_slide.slide_title
    else:
        try:
            subtopic = topic_titles_d[current_slide.topic_id]
        except KeyError:
            print(f"Error: Topic ID {current_slide.topic_id} not found in topic list. Slide type: {current_slide.slide_type}.")
            subtopic = "Unknown"
    
    try:
        xml_content = "<slide>\n"
        xml_content += f"  <subtopic>{subtopic}</subtopic>\n"
        xml_content += f"  <title>{current_slide.slide_title}</title>\n"
        xml_content += f"  <description>{slide_type_descriptions_script.get(current_slide.slide_type, 'Custom Slide')}</description>\n"
        if current_slide.slide_type == 'short_bullets_slide':
            xml_content += "  <content>\n"
            for item in current_slide.slide_content:
                xml_content += f"    <bullet-point>\n"
                xml_content += f"      <icon>{item.icon.name if item.icon and item.icon.name else 'Icon'}</icon>\n"
                xml_content += f"      <text>{item.content}</text>\n"
                xml_content += f"    </bullet-point>\n"
            xml_content += "  </content>\n"
        elif current_slide.slide_type == 'markdown_slide':
            xml_content += "  <content>\n"
            xml_content += f"    <markdown>{current_slide.slide_content['content']}</markdown>\n"
            xml_content += "  </content>\n"
        elif current_slide.slide_type == 'simple_mermaid_slide':
            xml_content += "  <content>\n"
            xml_content += f"    <mermaid-diagram>{current_slide.slide_content['mermaid_code']}</mermaid-diagram>\n"
            xml_content += "  </content>\n"
        elif current_slide.slide_type in ['section_header_slide', 'presentation_title_slide']:
            xml_content += "  <image>\n"
            xml_content += f"    <description>{current_slide.image.prompt}</description>\n"
            xml_content += "  </image>\n"
        
        xml_content += "</slide>"
        return xml_content
    except AttributeError:
        # Log the error for debugging purposes
        print(f"Error processing slide: {current_slide}. Slide will be omitted.")
        return ""

def slide_to_xml(current_slide: Slide):
    try:
        xml_content = f"<slide type='{current_slide.slide_type}'>\n"
        xml_content += f"  <title>{current_slide.slide_title}</title>\n"
        
        if current_slide.slide_type == 'short_bullets_slide':
            xml_content += "  <content>\n"
            for item in current_slide.slide_content:
                xml_content += f"    <bullet-point>\n"
                xml_content += f"      <icon>{item.icon.name if item.icon and item.icon.name else 'Icon'}</icon>\n"
                xml_content += f"      <text>{item.content}</text>\n"
                xml_content += f"    </bullet-point>\n"
            xml_content += "  </content>\n"
        elif current_slide.slide_type == 'markdown_slide':
            xml_content += "  <content>\n"
            xml_content += f"    <markdown>{current_slide.slide_content['content']}</markdown>\n"
            xml_content += "  </content>\n"
        elif current_slide.slide_type == 'simple_mermaid_slide':
            xml_content += "  <content>\n"
            xml_content += f"    <mermaid-diagram>{current_slide.slide_content['mermaid_code']}</mermaid-diagram>\n"
            xml_content += "  </content>\n"
        elif current_slide.slide_type in ['section_header_slide', 'presentation_title_slide']:
            xml_content += "  <image>\n"
            xml_content += f"    <prompt>{current_slide.image.prompt}</prompt>\n"
            xml_content += "  </image>\n"
        
        xml_content += "</slide>"
        return xml_content
    except AttributeError:
        # Log the error for debugging purposes
        print(f"Error processing slide: {current_slide}. Slide will be omitted.")
        return ""

def slides_to_xml(slides: List[Slide]):
    xml_output = "<slides>\n"
    xml_output += "\n".join([slide_to_xml(slide) for slide in slides if slide_to_xml(slide) != ""])
    xml_output += "\n</slides>"
    return xml_output