styles = [
    {
        "name": "Default Style",
        "tone": "Balanced, clear, and straightforward.",
        "language": "Neutral, simple, and direct, with clear explanations and a focus on the key points without embellishment.",
        "example": "Today, we're going to discuss the role of AI in education. We'll start by looking at current AI technologies and how they're being used in classrooms. After that, we'll explore the benefits and challenges of integrating AI into educational systems."
    },
    {
        "name": "Formal/Academic Style",
        "tone": "Professional, polished, and objective.",
        "language": "Formal, precise, with no contractions or colloquialisms.",
        "example": "Good morning, everyone. Today, we will explore the implications of artificial intelligence in modern education. First, we will examine the current state of AI technologies. Next, we will discuss their applications in educational settings, followed by an analysis of potential challenges and ethical considerations."
    },
    {
        "name": "Conversational Style",
        "tone": "Friendly, engaging, and approachable.",
        "language": "Casual, with contractions, and rhetorical questions to engage the audience.",
        "example": "Hey, everyone! So, AI in education—pretty cool, right? Let's dive into what it actually means. First up, how are schools using AI today? We'll check out some examples and talk about what this could mean for the future of learning."
    },
    {
        "name": "Storytelling Style",
        "tone": "Narrative, engaging, and personal.",
        "language": "Descriptive, focusing on vivid imagery and emotions, often using first-person perspective.",
        "example": "Let me tell you a story about how AI changed a classroom forever. It all started with a teacher who was struggling to keep up with her students' needs. But then, something extraordinary happened. An AI system stepped in, and what unfolded next transformed not just the classroom, but the lives of every student in it."
    },
    {
        "name": "Persuasive Style",
        "tone": "Assertive, convincing, and motivational.",
        "language": "Direct, with strong verbs and impactful statements, often using second-person to engage the audience.",
        "example": "Artificial intelligence isn't just the future—it's the present. And if we don't embrace it in our educational systems now, we'll be left behind. Imagine a world where every student receives personalized education, where no one is left behind. This is not just possible; it’s essential. We need to act now to integrate AI into every classroom."
    },
    {
        "name": "Analytical Style",
        "tone": "Logical, structured, and detailed.",
        "language": "Technical, with detailed explanations and logical connectors, often supported by data.",
        "example": "In 2023, the use of AI in education grew by 25%, driven by advancements in machine learning algorithms. This growth can be attributed to three main factors: the increased availability of educational datasets, the development of more sophisticated AI models, and the rising demand for personalized learning experiences."
    },
    {
        "name": "Humorous Style",
        "tone": "Light-hearted, witty, and entertaining.",
        "language": "Playful, with jokes, puns, and informal expressions to keep the audience entertained.",
        "example": "You know, when I was in school, the closest thing we had to AI was the teacher's pet. But now, AI is the teacher's pet! Seriously though, AI is doing some amazing things in classrooms. Let's take a look at how it's turning every student into a straight-A student—well, almost!"
    },
    {
        "name": "Inspirational Style",
        "tone": "Uplifting, motivational, and visionary.",
        "language": "Enthusiastic, with inspirational quotes, metaphors, and a focus on the future.",
        "example": "Imagine a world where every child, no matter where they are, has access to the best education possible. A world where AI bridges the gap between what is and what could be. We stand on the brink of that world today. Together, we can harness the power of AI to create an educational system that truly leaves no child behind."
    },
    {
        "name": "Emotive Style",
        "tone": "Passionate, expressive, and evocative.",
        "language": "Emotional, using strong adjectives and adverbs to convey deep feelings and create a powerful connection with the audience.",
        "example": "AI is more than just a tool—it's a beacon of hope for students who have been overlooked for far too long. Imagine the joy of a child who finally feels understood, who knows that their unique needs are being met by an AI that truly listens."
    },
    {
        "name": "Minimalist Style",
        "tone": "Concise, focused, and impactful.",
        "language": "Sparse, with short sentences and minimal use of adjectives or embellishments, focusing only on essential information.",
        "example": "AI is here. It’s changing education. Personalization, efficiency, accessibility—these are the benefits. Let’s make it happen."
    }
]


def generate_xml_for_style(style_index: int) -> str:
    try: 
        style = styles[style_index]
    except IndexError:
        return "Invalid style index."
    
    xml_string = f"<style>{style['name']}</style>\n"
    xml_string += f"<tone>{style['tone']}</tone>\n"
    xml_string += f"<language>{style['language']}</language>\n"
    xml_string += f"<example>{style['example']}</example>\n"
    return xml_string