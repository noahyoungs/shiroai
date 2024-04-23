def get_messages(topic, text):
    return [
        {
            "role": """user""",
            "content": """Your task is to rate a piece of text that has been extracted from a website for its potential value as a source in putting together a presentation about All the services provided by AWS.

First, here is the extracted text to analyze:

<extracted_text>
AWS

Managed NoSQL database
View product

Your AI-powered productivity tool for the IDE and command line
View product
Networking & Content Delivery

Virtual servers in the cloud
View product
Storage

Global content delivery network
View product
Developer Tools

Launch and manage virtual private servers
View product
Database
</extracted_text>

Consider the following criteria when evaluating the text:

1. Informative content: The text should contain objective, informative content that can be used in a presentation, such as explanations, comparisons, definitions, statistics, facts, or insights. The information should provide valuable context and background on the topic.

2. Clarity and organization: The text should be well-structured and clearly convey its main points. While complete paragraphs are ideal, bullet points or other concise formats are acceptable as long as the text maintains its semantic meaning and informative value.

3. Absence of non-informative content: The text should not contain bibliographies, reference lists, copyright notices, or other credits that do not contribute to the main content. It should also not include meaningless text fragments or text that appears to be a link without providing useful information.

4. Non-promotional content: The text should not be an advertisement for products or services, whether paid or free.

5. Objectivity: The text should maintain an objective tone and avoid overly detailed anecdotal content or subjective and emotional language.

First, write out your analysis and reasoning on the above criteria inside <reasoning></reasoning> tags.


After your reasoning, provide a value score from 1-5 in a <score></score> section, where:

1 = Completely useless
2 = Mostly useless
3 = Somewhat useful
4 = Quite useful
5 = Extremely useful

Please focus on critically evaluating the merits of the content as a source, not the content's relevance to the presentation topic. Highlight both the strengths and shortcomings of the text in your reasoning. Remember, provide your <reasoning></reasoning> first, then your numeric <score></score>.""",
        },
        {
            "role": """assistant""",
            "content": """<reasoning> The text provides only a high-level, promotional list of AWS product names without any meaningful explanations, comparisons, or other informative details that would be useful for a presentation on the full range of AWS services. The content lacks substance, depth, and objectivity, and would not contribute valuable information to the presentation. </reasoning>

<score>1</score>""",
        },
        {
            "role": """user""",
            "content": """Your task is to rate a piece of text that has been extracted from a website for its potential value as a source in putting together a presentation about All the services offered by AWS.

First, here is the extracted text to analyze:

<extracted_text>
View All Financial Services Customer Stories __

Customer Name
Customer Name
No products found for this category.
View All Government Stories __
Customer Name
Customer Name
No products found for this category.
View All Healthcare & Life Sciences Customer Stories __
Customer Name
Customer Name
No products found for this category.
View All Manufacturing Customer Stories __
Customer Name
Customer Name
No products found for this category.


Customer Name
Customer Name
No products found for this category.
View All Manufacturing Customer Stories __
Customer Name
Customer Name
No products found for this category.
View All Media & Entertainment Customer Stories __
Customer Name
Customer Name
No products found for this category.
View All Retail & Consumer Goods Customer Stories __
Customer Name
Customer Name
No products found for this category.


View All Aerospace & Satellite Customer Stories __

Customer Name
Customer Name
No products found for this category.
View All Agriculture Customer Stories __
Customer Name
Customer Name
No products found for this category.
View All Automotive Customer Stories __
Customer Name
Customer Name
No products found for this category.
View All Education Customer Stories __
Customer Name
Customer Name
No products found for this category.


Customer Name
Customer Name
No products found for this category.
View All Education Customer Stories __
Customer Name
Customer Name
No products found for this category.
View All Energy Customer Stories __
Customer Name
Customer Name
No products found for this category.
View All Financial Services Customer Stories __
Customer Name
Customer Name
No products found for this category.
View All Government Stories __
Customer Name
Customer Name


Customer Name
Customer Name
No products found for this category.
View All Customer Stories __
Customer Name
Customer Name
No products found for this category.
View All Advertising & Marketing Customer Stories __
Customer Name
Customer Name
No products found for this category.
View All Aerospace & Satellite Customer Stories __
Customer Name
Customer Name
No products found for this category.
View All Agriculture Customer Stories __
Customer Name
</extracted_text>

Consider the following criteria when evaluating the text:

1. Informative content: The text should contain objective, informative content that can be used in a presentation, such as explanations, comparisons, definitions, statistics, facts, or insights. The information should provide valuable context and background on the topic.

2. Clarity and organization: The text should be well-structured and clearly convey its main points. While complete paragraphs are ideal, bullet points or other concise formats are acceptable as long as the text maintains its semantic meaning and informative value.

3. Absence of non-informative content: The text should not contain bibliographies, reference lists, copyright notices, or other credits that do not contribute to the main content. It should also not include meaningless text fragments or text that appears to be a link without providing useful information.

4. Non-promotional content: The text should not be an advertisement for products or services, whether paid or free.

5. Objectivity: The text should maintain an objective tone and avoid overly detailed anecdotal content or subjective and emotional language.

First, write out your analysis and reasoning on the above criteria inside <reasoning></reasoning> tags.


After your reasoning, provide a value score from 1-5 in a <score></score> section, where:

1 = Completely useless
2 = Mostly useless
3 = Somewhat useful
4 = Quite useful
5 = Extremely useful

Please focus on critically evaluating the merits of the content as a source, not the content's relevance to the presentation topic. Highlight both the strengths and shortcomings of the text in your reasoning. Remember, provide your <reasoning></reasoning> first, then your numeric <score></score>.""",
        },
        {
            "role": """assistant""",
            "content": """<reasoning>
The text appears to be a list of links or headings related to customer stories across various industries like financial services, government, healthcare, manufacturing, media, retail, aerospace, agriculture, automotive, and education. However, the text contains no actual informative content about AWS services. It simply lists "Customer Name" repeatedly under each industry heading and states "No products found for this category."

The text lacks any explanations, descriptions, facts, statistics, or insights about AWS's service offerings. It is not well-structured to convey any clear points, as it just repeats the same non-informative "Customer Name" and "No products found" lines.

While the text does not contain bibliographies, references or promotional content, it also provides no meaningful information whatsoever about AWS services that could be used in a presentation. The text appears to be broken links or placeholders, completely devoid of useful content on the topic.
</reasoning>

<score>1</score>""",
        },
        {
            "role": """user""",
            "content": """Your task is to rate a piece of text that has been extracted from a website for its potential value as a source in putting together a presentation about All the services offered by AWS.

First, here is the extracted text to analyze:

<extracted_text>
Beginners who want to learn AWS can start with the basics first. Once you have mastered AWS basics you can move on to the advanced topics.
This free AWS training consists of 11 hours of video content that will help you understand AWS thoroughly.
It is recommended that you always start with AWS basics first. For a better understanding, watch the learning videos in sequence without skipping any.

As the world increasingly turns to cloud-based services, it's no surprise that Amazon Web Services (AWS) is becoming one of the most in-demand technology platforms. With so much demand, you must have a strong understanding of AWS if you're hoping to land a job with AWS in the future. In this article, we've compiled a list of the top 90+ questions and answers for your AWS interview preparation.
Lesson 14: Amazon Interview Questions and Answers That You Should Know

Share your certificate with prospective employers and your professional network on LinkedIn.
Expected growth rate for public cloud spending globally
Annual median salary of an AWS solutions architect
There are no prerequisites to learn AWS basics. This free AWS course has been designed to cater to the understanding level of beginners.
Beginners who want to learn AWS can start with the basics first. Once you have mastered AWS basics you can move on to the advanced topics.

It is recommended that you always start with AWS basics first. For a better understanding, watch the learning videos in sequence without skipping any.
The videos that you find in this AWS Basics course are created by mentors who are industry leaders with vast experience in the field. They are aware of the needs of different learners and have designed the course to be easy to learn.
The AWS basics covered in this free course include:

As soon as the certificate is unlocked, you will receive a mail with a link to your SkillUp learning dashboard on your registered mail address. Click the link to view and download your certificate. You can even add the certificate to your resume and share it on social media platforms.
After completing this free AWS basics course, you can opt for the AWS Cloud Architect Master's Program or Post Graduate Program in Cloud Computing provided by Simplilearn.
</extracted_text>

Consider the following criteria when evaluating the text:

1. Informative content: The text should contain objective, informative content that can be used in a presentation, such as explanations, comparisons, definitions, statistics, facts, or insights. The information should provide valuable context and background on the topic.

2. Clarity and organization: The text should be well-structured and clearly convey its main points. While complete paragraphs are ideal, bullet points or other concise formats are acceptable as long as the text maintains its semantic meaning and informative value.

3. Absence of non-informative content: The text should not contain bibliographies, reference lists, copyright notices, or other credits that do not contribute to the main content. It should also not include meaningless text fragments or text that appears to be a link without providing useful information.

4. Non-promotional content: The text should not be an advertisement for products or services, whether paid or free.

5. Objectivity: The text should maintain an objective tone and avoid overly detailed anecdotal content or subjective and emotional language.

First, write out your analysis and reasoning on the above criteria inside <reasoning></reasoning> tags.


After your reasoning, provide a value score from 1-5 in a <score></score> section, where:

1 = Completely useless
2 = Mostly useless
3 = Somewhat useful
4 = Quite useful
5 = Extremely useful

Please focus on critically evaluating the merits of the content as a source, not the content's relevance to the presentation topic. Highlight both the strengths and shortcomings of the text in your reasoning. Remember, provide your <reasoning></reasoning> first, then your numeric <score></score>.""",
        },
        {
            "role": """assistant""",
            "content": """<reasoning>
The text provides some useful background information on learning AWS, such as mentioning that there is demand for AWS skills and that beginners should start by learning the basics first before moving to advanced topics. It also lists some of the basics that are covered in the free AWS course it describes, like EC2, S3, and IAM.

However, the text is mostly focused on promoting a specific free AWS training course rather than giving an objective overview of all the services AWS offers. Many parts read like an advertisement, touting the benefits of the course and encouraging people to sign up. It does not go into detail explaining the various AWS services and seems more geared toward beginners than providing a comprehensive look at the AWS platform.

While there are a few potentially useful tidbits, overall the promotional and beginner-focused nature of the content limits its usefulness as a source for thoroughly covering all the services available on AWS in a presentation. To properly cover that topic, sources that methodically explain each of the major service categories and specific services would likely be more valuable.
</reasoning>

<score>2</score>""",
        },
        {
            "role": """user""",
            "content": """Your task is to rate a piece of text that has been extracted from a website for its potential value as a source in putting together a presentation about A comparison of Caged, Cage-Free, Free-Range, and Pasture-Raised Eggs.

First, here is the extracted text to analyze:

<extracted_text>
Eggs

Organic Consumers Association. “Regenerative Farming Starts Here-with Chickens.” Organic Consumers Association , 28 Feb. 2018, https://www.organicconsumers.org/blog/regenerative-farming-starts-here-chickens.
Karsten, H.D., et al. “Vitamins A, E and Fatty Acid Composition of the Eggs of Caged Hens and Pastured Hens.” Renewable Agriculture and Food Systems , vol. 25, no. 1, 12 Jan. 2010, pp. 45–54., https://doi.org/10.1017/s1742170509990214.
Koefoed, Alexis.

Goetz, Gretchen. “Who Inspects What? A Food Safety Scramble.” Food Safety News , Marler Clark, 16 Dec. 2010, https://www.foodsafetynews.com/2010/12/who-inspects-what-a-food-safety-scramble/.
Ibid.
“Salmonella .” Centers for Disease Control and Prevention , Centers for Disease Control and Prevention, 20 Oct. 2022, https://www.cdc.gov/salmonella/index.html.
Center for Food Safety and Applied Nutrition. “What You Need to Know about Egg Safety.” _U.S.

O’Keefe, Terrence. “Top U.S. Egg Producer Rankings for 2018: Cage-Free Surplus.” Egg Industry , Feb. 2018, https://www.eggindustry-digital.com/eggindustry/201802/MobilePagedReplica.action?pm=2&folio=Cover#pg1.
Fassler, Joe. “What Are ‘Pasture-Raised Eggs,” Really?” The Counter , 18 May 2016, https://thecounter.org/pasture-raised-eggs-part-one/.
Sherwin, C.M., et al. “Comparison of the Welfare of Layer Hens in 4 Housing Systems in the UK.” British Poultry Science , vol. 51, no.

Karsten, H.D., et al. “Vitamins A, E and Fatty Acid Composition of the Eggs of Caged Hens and Pastured Hens.” Renewable Agriculture and Food Systems , vol. 25, no. 1, 12 Jan. 2010, pp. 45–54., https://doi.org/10.1017/s1742170509990214.
Dekker, S.E.M., et al. “Emissions of Ammonia, Nitrous Oxide, and Methane from Aviaries with Organic Laying Hen Husbandry.” Biosystems Engineering , vol. 110, no. 2, Oct. 2011, pp. 123–133., https://doi.org/10.1016/j.biosystemseng.2011.07.006.

2022, https://www.cdc.gov/salmonella/index.html. 38. Center for Food Safety and Applied Nutrition. “What You Need to Know about Egg Safety.” U.S. Food and Drug Administration , U.S. Food and Drug Administration, 10 May 2022, https://www.fda.gov/food/buy-store-serve-safe-food/what-you-need-know-about-egg-safety. 39. Smithers, Rebecca. “Egg Safety – We’ve Cracked It, Food Watchdog Tells Britons.” The Guardian , Guardian News and Media, 10 Oct.
</extracted_text>

Consider the following criteria when evaluating the text:

1. Informative content: The text should contain objective, informative content that can be used in a presentation, such as explanations, comparisons, definitions, statistics, facts, or insights. The information should provide valuable context and background on the topic.

2. Clarity and organization: The text should be well-structured and clearly convey its main points. While complete paragraphs are ideal, bullet points or other concise formats are acceptable as long as the text maintains its semantic meaning and informative value.

3. Absence of non-informative content: The text should not contain bibliographies, reference lists, copyright notices, or other credits that do not contribute to the main content. It should also not include meaningless text fragments or text that appears to be a link without providing useful information.

4. Non-promotional content: The text should not be an advertisement for products or services, whether paid or free.

5. Objectivity: The text should maintain an objective tone and avoid overly detailed anecdotal content or subjective and emotional language.

First, write out your analysis and reasoning on the above criteria inside <reasoning></reasoning> tags.


After your reasoning, provide a value score from 1-5 in a <score></score> section, where:

1 = Completely useless
2 = Mostly useless
3 = Somewhat useful
4 = Quite useful
5 = Extremely useful

Please focus on critically evaluating the merits of the content as a source, not the content's relevance to the presentation topic. Highlight both the strengths and shortcomings of the text in your reasoning. Remember, provide your <reasoning></reasoning> first, then your numeric <score></score>.""",
        },
        {
            "role": """assistant""",
            "content": """<reasoning>
The text contains some potentially useful information for the presentation topic, such as mentioning vitamins A and E and fatty acid composition differences between caged and pastured eggs, as well as emissions data for organic aviaries. This provides some relevant factual comparisons.

However, the text is very disorganized and fragmented, reading more like a jumbled list of references than coherent informative content. It lacks clear structure, explanations, definitions, and context needed to be valuable for a presentation. Many of the lines appear to just be names of authors or partial references rather than actual informative statements.

There are also many irrelevant elements like links and repetitive citations of government agencies that do not contribute meaningful content on the topic of comparing egg production methods. More detailed, objective explanations of the differences between the egg types and their implications would be needed to make this a strong source for the presentation.
</reasoning>

<score>2</score>""",
        },
        {
            "role": """user""",
            "content": """Your task is to rate a piece of text that has been extracted from a website for its potential value as a source in putting together a presentation about The Coton de Tulear Dog Breed.

First, here is the extracted text to analyze:

<extracted_text>
Coton
It really works!" Photo courtesy of Cotons of Adam's Eden
Ami, a female Coton de Tulear puppy
"Ziggy, our male Coton de Tulear at 8 years old. Our family's sweetheart. We adore him!"

We call her "Captain Reno"" Photo courtesy of Cotons of Adam's Eden
"Reno is one of three Cotons that we own and is definitely the "Queen" of the dogs. She is a very kind leader but if one of the others gets out of line she lets them know. When her puppies are young she guards them well, allowing the others only a little sniff or two but she NEVER gets upset when one of her human family members or their friends pets and snuggles them.

"Another favorite pastime for Reno is riding on the lawnmower with my husband. She somehow knows when it's time to cut the grass and waits for him to start the mower. She eagerly jumps on and will ride with him the entire two hours it takes to cut our lawn. We call her "Captain Reno"" Photo courtesy of Cotons of Adam's Eden
"Reno is one of three Cotons that we own and is definitely the "Queen" of the dogs.

    NKC = National Kennel Club
    Photo courtesy of Chesterfield Coton de Tulear
    "This is our dog, Reno. She is a three-year-old Coton de Tulear and the joy of our home. Reno is the reason we decided to breed the Coton. Her friendly, calm and smart demeanor is unlike any dog we have ever owned. She is truly a big dog in a little dog body.
    "Reno is content to lie on our lap or at our feet but the minute we mention the word "outside" she is eager to play. Reno LOVES to play Frisbee.

She is truly a big dog in a little dog body.
"Reno is content to lie on our lap or at our feet but the minute we mention the word "outside" she is eager to play. Reno LOVES to play Frisbee. So much so that we have to spell the word F-R-I-S-B-E-E or she will run in circles and dance on two feet until we get our jackets and shoes on to go and throw it for her.
"Another favorite pastime for Reno is riding on the lawnmower with my husband.
</extracted_text>

Consider the following criteria when evaluating the text:

1. Informative content: The text should contain objective, informative content that can be used in a presentation, such as explanations, comparisons, definitions, statistics, facts, or insights. The information should provide valuable context and background on the topic.

2. Clarity and organization: The text should be well-structured and clearly convey its main points. While complete paragraphs are ideal, bullet points or other concise formats are acceptable as long as the text maintains its semantic meaning and informative value.

3. Absence of non-informative content: The text should not contain bibliographies, reference lists, copyright notices, or other credits that do not contribute to the main content. It should also not include meaningless text fragments or text that appears to be a link without providing useful information.

4. Non-promotional content: The text should not be an advertisement for products or services, whether paid or free.

5. Objectivity: The text should maintain an objective tone and avoid overly detailed anecdotal content or subjective and emotional language.

First, write out your analysis and reasoning on the above criteria inside <reasoning></reasoning> tags.


After your reasoning, provide a value score from 1-5 in a <score></score> section, where:

1 = Completely useless
2 = Mostly useless
3 = Somewhat useful
4 = Quite useful
5 = Extremely useful

Please focus on critically evaluating the merits of the content as a source, not the content's relevance to the presentation topic. Highlight both the strengths and shortcomings of the text in your reasoning. Remember, provide your <reasoning></reasoning> first, then your numeric <score></score>.""",
        },
        {
            "role": """assistant""",
            "content": """<reasoning>
The text provides some useful information about the Coton de Tulear breed, such as describing their friendly, calm, and smart demeanor. It also gives a couple specific examples of the breed's behavior and personality through anecdotes about a particular Coton named Reno.

However, the text is mostly just a collection of quotes describing one family's experiences with their pet Coton de Tulear dogs. While this provides a bit of color and real-world examples, it lacks the kind of objective, factual information that would be most valuable in an informative presentation, such as details on the breed's history, physical characteristics, care requirements, health issues, etc. The text reads more like personal testimonials rather than authoritative information from experts on the breed.

Additionally, the text is somewhat disorganized and jumps around between different topics and anecdotes without a clear structure. Some parts seem to repeat or contradict each other as well. It would require quite a bit of editing and restructuring to extract the useful bits into a well-organized segment for a presentation.

So in summary, while the text provides a few nuggets of useful information and examples, it is not an ideal source overall given its lack of comprehensive, objective facts about the breed and its somewhat unstructured and anecdotal nature. It would be better to seek out sources that are more informative, well-organized and less centered around individuals' subjective experiences.
</reasoning>

<score>2</score>""",
        },
        {
            "role": """user""",
            "content": """Your task is to rate a piece of text that has been extracted from a website for its potential value as a source in putting together a presentation about Understanding Microplastics Exposure Metrics, Safe Levels, and Common Sources.

First, here is the extracted text to analyze:

<extracted_text>
Chemosphere (2018) 205:80–7. 10.1016/j.chemosphere.2018.04.076 [PubMed] [CrossRef] [Google Scholar] [Ref list]
86. Naji A, Nuri M, Vethaak AD. Microplastics Contamination in Molluscs From the Northern Part of the Persian Gulf. Environ Pollut (2018) 235:113–20. 10.1016/j.envpol.2017.12.046 [PubMed] [CrossRef] [Google Scholar] [Ref list]
87. Li Q, Sun C, Wang Y, Cai H, Li L, Li J, et al.. Fusion of Microplastics Into the Mussel Byssus. Environ Pollut (2019) 252:420–6.

Sci Rep (2017) 7(1):1–10. 10.1038/srep46687 [PMC free article] [PubMed] [CrossRef] [Google Scholar] [Ref list]
182. Lu L, Wan Z, Luo T, Fu Z, Jin Y. Polystyrene Microplastics Induce Gut Microbiota Dysbiosis and Hepatic Lipid Metabolism Disorder in Mice. Sci Total Environ (2018) 631:449–58. 10.1016/j.scitotenv.2018.03.051 [PubMed] [CrossRef] [Google Scholar] [Ref list]
183. Deng Y, Zhang Y, Qiao R, Bonilla MM, Yang X, Ren H, et al..

[PubMed] [Google Scholar] [Ref list]
116. Gasperi J, Wright SL, Dris R, Collard F, Mandin C, Guerrouache M, et al.. Microplastics in Air: Are We Breathing It in? Curr Opin J Environ Sci Health (2018) 1:1–5. 10.1016/j.coesh.2017.10.002 [CrossRef] [Google Scholar] [Ref list]
117. Vethaak AD, Leslie HA. Plastic Debris Is a Human Health Issue. Environ Sci Technol (2016) 50(13):6825–6. 10.1021/acs.est.6b02569 [PubMed] [CrossRef] [Google Scholar] [Ref list]
118.

Environ Pollut (2019) 244:153–64. 10.1016/j.envpol.2018.10.039 [PubMed] [CrossRef] [Google Scholar] [Ref list]
17. Karbalaei S, Hanachi P, Walker TR, Cole M. Occurrence, Sources, Human Health Impacts and Mitigation of Microplastic Pollution. Environ Sci Pollut Res (2018) 25(36):36046–63. 10.1007/s11356-018-3508-7 [PubMed] [CrossRef] [Google Scholar] [Ref list]
18. Andrady AL. Microplastics in the Marine Environment. Mari Pollut Bull (2011) 62(8):1596–605.

10.1007/s11356-018-3508-7 [PubMed] [CrossRef] [Google Scholar] [Ref list]
18. Andrady AL. Microplastics in the Marine Environment. Mari Pollut Bull (2011) 62(8):1596–605. 10.1016/j.marpolbul.2011.05.030 [PubMed] [CrossRef] [Google Scholar] [Ref list]
21. Rillig MC. Microplastic in Terrestrial Ecosystems and the Soil? Environ Sci Technol (2012) 46(12):6453–4. 10.1021/es302011r [PubMed] [CrossRef] [Google Scholar] [Ref list]
22.
</extracted_text>

Consider the following criteria when evaluating the text:

1. Informative content: The text should contain objective, informative content that can be used in a presentation, such as explanations, comparisons, definitions, statistics, facts, or insights. The information should provide valuable context and background on the topic.

2. Clarity and organization: The text should be well-structured and clearly convey its main points. While complete paragraphs are ideal, bullet points or other concise formats are acceptable as long as the text maintains its semantic meaning and informative value.

3. Absence of non-informative content: The text should not contain bibliographies, reference lists, copyright notices, or other credits that do not contribute to the main content. It should also not include meaningless text fragments or text that appears to be a link without providing useful information.

4. Non-promotional content: The text should not be an advertisement for products or services, whether paid or free.

5. Objectivity: The text should maintain an objective tone and avoid overly detailed anecdotal content or subjective and emotional language.

First, write out your analysis and reasoning on the above criteria inside <reasoning></reasoning> tags.


After your reasoning, provide a value score from 1-5 in a <score></score> section, where:

1 = Completely useless
2 = Mostly useless
3 = Somewhat useful
4 = Quite useful
5 = Extremely useful

Please focus on critically evaluating the merits of the content as a source, not the content's relevance to the presentation topic. Highlight both the strengths and shortcomings of the text in your reasoning. Remember, provide your <reasoning></reasoning> first, then your numeric <score></score>.""",
        },
        {
            "role": """assistant""",
            "content": """<reasoning>
The text appears to be a fragmented list of references from scientific papers, with only partial information provided for each one. While the references seem to be on the general topic of microplastics and their impacts, there is no coherent informative content, explanations, facts, or insights that could be used in a presentation. The text is very disorganized, lacks any clear structure or main points, and consists almost entirely of non-informative reference information like journal names, publication years, DOI numbers, and links like "[PubMed]" and "[Google Scholar]". There are no complete sentences or paragraphs.

The references hint that the full text of the cited papers may contain useful information on topics like microplastics contamination in mollusks, polystyrene microplastics causing gut issues in mice, microplastics in the air and human health, and microplastics in marine and terrestrial environments. However, none of that informative content is included here. The text is an example of exactly what should be excluded according to the criteria - it is essentially a meaningless list of references and links without the actual informative content from the papers. It cannot be used as a source in its current form and would require accessing and extracting the relevant content from each of the cited papers individually.
</reasoning>

<score>1</score>""",
        },
        {
            "role": """user""",
            "content": """Your task is to rate a piece of text that has been extracted from a website for its potential value as a source in putting together a presentation about Understanding Microplastics Exposure Metrics, Safe Levels, and Common Sources.

First, here is the extracted text to analyze:

<extracted_text>
Mirjana Andjelkovic
3. Center of Excellence for Molecular Food Sciences & Department of Biochemistry, University of Belgrade-Faculty of Chemistry, Studentski trg 12–16, Belgrade, 11000, Serbia
Tanja Cirkovic-Velickovic
4. Department of Food Technology, Food Safety and Health, Faculty of Bioscience Engineering, Ghent University, Coupure links 653, B-9000, Ghent, Belgium
Andreja Rajkovic
Authors

    Bozidar Udovicki
    View author publications

This article was submitted to Obesity, a section of the journal Frontiers in Endocrinology
Received 2021 Jun 14; Accepted 2021 Jul 26.
Copyright © 2021 Kannan and Vimalkumar
This is an open-access article distributed under the terms of the Creative Commons Attribution License (CC BY).

Received 2021 Jun 14; Accepted 2021 Jul 26.
Copyright © 2021 Kannan and Vimalkumar
This is an open-access article distributed under the terms of the Creative Commons Attribution License (CC BY). The use, distribution or reproduction in other forums is permitted, provided the original author(s) and the copyright owner(s) are credited and that the original publication in this journal is cited, in accordance with accepted academic practice.

Edited by: Malarvannan Govindan, University of Antwerp, Belgium
Reviewed by: Thomas McGrath, University of Antwerp, Belgium; Thava Palanisami, The University of Newcastle, Australia; K. Ramu, National Centre for Coastal Research, India
*Correspondence: Kurunthachalam Kannan, gro.enognaluyn@nannak.malahcahtnuruK
This article was submitted to Obesity, a section of the journal Frontiers in Endocrinology
Received 2021 Jun 14; Accepted 2021 Jul 26.
Copyright © 2021 Kannan and Vimalkumar

The images or other third party material in this article are included in the article's Creative Commons licence, unless indicated otherwise in a credit line to the material. If material is not included in the article's Creative Commons licence and your intended use is not permitted by statutory regulation or exceeds the permitted use, you will need to obtain permission directly from the copyright holder. To view a copy of this licence, visit http://creativecommons.org/licenses/by/4.0/.
</extracted_text>

Consider the following criteria when evaluating the text:

1. Informative content: The text should contain objective, informative content that can be used in a presentation, such as explanations, comparisons, definitions, statistics, facts, or insights. The information should provide valuable context and background on the topic.

2. Clarity and organization: The text should be well-structured and clearly convey its main points. While complete paragraphs are ideal, bullet points or other concise formats are acceptable as long as the text maintains its semantic meaning and informative value.

3. Absence of non-informative content: The text should not contain bibliographies, reference lists, copyright notices, or other credits that do not contribute to the main content. It should also not include meaningless text fragments or text that appears to be a link without providing useful information.

4. Non-promotional content: The text should not be an advertisement for products or services, whether paid or free.

5. Objectivity: The text should maintain an objective tone and avoid overly detailed anecdotal content or subjective and emotional language.

First, write out your analysis and reasoning on the above criteria inside <reasoning></reasoning> tags.


After your reasoning, provide a value score from 1-5 in a <score></score> section, where:

1 = Completely useless
2 = Mostly useless
3 = Somewhat useful
4 = Quite useful
5 = Extremely useful

Please focus on critically evaluating the merits of the content as a source, not the content's relevance to the presentation topic. Highlight both the strengths and shortcomings of the text in your reasoning. Remember, provide your <reasoning></reasoning> first, then your numeric <score></score>.""",
        },
        {
            "role": """assistant""",
            "content": """<reasoning>
The extracted text appears to be fragments of author information, copyright notices, and submission details for a scientific journal article. It does not contain any substantive, informative content related to the topic of microplastics exposure. There are no explanations, facts, statistics, or other objective information that could be used as background or context in a presentation.

The text is disjointed and poorly organized, consisting of author names and affiliations, dates, and copyright statements. It lacks any coherent structure or main points relevant to the topic.

Most of the content is non-informative bibliographic information, copyright notices, and submission details that do not contribute anything meaningful to the subject of microplastics exposure metrics, levels, or sources. There are no complete sentences or paragraphs, just fragments of ancillary information.

The text does not contain any promotional content, as it appears to just be snippets from a scientific journal. However, the lack of any objective, informative content means it is not suitable as a source.
</reasoning>

<score>1</score>""",
        },
        {
            "role": """user""",
            "content": """Your task is to rate a piece of text that has been extracted from a website for its potential value as a source in putting together a presentation about All the services provided by AWS.

First, here is the extracted text to analyze:

<extracted_text>
With EC2 launch type, you can use Amazon ECS to manage a cluster of servers and schedule placement of containers on the servers. Amazon ECS keeps track of all the CPU, memory and other resources in your cluster, and also finds the best server for a container to run on based on your specified resource requirements.
You are responsible for provisioning, patching, and scaling clusters of servers.

With Fargate launch type, all you have to do is package your application in containers, specify the CPU and memory requirements, define networking and IAM policies, and launch the application. EC2 launch type allows you to have server-level, more granular control over the infrastructure that runs your container applications. With EC2 launch type, you can use Amazon ECS to manage a cluster of servers and schedule placement of containers on the servers.

This removes the need to choose server types, decide when to scale your clusters, or optimize cluster packing. Fargate removes the need for you to interact with or think about servers or clusters. Fargate lets you focus on designing and building your applications instead of managing the infrastructure that runs them.
Amazon ECS has two modes: Fargate launch type and EC2 launch type.

Fargate lets you focus on designing and building your applications instead of managing the infrastructure that runs them.
Amazon ECS has two modes: Fargate launch type and EC2 launch type. With Fargate launch type, all you have to do is package your application in containers, specify the CPU and memory requirements, define networking and IAM policies, and launch the application.

AWS Fargate is a compute engine for Amazon ECS that allows you to run containers without having to manage servers or clusters. With AWS Fargate, you no longer have to provision, configure, and scale clusters of VMs to run containers. This removes the need to choose server types, decide when to scale your clusters, or optimize cluster packing. Fargate removes the need for you to interact with or think about servers or clusters.
</extracted_text>

Consider the following criteria when evaluating the text:

1. Informative content: The text should contain objective, informative content that can be used in a presentation, such as explanations, comparisons, definitions, statistics, facts, or insights. The information should provide valuable context and background on the topic.

2. Clarity and organization: The text should be well-structured and clearly convey its main points. While complete paragraphs are ideal, bullet points or other concise formats are acceptable as long as the text maintains its semantic meaning and informative value.

3. Absence of non-informative content: The text should not contain bibliographies, reference lists, copyright notices, or other credits that do not contribute to the main content. It should also not include meaningless text fragments or text that appears to be a link without providing useful information.

4. Non-promotional content: The text should not be an advertisement for products or services, whether paid or free.

5. Objectivity: The text should maintain an objective tone and avoid overly detailed anecdotal content or subjective and emotional language.

First, write out your analysis and reasoning on the above criteria inside <reasoning></reasoning> tags.


After your reasoning, provide a value score from 1-5 in a <score></score> section, where:

1 = Completely useless
2 = Mostly useless
3 = Somewhat useful
4 = Quite useful
5 = Extremely useful

Please focus on critically evaluating the merits of the content as a source, not the content's relevance to the presentation topic. Highlight both the strengths and shortcomings of the text in your reasoning. Remember, provide your <reasoning></reasoning> first, then your numeric <score></score>.""",
        },
        {
            "role": """assistant""",
            "content": """<reasoning>
The text provides useful information comparing the EC2 and Fargate launch types for running containers on Amazon ECS. It explains the key differences between the two approaches:

- With EC2 launch type, you manage the cluster of servers yourself and Amazon ECS schedules containers on those servers. This gives you more granular control over the infrastructure.

- With Fargate launch type, you just package your application in containers, specify the resource requirements, and launch it. AWS manages the underlying server infrastructure for you. This removes the need to manage servers and clusters yourself.

The text is clearly organized, using paragraphs to separate the main points. The content is objective and informative, focusing on factual comparisons rather than subjective opinions or promotions. There are no bibliographies, references, or other non-informative sections.

However, the text is quite narrowly focused on just the EC2 vs Fargate distinction. For a broad presentation on "all the services provided by AWS", this text would only be relevant to one specific aspect. It doesn't cover the vast majority of other AWS services and offerings. More context would be needed around how Amazon ECS and the EC2/Fargate options fit into AWS's overall portfolio of services.

So in summary, the text provides clear and useful information, but only covers a very specific subtopic in limited depth. It would need to be combined with a lot of additional sources to assemble a comprehensive presentation on all of AWS's services. On its own, its usefulness is somewhat limited by its narrow scope.
</reasoning>

<score>3</score>""",
        },
        {
            "role": """user""",
            "content": """Your task is to rate a piece of text that has been extracted from a website for its potential value as a source in putting together a presentation about All the services provided by AWS.

First, here is the extracted text to analyze:

<extracted_text>
Additionally, the AWS Organizations service lets a business establish and manage policies for multiple AWS accounts.
Amazon Web Services has also introduced tools that automatically assess potential security risks. Amazon Inspector analyzes an AWS environment for vulnerabilities that might impact security and compliance. Amazon Macie uses ML technology to protect sensitive cloud data.

This is backed by a deep set of cloud security tools, with over 300 security, compliance, and governance services and features. AWS supports 143 security standards and compliance certifications, and all 117 AWS services that store customer data offer the ability to encrypt that data.

AWS is architected to be the most flexible and secure cloud computing environment available today. Our core infrastructure is built to satisfy the security requirements for the military, global banks, and other high-sensitivity organizations. This is backed by a deep set of cloud security tools, with over 300 security, compliance, and governance services and features.

AWS is architected to be the most flexible and secure cloud computing environment available today. Our core infrastructure is built to satisfy the security requirements for the military, global banks, and other high-sensitivity organizations. This is backed by a deep set of cloud security tools, with over 300 security, compliance, and governance services and features, as well as support for 143 security standards and compliance certifications.

Amazon Inspector analyzes an AWS environment for vulnerabilities that might impact security and compliance. Amazon Macie uses ML technology to protect sensitive cloud data.
AWS also includes tools and services that provide software- and hardware-based encryption, protect against distributed denial-of-service (DDoS) attacks, acquire secure sockets layer and Transport Layer Security certificates, and filter potentially harmful traffic to web applications.
</extracted_text>

Consider the following criteria when evaluating the text:

1. Informative content: The text should contain objective, informative content that can be used in a presentation, such as explanations, comparisons, definitions, statistics, facts, or insights. The information should provide valuable context and background on the topic.

2. Clarity and organization: The text should be well-structured and clearly convey its main points. While complete paragraphs are ideal, bullet points or other concise formats are acceptable as long as the text maintains its semantic meaning and informative value.

3. Absence of non-informative content: The text should not contain bibliographies, reference lists, copyright notices, or other credits that do not contribute to the main content. It should also not include meaningless text fragments or text that appears to be a link without providing useful information.

4. Non-promotional content: The text should not be an advertisement for products or services, whether paid or free.

5. Objectivity: The text should maintain an objective tone and avoid overly detailed anecdotal content or subjective and emotional language.

First, write out your analysis and reasoning on the above criteria inside <reasoning></reasoning> tags.


After your reasoning, provide a value score from 1-5 in a <score></score> section, where:

1 = Completely useless
2 = Mostly useless
3 = Somewhat useful
4 = Quite useful
5 = Extremely useful

Please focus on critically evaluating the merits of the content as a source, not the content's relevance to the presentation topic. Highlight both the strengths and shortcomings of the text in your reasoning. Remember, provide your <reasoning></reasoning> first, then your numeric <score></score>.""",
        },
        {
            "role": """assistant""",
            "content": """<reasoning>
The text provides some useful information about AWS security services and features, such as:

- AWS Organizations for managing policies across multiple accounts
- Security tools like Amazon Inspector and Amazon Macie that assess security risks and protect data
- Support for encryption, DDoS protection, SSL/TLS certificates, and web application firewalls
- Meeting security requirements of highly sensitive organizations like the military and banks

This content is informative and provides good background on AWS's security capabilities. The text is also clearly written and organized, presenting the information in a logical flow.

However, the text has some significant shortcomings:

- It only covers security services, which is just one aspect of AWS's overall service offerings. To be a comprehensive source on all AWS services, it would need to discuss many other categories like compute, storage, database, analytics, machine learning, etc.

- The text repeats itself substantially, with some paragraphs appearing nearly verbatim. This redundancy does not add additional value.

- While the text provides a high-level overview of some security features, it lacks more specific details and examples that would make it a richer, more useful source. Mentioning the number of security standards supported (143) is a start, but naming and explaining some of the most important ones would be better.

- The tone comes across as somewhat promotional of AWS, focusing on its "deep set of cloud security tools" and "most flexible and secure" infrastructure. A more objective take that critically evaluates AWS's security compared to other cloud providers would improve the text as a source.
</reasoning>

<score>3</score>""",
        },
        {
            "role": """user""",
            "content": """Your task is to rate a piece of text that has been extracted from a website for its potential value as a source in putting together a presentation about All the services provided by AWS.

First, here is the extracted text to analyze:

<extracted_text>
AWS's Virtual Private Cloud (VPC) is a powerful tool that companies can use to create isolated, secure instances that can run code and applications without affecting the public or internal networks. In this post, we'll explore how VPC works and what benefits it has for businesses.
AWS (Amazon web service) S3 is a cloud-based storage service that offers an extensive range of features and storage classes.

In this tutorial, we'll walk you through the key features of AWS and how it can benefit your business. So whether you're a beginner or an experienced user, this tutorial is for you.
Amazon Web Services is a comprehensive suite of cloud computing services that lets you create, operate, and manage a variety of applications. AWS offers a broad range of services that can be used to power your business and help you increase efficiency and improve your scalability.

In this article, we will provide an overview of the AWS S3, its features, and storage classes.
AWS IAM is a powerful tool that can help you manage your AWS resources more effectively. It Includes IAM is, its components, and some of its key features and also learn how to use IAM to manage user permissions and access to resources and to monitor and manage your AWS infrastructure.
AWS CloudFront is a service that makes it easy for you to distribute your web content to multiple endpoints.

AWS offers a broad range of services that can be used to power your business and help you increase efficiency and improve your scalability.
As the world's leading provider of cloud services, Amazon Web Services (AWS) has plenty to offer business owners. It offers a variety of services, including Amazon Elastic Compute Cloud (EC2), Amazon Simple Storage Service (S3), and Amazon Route 53.

If you're in the market for a cloud computing platform, there's no doubt that Amazon Web Services (AWS) is a top contender. AWS is known for its ease of use and its vast array of features, both of which make it an ideal platform for businesses of all sizes. It allows users to access various computing, storage, and networking services from anywhere in the world. In this tutorial, we'll walk you through the key features of AWS and how it can benefit your business.
</extracted_text>

Consider the following criteria when evaluating the text:

1. Informative content: The text should contain objective, informative content that can be used in a presentation, such as explanations, comparisons, definitions, statistics, facts, or insights. The information should provide valuable context and background on the topic.

2. Clarity and organization: The text should be well-structured and clearly convey its main points. While complete paragraphs are ideal, bullet points or other concise formats are acceptable as long as the text maintains its semantic meaning and informative value.

3. Absence of non-informative content: The text should not contain bibliographies, reference lists, copyright notices, or other credits that do not contribute to the main content. It should also not include meaningless text fragments or text that appears to be a link without providing useful information.

4. Non-promotional content: The text should not be an advertisement for products or services, whether paid or free.

5. Objectivity: The text should maintain an objective tone and avoid overly detailed anecdotal content or subjective and emotional language.

First, write out your analysis and reasoning on the above criteria inside <reasoning></reasoning> tags.


After your reasoning, provide a value score from 1-5 in a <score></score> section, where:

1 = Completely useless
2 = Mostly useless
3 = Somewhat useful
4 = Quite useful
5 = Extremely useful

Please focus on critically evaluating the merits of the content as a source, not the content's relevance to the presentation topic. Highlight both the strengths and shortcomings of the text in your reasoning. Remember, provide your <reasoning></reasoning> first, then your numeric <score></score>.""",
        },
        {
            "role": """assistant""",
            "content": """<reasoning>
The text provides an overview of several key AWS services, including VPC, S3, IAM, and CloudFront. It explains at a high level what these services do and some of their benefits and use cases for businesses. This information would be useful background and context to include in a presentation on AWS's service offerings.

However, the text reads more like a series of introductory paragraphs rather than an in-depth or well-organized explanation of AWS services. It jumps around between different services without a clear structure. Some services are described in more detail than others. The text also contains some repetition, such as mentioning that AWS offers services to help businesses multiple times.

To serve as a strong source for a presentation, the text would benefit from a clearer organizational structure, more consistent level of detail on each service, and removal of repetitive statements. Specific facts, statistics, or customer examples for each service would also enhance its informative value. 

The text maintains an objective, non-promotional tone which is good for an informative presentation. But it lacks the depth and focus to be a primary source on its own. It would need to be combined with additional sources that provide more substantive information about the key AWS services and their features, pricing, comparisons to alternatives, etc.
</reasoning>

<score>3</score>""",
        },
        {
            "role": """user""",
            "content": """Your task is to rate a piece of text that has been extracted from a website for its potential value as a source in putting together a presentation about A comparison of Caged, Cage-Free, Free-Range, and Pasture-Raised Eggs.

First, here is the extracted text to analyze:

<extracted_text>
The Certified Humane Program, meanwhile, states that free-range hens must have at least 2 square feet of outdoor space that they can access for at least 6 hours per day.
Hens that produce pasture-raised eggs have regular access to a large outdoor space that is covered in grass or other vegetation. This is the pasture.
There are various definitions of constitutes pasture-raised eggs.
Animal Welfare Approved offer the highest level of animal welfare.

The Certified Humane Program states that in order to be considered pasture-raised, each bird must have access to a living vegetation-covered pasture for at least 6 hours per day. Each hen must have at least 108 square feet of pasture.
The cheapest way to produce eggs is by using the conventional caged method. This is because it is less labor-intensive. Also, hens living in such controlled conditions do not eat as much as those that are free to roam around.

The term “free range” is regulated by the USDA. USDA free range eggs come from hens that are allowed to roam freely outdoors in a fenced area. This means they have more space and access to natural sunlight and fresh air than hens that are kept in cages and those labeled cage free.
The exact amount of time that hens spend outside and the size of the outdoor area can vary greatly depending on the producer.

The American Humane Certified program states that cage-free hens must have a minimum of 1.25 square feet of floor space each, plus access to perches and nesting boxes.
Many egg cartons carry the “free-range” label. The main difference between cage-free and free-range eggs is that the latter come from hens that, in addition to the extra space that cage-free birds have, can also access some form of outside area.

In cage-free barns, hens can move around and spread their wings. Some have an outdoor area, though it is usually small and hard to get to. The buildings have nesting areas, most commonly in the center of the structure. Many cage-free systems don’t have separate aerial perches for the hens, although they do allow the birds to perch on other structures in the house, such as the nest boxes, feed and water lines. etc.
</extracted_text>

Consider the following criteria when evaluating the text:

1. Informative content: The text should contain objective, informative content that can be used in a presentation, such as explanations, comparisons, definitions, statistics, facts, or insights. The information should provide valuable context and background on the topic.

2. Clarity and organization: The text should be well-structured and clearly convey its main points. While complete paragraphs are ideal, bullet points or other concise formats are acceptable as long as the text maintains its semantic meaning and informative value.

3. Absence of non-informative content: The text should not contain bibliographies, reference lists, copyright notices, or other credits that do not contribute to the main content. It should also not include meaningless text fragments or text that appears to be a link without providing useful information.

4. Non-promotional content: The text should not be an advertisement for products or services, whether paid or free.

5. Objectivity: The text should maintain an objective tone and avoid overly detailed anecdotal content or subjective and emotional language.

First, write out your analysis and reasoning on the above criteria inside <reasoning></reasoning> tags.


After your reasoning, provide a value score from 1-5 in a <score></score> section, where:

1 = Completely useless
2 = Mostly useless
3 = Somewhat useful
4 = Quite useful
5 = Extremely useful

Please focus on critically evaluating the merits of the content as a source, not the content's relevance to the presentation topic. Highlight both the strengths and shortcomings of the text in your reasoning. Remember, provide your <reasoning></reasoning> first, then your numeric <score></score>.""",
        },
        {
            "role": """assistant""",
            "content": """<reasoning>
The text provides useful, objective information comparing the different egg production methods, including:

- Definitions of what qualifies as "free-range" and "pasture-raised" under various certification programs, with specific space requirements per hen
- A comparison of the amount of outdoor access hens have in the different systems
- Details on the housing conditions and hen behavior in cage-free barns
- Insight that caged eggs are cheapest to produce due to lower labor and feed costs

The information is presented in an organized way, clearly delineating the differences between the egg types. The text maintains an objective, factual tone focused on the key characteristics of each production method without extraneous details.

However, the text does not cover all the egg types in the presentation topic, as it is missing information specifically about caged eggs. More details comparing the pros and cons of each type for a robust comparison would further strengthen this as a source.
</reasoning>

<score>4</score>""",
        },
        {
            "role": """user""",
            "content": """Your task is to rate a piece of text that has been extracted from a website for its potential value as a source in putting together a presentation about Understanding Microplastics Exposure Metrics, Safe Levels, and Common Sources.

First, here is the extracted text to analyze:

<extracted_text>
The true amount of MP humans may be exposed to via food still cannot be assessed with certainty as many data gaps in MPs research exists (Smith et al. 2018). Also, little is known about the fate of MPs in the digestive tract, absorption uptake kinetics, bioavailability and distribution of MPs in the human body. Exposure to MPs is a complex issue as potential negative health effects can arise from plastics themselves, monomers, additives and various pollutants.

This review aimed to provide relevant information on the possible health effect of ingested MPs, the occurrence, and levels of MPs contamination in various foods and estimated exposure to MPs through food. Potential toxic consequences from exposure to MPs through food can arise from MPs themselves, diffused monomers and additives but also from sorbed contaminants or microorganisms that colonise MPs.

According to available data, conventional and optimised wastewater treatment can effectively remove more than 90% of MPs from wastewater (WHO 2019). Plastic bottles and caps that are used in bottled water may also be sources of MPs in drinking water. To date, several studies investigated the presence of MPs in water. As shown in Table 1 contamination of water with MPs is a global issue with comparatively higher amounts of MPs present in bottled water.

Furthermore, the identification of MPs in human placenta raised serious concern about exposure in utero (46). A meta-analysis of existing data on the concentrations of MPs in various sources of human exposure suggested a mean ingestion dose in the range of 0.10–5 g/week (47). Zhang et al. (48) assessed the mass of PET and PC MPs recovered from the feces of dogs and cats, which were used as surrogates for biomonitoring of MPs in humans, and found an excretion rate of 0.03–677 mg MPs/week.

The ubiquitous exposure of humans to microplastics (MPs) through inhalation of particles in air and ingestion in dust, water, and diet is well established. Humans are estimated to ingest tens of thousands to millions of MP particles annually, or on the order of several milligrams daily. Available information suggests that inhalation of indoor air and ingestion of drinking water bottled in plastic are the major sources of MP exposure. Little is known on the occurrence of MPs in human diet.
</extracted_text>

Consider the following criteria when evaluating the text:

1. Informative content: The text should contain objective, informative content that can be used in a presentation, such as explanations, comparisons, definitions, statistics, facts, or insights. The information should provide valuable context and background on the topic.

2. Clarity and organization: The text should be well-structured and clearly convey its main points. While complete paragraphs are ideal, bullet points or other concise formats are acceptable as long as the text maintains its semantic meaning and informative value.

3. Absence of non-informative content: The text should not contain bibliographies, reference lists, copyright notices, or other credits that do not contribute to the main content. It should also not include meaningless text fragments or text that appears to be a link without providing useful information.

4. Non-promotional content: The text should not be an advertisement for products or services, whether paid or free.

5. Objectivity: The text should maintain an objective tone and avoid overly detailed anecdotal content or subjective and emotional language.

First, write out your analysis and reasoning on the above criteria inside <reasoning></reasoning> tags.


After your reasoning, provide a value score from 1-5 in a <score></score> section, where:

1 = Completely useless
2 = Mostly useless
3 = Somewhat useful
4 = Quite useful
5 = Extremely useful

Please focus on critically evaluating the merits of the content as a source, not the content's relevance to the presentation topic. Highlight both the strengths and shortcomings of the text in your reasoning. Remember, provide your <reasoning></reasoning> first, then your numeric <score></score>.""",
        },
        {
            "role": """assistant""",
            "content": """<reasoning>
The text provides highly relevant and informative content on the topic of microplastics exposure in humans. Key strengths include:

- Covers important aspects like exposure routes (ingestion, inhalation), estimated exposure levels, major sources (drinking water, diet), and potential health effects
- Provides specific data points and statistics to quantify exposure, such as estimated ingestion of tens of thousands to millions of particles annually or several milligrams daily
- Discusses data gaps and unknowns that still need to be researched, providing important context
- Well-organized into coherent paragraphs that cover different aspects of the topic
- Maintains an objective, scientific tone focused on evidence 
- Does not contain irrelevant content like references, copyright notices or promotions

Some limitations to consider:
- A few sentences are long and complex, which could be edited for clarity in a presentation
- Mentions a couple specific studies without full context, which may require further explanation to an audience

Overall, this is a highly useful, information-dense text that covers key aspects of microplastics exposure in a clear, objective manner. With some minor editing and synthesis, it could serve as valuable source material to build a comprehensive presentation on the topic. The specific data points help quantify the issue while the discussion of data gaps provides important context.
</reasoning>

<score>5</score>""",
        },
        {
            "role": """user""",
            "content": f"""Your task is to rate a piece of text that has been extracted from a website for its potential value as a source in putting together a presentation about {topic}.\n\nFirst, here is the extracted text to analyze:\n\n<extracted_text>\n{text}\n</extracted_text>\n\nConsider the following criteria when evaluating the text:\n\n1. Informative content: The text should contain objective, informative content that can be used in a presentation, such as explanations, comparisons, definitions, statistics, facts, or insights. The information should provide valuable context and background on the topic.\n\n2. Clarity and organization: The text should be well-structured and clearly convey its main points. While complete paragraphs are ideal, bullet points or other concise formats are acceptable as long as the text maintains its semantic meaning and informative value.\n\n3. Absence of non-informative content: The text should not contain bibliographies, reference lists, copyright notices, or other credits that do not contribute to the main content. It should also not include meaningless text fragments or text that appears to be a link without providing useful information.\n\n4. Non-promotional content: The text should not be an advertisement for products or services, whether paid or free.\n\n5. Objectivity: The text should maintain an objective tone and avoid overly detailed anecdotal content or subjective and emotional language.\n\nFirst, write out your analysis and reasoning on the above criteria inside <reasoning></reasoning> tags.\n\n\nAfter your reasoning, provide a value score from 1-5 in a <score></score> section, where:\n\n1 = Completely useless\n2 = Mostly useless\n3 = Somewhat useful\n4 = Quite useful\n5 = Extremely useful\n\nPlease focus on critically evaluating the merits of the content as a source, not the content"s relevance to the presentation topic. Highlight both the strengths and shortcomings of the text in your reasoning. Remember, provide your <reasoning></reasoning> first, then your numeric <score></score>.""",
        },
    ]
