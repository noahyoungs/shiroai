def get_messages(presentation_topic, audience, goal, subtopic_label, keywords, documents):
    return [
        {
            "role": """user""",
            "content": """Your task is to evaluate the relevance of a potential subtopic for inclusion in a presentation, based on the presentation's main topic, target audience, and goal.

Here are the key details about the presentation:
Main Topic: <presentation_topic>The 7 Natural Wonders of the World</presentation_topic>
Target Audience: <audience>Curious individuals eager to learn about iconic natural landmarks</audience>
Goal: <goal>To inspire curiosity and awe by showcasing the beauty and wonder of the 7 Natural Wonders of the World</goal>

And here are the details about the subtopic being considered:
<subtopic>
Subtopic Name: Paricutin Volcano in Mexico: Birth and Exploration
Keywords: paricutin, volcano, volcanos, michoacán, volcanic, parícutin, mexico, parangaricutiro, erupted, eruption
Excerpt(s): You can venture on a twelve-mile round-trip to the peak of the volcano, either by hiking or horseback. Hikers will walk through sandy banks and lava fields surrounding the volcano.  
You can explore Paricutin at any time of the year. It's located about a seven-hour drive from Mexico City. Combine a trip to the volcano with a visit to the capital city for a bit of nature and culture all in one. Accommodation near the volcano can be found in the city of Urapan.

The Paricutin Volcano.  
The Parícutin Volcano in Michoacán, Mexico, a cinder cone volcano, emerged in 1943 in a farmer's field, marking a remarkable event in geological history. This volcano, which is the youngest in the Northern Hemisphere, grew rapidly to a height of 424 meters (1,391 feet) over a period of nine years.

Another North American natural wonder, Paricutin is a volcano located in Michoacán, Mexico, 200 miles west of Mexico City.  
Though not the largest or most active volcano, Paricutin is special because it was the first volcano whose birth was witnessed and recorded by humankind. It also happens to be one of the world's youngest volcanos.  
In 1943, Paricutin emerged from a cornfield owned by local farmer Dionisio Pulido, growing to nearly 500 feet in just over a week.

One of the lesser-known natural wonders of the world, Paricutin is a cone-shaped volcano located in Michoacán, Mexico. Although you may never have heard of Paricutin before, it’s considered one of the 7 wonders of the natural world due to its youth. In fact, Paricutin first emerged in 1943, during a volcanic eruption. Surging out of a local cornfield, humanity witnessed the birth of the youngest volcano in the Northern Hemisphere.

In fact, Paricutin first emerged in 1943, during a volcanic eruption. Surging out of a local cornfield, humanity witnessed the birth of the youngest volcano in the Northern Hemisphere. Although the last eruption was in 1952, Paricutin continues to astound visitors with its perfectly symmetrical shape. Furthermore, if you travel to this part of Mexico you can enjoy hikes around the surrounding lava fields and even trek to the summit.
</subtopic>

Carefully analyze the subtopic keywords and excerpts in light of the presentation topic, audience
and goal. Consider the degree of overlap and alignment between them.

Write out your analysis in a <reasoning> section, explaining how relevant or irrelevant this
subtopic appears to be for this specific presentation and why. Cite specific connections and
evidence.

After your reasoning, provide a relevance score from 1-5 in a <score> section, where:
1 = Completely irrelevant
2 = Mostly irrelevant
3 = Somewhat relevant
4 = Quite relevant
5 = Extremely relevant

Remember, provide your <reasoning> first, then your numeric <score>.""",
        },
        {
            "role": """assistant""",
            "content": """<reasoning>
 This is highly relevant because the Paricutin Volcano one of the 7 wonders of the world.
 </reasoning>
 <score>
 5
 </score>""",
        },
        {
            "role": """user""",
            "content": """Your task is to evaluate the relevance of a potential subtopic for inclusion in a presentation, based on the presentation's main topic, target audience, and goal.

Here are the key details about the presentation:
Main Topic: <presentation_topic>The 7 Natural Wonders of the World</presentation_topic>
Target Audience: <audience>Curious individuals eager to learn about iconic natural landmarks</audience>
Goal: <goal>To inspire curiosity and awe by showcasing the beauty and wonder of the 7 Natural Wonders of the World</goal>

And here are the details about the subtopic being considered:
<subtopic>
Subtopic Name: Natural Wonders Organization and List.
Keywords: new7wonders, wonders, marvels, monuments, world, awe, nature, ancient, seven, mysteries
Excerpt(s): Travel Trends  
Post Tags  
Australia, Brazil, China, mexico, nepal, Norway, United States, Zambia  
Do you know what the 7 natural wonders of the world are? We all know about the 7 wonders of the world but nature has its own incredible selection of wonders! Dotted across the globe, these natural attractions are awe-inspiring displays of the power and beauty of nature. If you’re planning a trip, why not put one of these 7 natural wonders on your list of places to visit!  
Index  
Toggle

The oldest list of wonders of the world, the seven wonders of the ancient world includes a list of human-made marvels of their time.

Organisation protecting natural wonders  
**Seven Natural Wonders** is an organization that was created with the mission of protecting and promoting the natural wonders of the world. The project was launched in 2008 in response to the New 7 Wonders efforts to change the natural wonders of the world. This announcement was made following the campaign's efforts to establish a new list of modern man-made wonders.

The oldest list of wonders of the world, the seven wonders of the ancient world includes a list of human-made marvels of their time.

This announcement was made following the campaign's efforts to establish a new list of modern man-made wonders.  
Seven Natural Wonders was established to protect the original vision and declaration of the seven natural wonders of the world. Their list of the natural wonders includes:  
* Aurora Borealis (also known as the northern lights)
* Harbor of Rio de Janeiro
* Grand Canyon, USA
* Great Barrier Reef, Australia
* Mount Everest, Nepal
* Victoria Falls, Zambia and Zimbabwe
</subtopic>

Carefully analyze the subtopic keywords and excerpts in light of the presentation topic, audience
and goal. Consider the degree of overlap and alignment between them.

Write out your analysis in a <reasoning> section, explaining how relevant or irrelevant this
subtopic appears to be for this specific presentation and why. Cite specific connections and
evidence.

After your reasoning, provide a relevance score from 1-5 in a <score> section, where:
1 = Completely irrelevant
2 = Mostly irrelevant
3 = Somewhat relevant
4 = Quite relevant
5 = Extremely relevant

Remember, provide your <reasoning> first, then your numeric <score>.""",
        },
        {
            "role": """assistant""",
            "content": """<reasoning>This is quite relevant because The Natural Wonders organization is what created the list of Natural Wonders, and the List of Natural wonders is an fundamental topic for a presentation on the natural wonders of the world.</reasoning>
<score>4</score>""",
        },
        {
            "role": """user""",
            "content": """Your task is to evaluate the relevance of a potential subtopic for inclusion in a presentation, based on the presentation's main topic, target audience, and goal.

Here are the key details about the presentation:
Main Topic: <presentation_topic>The 7 Natural Wonders of the World</presentation_topic>
Target Audience: <audience>Curious individuals eager to learn about iconic natural landmarks</audience>
Goal: <goal>To inspire curiosity and awe by showcasing the beauty and wonder of the 7 Natural Wonders of the World</goal>

And here are the details about the subtopic being considered:
<subtopic>
Subtopic Name: Jeju Island's Natural Wonders and Unique Culture
Keywords: jeju, korea, island, koreans, korean, mermaids, sea, mainland, touristy, volcanic
Excerpt(s): Besides, there are so many things to do here, you'll need to come back multiple times to even make a dent in your to-see list: horseback riding, snorkeling, enjoying the beach and visiting green tea fields.  
Need more convincing? The following facts may just inspire you to book a ticket to incredible Jeju.

Jeju Island in South Korea.  
A volcanic island off the southern coast of South Korea, Jeju Island is the most beautiful natural wonder you might not have even heard of.  
The island is teeming with gorgeous natural features like cylindrical volcanic rocks, large lava tubes you can walk through, waterfalls that go into the sea, natural rock pools, volcanic craters and Hallasan, the tallest mountain in South Korea.

Jeju Island in South Korea.  
A UNESCO Biosphere Reserve, Hallasan is the mountain with the most species of plants on Earth. About 33 of these plants are endemic to it. This astonishing biodiversity is due to the volcanic nature of the mountain as well as its height, which rises 6,398 feet above sea level.  
As you go up the mountain, you'll see multiple ecosystems and numerous species of flora and fauna. Once at the summit, you'll be greeted by a large crater filled with a deep blue lake.

One of the most famous aspects of Jeju culture are the mermaids of Korea. These women divers fish completely by hand to maintain an important island tradition.  
However, the island's unique culture is, sadly, disappearing as it becomes more touristy and developed. Still, if you want a Korean experience that is very different from the homogenous mainland, you can still find it on Jeju.

Jeju Island waterfall.  
Because it is separated from the mainland, Jeju has its own distinct culture that is different from that of the mainland. This can be seen in the dialect, which even some South Koreans have a hard time understanding, as well as in the food, customs and architecture.  
One of the most famous aspects of Jeju culture are the mermaids of Korea. These women divers fish completely by hand to maintain an important island tradition.
</subtopic>

Carefully analyze the subtopic keywords and excerpts in light of the presentation topic, audience
and goal. Consider the degree of overlap and alignment between them.

Write out your analysis in a <reasoning> section, explaining how relevant or irrelevant this
subtopic appears to be for this specific presentation and why. Cite specific connections and
evidence.

After your reasoning, provide a relevance score from 1-5 in a <score> section, where:
1 = Completely irrelevant
2 = Mostly irrelevant
3 = Somewhat relevant
4 = Quite relevant
5 = Extremely relevant

Remember, provide your <reasoning> first, then your numeric <score>.""",
        },
        {
            "role": """assistant""",
            "content": """<reasoning>
 This is mostly irrelevant because Jeju island is not one of the 7 natural wonders of the world. It's only very slightly relevant because it's a natural landmark, but it's not one of the 7 wonders.
 </reasoning>
 <score>
 2
 </score>""",
        },
        {
            "role": """user""",
            "content": """Your task is to evaluate the relevance of a potential subtopic for inclusion in a presentation, based on the presentation's main topic, target audience, and goal.

Here are the key details about the presentation:
Main Topic: <presentation_topic>MongoDB vs DynamoDB: A Comparative Analysis</presentation_topic>
Target Audience: <audience>Software Developers and Technology Decision Makers</audience>
Goal: <goal>To inform and educate the audience about the differences and use cases of MongoDB and DynamoDB to help software developers and technology decision makers make informed decisions.</goal>

And here are the details about the subtopic being considered:
<subtopic>
Subtopic Name: DynamoDB Components and Queries (vs MongoDB)
Keywords: dynamodb, dynobase, mongodb, queries, cloud, query, sql, indexes, data, json
Excerpt(s): These are the core components of DynamoDB:

* DynamoDB Book
* DynamoDB Intro
* DynamoDB FAQ
* DynamoDB Tools
* DynamoDB GSI
* DynamoDB TTL
* DynamoDB PartiQL
* DynamoDB Indexes
* DynamoDB Triggers
* DynamoDB vs MongoDB
* DynamoDB Global Tables
* DynamoDB Best Practices  
Download  
/  
Changelog  
/  
Pricing  
/  
Member Portal  
/  
Privacy  
/  
EULA  
/  
Twitter  
© 2024 Dynobase

* Chat With Cloud
* DynamoDB CLI Queries
* DynamoDB Query Builder
* DynamoDB Boto3 Queries
* DynamoDB Golang Queries
* DynamoDB Code Examples
* DynamoDB Query Codegen
* DynamoDB Node.js Queries
* DynamoDB JSON Converter
* DynamoDB Local Admin GUI
* DynamoDB Pricing Calculator
* DynamoDB Single-Table Design

* DynamoDB Streams
* DynamoDB vs Aurora
* DynamoDB Key Types
* DynamoDB Data Types
* DynamoDB Local Setup
* DynamoDB Transactions
* DynamoDB Java Queries
* DynamoDB Data Modeling
* DynamoDB with AWS SAM
* DynamoDB Common Errors
* DynamoDB Capacity Modes
* DynamoDB Query Examples

* Use SQL with DynamoDB
* Import CSV To DynamoDB
* Import JSON To DynamoDB
* Export DynamoDB To JSON
* Export DynamoDB To S3
* Export DynamoDB To CSV
* DynamoDB Update Item
* DynamoDB Delete All Items
* DynamoDB Delete Item
* DynamoDB Create Table
* DynamoDB Delete Table
* DynamoDB Conditional Update
</subtopic>

Carefully analyze the subtopic keywords and excerpts in light of the presentation topic, audience
and goal. Consider the degree of overlap and alignment between them.

Write out your analysis in a <reasoning> section, explaining how relevant or irrelevant this
subtopic appears to be for this specific presentation and why. Cite specific connections and
evidence.

After your reasoning, provide a relevance score from 1-5 in a <score> section, where:
1 = Completely irrelevant
2 = Mostly irrelevant
3 = Somewhat relevant
4 = Quite relevant
5 = Extremely relevant

Remember, provide your <reasoning> first, then your numeric <score>.""",
        },
        {
            "role": """assistant""",
            "content": """<reasoning>
 This is completely irrelevant to the main topic of the presentation, which is about the differences between MongoDB and DynamoDB. All the excerpt are about different aspects of DynamoDB with no mention of MongoDB, and some of the comparisons are with other databases.
 </reasoning>
 <score>
 1
 </score>""",
        },
        {
            "role": """user""",
            "content": """Your task is to evaluate the relevance of a potential subtopic for inclusion in a presentation, based on the presentation's main topic, target audience, and goal.

Here are the key details about the presentation:
Main Topic: <presentation_topic>MongoDB vs DynamoDB: A Comparative Analysis</presentation_topic>
Target Audience: <audience>Software Developers and Technology Decision Makers</audience>
Goal: <goal>To inform and educate the audience about the differences and use cases of MongoDB and DynamoDB to help software developers and technology decision makers make informed decisions.</goal>

And here are the details about the subtopic being considered:
<subtopic>
Subtopic Name: Security and Access Control in MongoDB and DynamoDB
Keywords: dynamodb, dynamo, mongodb, authentication, cloud, authorization, api, encryption, access, aws
Excerpt(s): Access control for DynamoDB is managed using AWS Identity and Access Management (IAM).  
MongoDB Atlas provides encryption at rest on all cloud platforms using their transparent disk encryption. Similar to DynamoDB, customers can provide their own keys and utilize the key management system available on their chosen cloud provider. MongoDB Atlas also provides role-based access rules to control access to the data.

DynamoDB provides out of the box security; the security model is based on Identity and Access Management (IAM), enabling one to manage access to AWS services and resources securely. One can create and manage AWS users and groups and use permissions to allow and deny their access to AWS resources. IAM has been battle-tested and found to be intuitive and cooperative with limited configuration.

IAM has been battle-tested and found to be intuitive and cooperative with limited configuration. It is not possible to access DynamoDB from the open internet as it is not directly addressed, requests route through an API gateway, and AWS manages authorization from here. MongoDB is secure, but the default configuration is not. Because it does not provide out of the box security, it can be particularly vulnerable to breaches.

When it comes to security, DynamoDB offers much better features out-of-the-box. Being a part of AWS, the AWS Identity and Access Management (IAM) permission model applies to it, as it does with AWS services like EC2, RDS, and others.  
In addition, DynamoDB is not accessible directly from the internet, which adds another layer of security on top of its particular configuration.  
MongoDB also offers good security features, but not through its default settings.

DynamoDB comes with baked-in security best practices as their service is managed by AWS. The authentication and authorization model is based on AWS Identity and Access Management (IAM) which offers users fine-grained control over users, roles, and policies that are used to interact with DynamoDB.  
Besides, DynamoDB is not directly connected to the wider internet since requests are routed through an API gateway where the authorization is managed by AWS.
</subtopic>

Carefully analyze the subtopic keywords and excerpts in light of the presentation topic, audience
and goal. Consider the degree of overlap and alignment between them.

Write out your analysis in a <reasoning> section, explaining how relevant or irrelevant this
subtopic appears to be for this specific presentation and why. Cite specific connections and
evidence.

After your reasoning, provide a relevance score from 1-5 in a <score> section, where:
1 = Completely irrelevant
2 = Mostly irrelevant
3 = Somewhat relevant
4 = Quite relevant
5 = Extremely relevant

Remember, provide your <reasoning> first, then your numeric <score>.""",
        },
        {
            "role": """assistant""",
            "content": """<reasoning>
 This is quite relevant to our topic because security is a key concern for software developers and technology decision makers, and the excerpts make a good comparison on security features between MongoDB and DynamoDB.
 </reasoning>
 <score>
 4
 </score>""",
        },
        {
            "role": """user""",
            "content": f"""Your task is to evaluate the relevance of a potential subtopic for inclusion in a presentation, based on the presentation"s main topic, target audience, and goal.\n\nHere are the key details about the presentation:\nMain Topic: <presentation_topic>{presentation_topic}</presentation_topic>\nTarget Audience: <audience>{audience}</audience>\nGoal: <goal>{goal}</goal>\n\nAnd here are the details about the subtopic being considered:\n<subtopic>\nSubtopic Name: {subtopic_label}\nKeywords: {keywords}\nExcerpt(s): {documents}\n</subtopic>\n\nCarefully analyze the subtopic keywords and excerpts in light of the presentation topic, audience\nand goal. Consider the degree of overlap and alignment between them.\n\nWrite out your analysis in a <reasoning> section, explaining how relevant or irrelevant this\nsubtopic appears to be for this specific presentation and why. Cite specific connections and\nevidence.\n\nAfter your reasoning, provide a relevance score from 1-5 in a <score> section, where:\n1 = Completely irrelevant\n2 = Mostly irrelevant\n3 = Somewhat relevant\n4 = Quite relevant\n5 = Extremely relevant\n\nRemember, provide your <reasoning> first, then your numeric <score>.""",
        },
    ]
