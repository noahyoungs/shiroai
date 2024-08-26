styles = [
    {
        "name": "Default Style",
        "tone": "Balanced, clear, and straightforward.",
        "content": "Provides essential notes with clear instructions and main points for each slide, without embellishments.",
        "example": "Introduce AI in education. Highlight key benefits: personalization, efficiency. Conclude with future trends."
    },
    {
        "name": "Detailed Guide Style",
        "tone": "Instructive, thorough, and supportive.",
        "content": "Provides step-by-step instructions, cues for gestures, and detailed explanations for each slide.",
        "example": "Start by greeting the audience with a warm smile. Introduce the topic with enthusiasm: 'Today, we’re exploring the transformative impact of AI on education.' Pause for a moment after mentioning the key point. Use a hand gesture to emphasize 'transformative impact.' Move on to the next slide when you notice nods of understanding."
    },
    {
        "name": "Bullet Point Style",
        "tone": "Concise, focused, and to the point.",
        "content": "Contains key points or prompts that guide the speaker’s flow without detailed explanations.",
        "example": "- AI in education: key benefits.\n- Personalization.\n- Efficiency.\n- Future trends.\n- Next slide: Challenges of AI."
    },
    {
        "name": "Reminder Style",
        "tone": "Subtle, simple, and supportive.",
        "content": "Includes brief reminders of important elements like pace, eye contact, and transitions.",
        "example": "Remember to maintain eye contact with the audience. Slow down when explaining the next point. Transition smoothly to the next slide."
    },
    {
        "name": "Conversational Style",
        "tone": "Relaxed, informal, and engaging.",
        "content": "Mimics a natural conversation, with prompts for casual language and interaction with the audience.",
        "example": "So, here’s the deal—AI is changing everything in education, right? Let’s talk about how. Feel free to ask the audience: 'Have any of you seen AI in action in your own classrooms?' Encourage a quick show of hands."
    },
    {
        "name": "Prompt Style",
        "tone": "Interactive, questioning, and engaging.",
        "content": "Encourages interaction with the audience through questions and prompts.",
        "example": "Ask the audience: 'What do you think are the biggest challenges of using AI in education?' Wait for responses before moving on. Prompt discussion based on their answers."
    },
    {
        "name": "Motivational Style",
        "tone": "Uplifting, positive, and energetic.",
        "content": "Focuses on inspirational messages and motivating the audience throughout the presentation.",
        "example": "Encourage the audience: 'Imagine a world where every student has access to personalized learning. That’s the power of AI!' Use an enthusiastic tone to inspire."
    },
    {
        "name": "Minimalist Style",
        "tone": "Brief, focused, and essential.",
        "content": "Provides only the most crucial notes, minimizing words to keep the speaker on track.",
        "example": "AI in Education.\n- Personalization.\n- Efficiency.\n- Challenges.\n- Future."
    }
]

def generate_xml_for_style(style_index: int) -> str:
    try: 
        style = styles[style_index]
    except IndexError:
        return "Invalid style index."
    
    xml_string = f"<style>{style['name']}</style>\n"
    xml_string += f"<tone>{style['tone']}</tone>\n"
    xml_string += f"<content>{style['content']}</content>\n"
    xml_string += f"<example>{style['example']}</example>\n"
    return xml_string