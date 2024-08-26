interface Style {
    name: string;
    tone?: string;
    language?: string;
    example?: string;
    content?: string; // Added content parameter
    icon: string;
    key: string;
    description?: string;
}

export const styles: Style[] = [
    {
        name: "Default",
        tone: "Balanced, clear, and straightforward.",
        example: "Introduce AI in education. Highlight key benefits: personalization, efficiency. Conclude with future trends.",
        content: "Provides essential notes with clear instructions and main points for each slide, without embellishments.",
        icon: "tabler:clear-formatting",
        key: "0",
    },
    {
        name: "Detailed Guide",
        tone: "Instructive, thorough, and supportive.",
        example: "Start by greeting the audience with a warm smile. Introduce the topic with enthusiasm: 'Today, we’re exploring the transformative impact of AI on education.' Pause for a moment after mentioning the key point. Use a hand gesture to emphasize 'transformative impact.' Move on to the next slide when you notice nods of understanding.",
        content: "Provides step-by-step instructions, cues for gestures, and detailed explanations for each slide.",
        icon: "tabler:vocabulary",
        key: "1",
    },
    {
        name: "Bullet Point",
        tone: "Concise, focused, and to the point.",
        example: "- AI in education: key benefits.\n- Personalization.\n- Efficiency.\n- Future trends.\n- Next slide: Challenges of AI.",
        content: "Contains key points or prompts that guide the speaker’s flow without detailed explanations.",
        icon: "tabler:list",
        key: "2",
    },
    {
        name: "Reminder",
        tone: "Subtle, simple, and supportive.",
        example: "Remember to maintain eye contact with the audience. Slow down when explaining the next point. Transition smoothly to the next slide.",
        content: "Includes brief reminders of important elements like pace, eye contact, and transitions.",
        icon: "tabler:list-check",
        key: "3",
    },
    {
        name: "Conversational",
        tone: "Relaxed, informal, and engaging.",
        example: "So, here’s the deal—AI is changing everything in education, right? Let’s talk about how. Feel free to ask the audience: 'Have any of you seen AI in action in your own classrooms?' Encourage a quick show of hands.",
        content: "Mimics a natural conversation, with prompts for casual language and interaction with the audience.",
        icon: "tabler:message-chatbot",
        key: "4",
    },
    {
        name: "Prompt",
        tone: "Interactive, questioning, and engaging.",
        example: "Ask the audience: 'What do you think are the biggest challenges of using AI in education?' Wait for responses before moving on. Prompt discussion based on their answers.",
        content: "Encourages interaction with the audience through questions and prompts.",
        icon: "tabler:message-question",
        key: "5",
    },
    {
        name: "Motivational",
        tone: "Uplifting, positive, and energetic.",
        example: "Encourage the audience: 'Imagine a world where every student has access to personalized learning. That’s the power of AI!' Use an enthusiastic tone to inspire.",
        content: "Focuses on inspirational messages and motivating the audience throughout the presentation.",
        icon: "tabler:heart-up",
        key: "6",
    },
    {
        name: "Minimalist",
        tone: "Brief, focused, and essential.",
        example: "AI in Education.\n- Personalization.\n- Efficiency.\n- Challenges.\n- Future.",
        content: "Provides only the most crucial notes, minimizing words to keep the speaker on track.",
        icon: "tabler:text-color",
        key: "7",
    },
    {
        name: "Custom Style",
        description: "Define your own style, tailored to your needs.",
        content: "Allows the user to create a personalized style based on their preferences and presentation requirements.",
        icon: "tabler:edit",
        key: "-1",
    }
];
