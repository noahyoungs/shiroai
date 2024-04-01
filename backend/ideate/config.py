interface_fields = {
    "ideate": [{
        "key": "topic",
        "type": "string",
        "description": "A concise and descriptive title that captures the main theme of the presentation.",
        "examples": [
            "The Impact of Social Media on Mental Health",
            "The Future of Artificial Intelligence and Its Implications",
            "Climate Change: Causes, Effects, and Mitigation Strategies",
            ],
        "title": "Presentation Topic"
    },
    {
        "key": "audience",
        "type": "string",
        "description": "The intended audience for the presentation. This can include groups of people, organizations, communities, demographics, psychographics, behaivors, or geographic locations.",
        "examples": [
            "Mental health professionals, social media users, and concerned parents",
            "Tech enthusiasts, business leaders, and policymakers",
            "Environmentalists, students, and concerned citizens",
            ],
        "title": "Target Audience"
    },
    {
        "key": "goal",
        "type": "string",
        "description": "Represents the desired outcome or purpose that the presenter aims to achieve through their presentation. Can be informative persuasive, instructional, insperational, entertaining, or any combination of these.",
        "examples": [
            "To raise awareness about the potential negative effects of social media on mental health and discuss strategies for promoting healthy social media use",
            "To explore the current state and future potential of AI, and discuss its implications for society, the economy, and ethical considerations",
            "To educate the audience about the causes and effects of climate change, and discuss potential mitigation strategies and individual actions",
            ],
        "title": "Presentation Goal"
    }]
}

def get_interface_keys(interface):
    if interface in interface_fields:
        return [field["key"] for field in interface_fields[interface]]
    else:
        return []