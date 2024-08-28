import json
from dynamodb import get_presentation, get_all_slides

def lambda_handler(event, context):
    """Lambda function handler for processing a presentation request."""
    
    # Extract presentation_id from the event
    presentation_id = event['presentation_id']
    
    # Retrieve the presentation details from DynamoDB
    presentation = get_presentation(presentation_id, attributes=['topic'])
    
    if presentation and 'topic' in presentation:
        topic = presentation['topic']
        message = f"Topic for presentation ID {presentation_id} is '{topic}'."
    else:
        message = f"Presentation ID {presentation_id} not found or 'topic' attribute missing."

    slides = get_all_slides(presentation_id, ['script'])
    if slides:
        message += f" Presentation has {len(slides)} slides."
        scripts = [slide.get('script', '') for slide in slides]
        if all(len(script) > 0 for script in scripts):
            message += " All slides have scripts."
        else:
            message += " Not all slides have scripts."
    else:
        message += " No slides found for presentation."
    
    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": message,
        }),
    }