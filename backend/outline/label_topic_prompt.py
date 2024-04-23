
def get_prompt(documents, keywords, topic):
    return f"""<s>[INST] You are an expert at labeling subtopics given a main topic and excerpts containing a subtopic. Your task is to generate a short, descriptive label for the subtopic found in the provided excerpts, using 8 words or less. The label should succinctly capture the essence of the subtopic. Focus on the key information and themes from the excerpts to craft an informative and on-topic label. I'm doing some research about MongoDB vs DynamoDB: A Comparative Analysis (my main topic).
I think I've found a subtopic in these excerpts from my research, but I'm not quite sure what to call it: 

Also, take into account how much speed your application needs and what you can sacrifice in terms of information consistency in order to get that speed. In other words, what's worse: a couple of seconds of delay to get the answer you need or less-than-trustworthy data?

There is no size fits all, and every production system is different with its own needs and quirks; the following questions should lead to answers that will cement your position on which one to choose.  
Is your team deploying a mission-critical application that must be highly available at all times without manual intervention?  
Are you comfortable running on proprietary software, without control or knowing what's going on under the hood?

First of all, you should assess the skill level of your team members and consider the following questions:  
* Will they be able to implement a MongoDB?
* Will they be able to make sure it runs smoothly 24x7?  
If you answer no to those questions, then you should give DynamoDB a deeper look.  
Another option you might want to consider is MongoDB Atlas (a managed MongoDB service similar to DynamoDB).

Does your team have the skill to implement Mongo? Will they be able to support it and make sure it runs smoothly? If not, you may be better off going with Dynamo as a managed solution.

It depends on your use case. In many cases it will, but you will need to keep in mind that how you query data will be different. Some cases will prevent you from choosing DynamoDB, such as the need to store binary data > 400KB or using it as a geospatial database.

The subtopic is described by the following keywords: questions, mongodb, deploying, queries, mongo, answers, managed, application, answer, evaluate
Based on the above information, can you give a short label of the subtopic? Maximum 8 words. [/INST] Short Label:Decide based on your team and use case</s>[INST] You are an expert at labeling subtopics given a main topic and excerpts containing a subtopic. Your task is to generate a short, descriptive label for the subtopic found in the provided excerpts, using 8 words or less. The label should succinctly capture the essence of the subtopic. Focus on the key information and themes from the excerpts to craft an informative and on-topic label. I'm doing some research about The 7 Natural Wonders of the World (my main topic).
I think I've found a subtopic in these excerpts from my research, but I'm not quite sure what to call it: 

The reef provides a home for over 400 species of hard coral, 300 species of soft coral, 1,600 species of fish, 134 species of sharks and rays, 30 species of whales and dolphins, and six species of turtle.  
This fact makes it one of the most diverse ecosystems on the planet.

Renowned for its biological diversity, the reef is home to more than 1,500 fish species, 411 types of hard coral, and a third of the world's soft corals. Additionally, it supports 134 shark and ray species, six of the seven threatened marine turtle species, over 30 marine mammal species, and serves as a critical breeding ground for humpback whales and a sanctuary for endangered species like the dugong and large green turtle.

The gem of Australia, the Great Barrier Reef is both breathtakingly beautiful and ecologically important.  
A delight for snorkelers, scuba divers and sunbathers, the world’s largest coral reef includes over 900 islands, 2,900 separate reefs and a plethora of diverse marine life. Covering over 133,000 square miles, the Great Barrier Reef is larger than the Great Wall of China (and, unlike the wall, it is actually visible from space).  
Ready to dive deeper? Check out these amazing facts.

Aerial view of the Great Barrier Reef.  
The Great Barrier Reef, located off Queensland, Australia in the Coral Sea, is the world's largest coral reef system, extending over 2,300 kilometers with 2,900 individual reefs and 900 islands across 344,400 square kilometers of ocean. Renowned for its biological diversity, the reef is home to more than 1,500 fish species, 411 types of hard coral, and a third of the world's soft corals.

As the world's largest coral reef, the Great Barrier Reef includes over 900 islands, roughly 3,000 separate reefs, and sustains a diverse ecosystem. Measuring approximately 2,300 kilometers in length, it covers an immense area of the ocean, much of it a long way offshore.  
Boat trips and excursions offer visitors a chance to experience the highlights of the Great Barrier Reef. Snorkeling or dive trips can be arranged, and provide opportunities to see colorful fish, coral, and marine life.

The subtopic is described by the following keywords: corals, reefs, coral, reef, snorkeling, australia, whales, islands, largest, ocean
Based on the above information, can you give a short label of the subtopic? Maximum 8 words. [/INST] Short Label:The Great Barrier Reef</s>[INST] You are an expert at labeling subtopics given a main topic and excerpts containing a subtopic. Your task is to generate a short, descriptive label for the subtopic found in the provided excerpts, using 8 words or less. The label should succinctly capture the essence of the subtopic. Focus on the key information and themes from the excerpts to craft an informative and on-topic label. I'm doing some research about The Transformer Model: Revolutionizing Natural Language Processing (my main topic).
I think I've found a subtopic in these excerpts from my research, but I'm not quite sure what to call it: 

where  θ = t r k , r = N 2 / d {{\displaystyle 	heta ={{rac {{t}}{{r^{{k}}}}}},r=N^{{2/d}}}} .  
Here,  N {{\displaystyle N}} is a free parameter that should be significantly larger than the biggest  k {{\displaystyle k}} that would be input into the positional encoding function. In the original paper, the authors chose  N = 10000 {{\displaystyle N=10000}} .  
The function is in a simpler form when written as a complex function of type  f : R → C d / 2 {{\displaystyle f:\mathbb {{R}} 	o \mathbb {{C}} ^{{d/2}}}}

A positional encoding is a fixed-size vector representation that encapsulates the relative positions of tokens within a target sequence: it provides the transformer model with information about _where_ the words are in the input sequence.  
The positional encoding is defined as a function of type  f : R → R d ; d ∈ Z , d > 0 {{\displaystyle f:\mathbb {{R}} 	o \mathbb {{R}} ^{{d}};d\in \mathbb {{Z}} ,d>0}} , where  d {{\displaystyle d}} is a positive even integer.

The function is in a simpler form when written as a complex function of type  f : R → C d / 2 {{\displaystyle f:\mathbb {{R}} 	o \mathbb {{C}} ^{{d/2}}}}  
f ( t ) = ( e i t / r k ) k = 0 , 1 , … , d 2 − 1 {{\displaystyle f(t)=\left(e^{{it/r^{{k}}}}
ight)_{{k=0,1,\ldots ,{{rac {{d}}{{2}}}}-1}}}}  
where  r = N 2 / d {{\displaystyle r=N^{{2/d}}}} .  
The main reason the authors chose this as the positional encoding function is that it allows one to perform shifts as linear transformations:

To give the model a sense of the order of the words, we add positional encoding vectors -- the values of which follow a specific pattern.  
If we assumed the embedding has a dimensionality of 4, the actual positional encodings would look like this:  
A real example of positional encoding with a toy embedding size of 4  
What might this pattern look like?  
In the following figure, each row corresponds to a positional encoding of a vector.

That's because the values of the left half are generated by one function (which uses sine), and the right half is generated by another function (which uses cosine). They're then concatenated to form each of the positional encoding vectors.  
The formula for positional encoding is described in the paper (section 3.5). You can see the code for generating positional encodings in `get_timing_signal_1d()`. This is not the only possible method for positional encoding.

The subtopic is described by the following keywords: encodings, positional, encoding, coded, get_timing_signal_1d, embedding, vector, transformations, 512, code
Based on the above information, can you give a short label of the subtopic? Maximum 8 words. [/INST] Short Label:Positional Encoding in Transformer Models</s>[INST] You are an expert at labeling subtopics given a main topic and excerpts containing a subtopic. Your task is to generate a short, descriptive label for the subtopic found in the provided excerpts, using 8 words or less. The label should succinctly capture the essence of the subtopic. Focus on the key information and themes from the excerpts to craft an informative and on-topic label. I'm doing some research about Cultural Differences Between Japan and the USA (my main topic).
I think I've found a subtopic in these excerpts from my research, but I'm not quite sure what to call it: 

“To keep places clean, it was believed, was important to keep the gods happy and to bring good karma.”  
The Japanese have a lot of respect for Mother Nature (as we all should) and it’s pretty obvious by looking at their immaculate streets. Just try to find old gum on the sidewalks. Trash on the streets? Not a chance. And the subways? I was floored the first time I took a seat on a Tokyo subway.

And when you do get back to your hotel, you will notice that disposing of this packaging is a bit more complicated than in the US. Instead of having just trash and recycling, there are many more classifications for how to divide waste.  
Don’t just mindlessly throw your garbage away! Read this guide to trash separation and disposal in Japan.  
As inconvenient as this may seem to many Westerners, the Japanese relationship to trash actually helps the country stay one of the cleanest in the world.

Ironically, I was surprised to see so few (if any) public trash cans, which seemed counterintuitive -- where are these people _actually_ throwing their trash? But the reason you won’t find trash bins anywhere is because of a 1995 terrorist attack from invisible and lethal sarin gas that left 6,000 people injured and led to the removal of public trash bins. Over the years, the locals have been accustomed to holding on to their garbage until they come across a trash bin.

Just try to find old gum on the sidewalks. Trash on the streets? Not a chance. And the subways? I was floored the first time I took a seat on a Tokyo subway. No graffiti on the windows, the hand rails were sparkling, and the whole thing looked like a shiny new toy. It makes the New York City subway feel like a moving petri dish.  
Ironically, I was surprised to see so few (if any) public trash cans, which seemed counterintuitive -- where are these people _actually_ throwing their trash?

Over the years, the locals have been accustomed to holding on to their garbage until they come across a trash bin. And the Japanese are big on recycling, so it’s super easy with their color coded disposal bins -- it’s like Recycling for Dummies. And if you don’t keep up your trash duties? Your neighbor will make sure you do. _Gomi toban_ is the idea that neighbors look after each other’s trash to ensure it’s done properly, taking Neighborhood Watch to a whole new level.

The subtopic is described by the following keywords: garbage, trash, janitors, disposal, tokyo, recycling, waste, japanese, _gomi, subways
Based on the above information, can you give a short label of the subtopic? Maximum 8 words. [/INST] Short Label:Japanese cleanliness norms and waste disposal practices</s>[INST] You are an expert at labeling subtopics given a main topic and excerpts containing a subtopic. Your task is to generate a short, descriptive label for the subtopic found in the provided excerpts, using 8 words or less. The label should succinctly capture the essence of the subtopic. Focus on the key information and themes from the excerpts to craft an informative and on-topic label. I'm doing some research about The Coton de Tulear Dog Breed (my main topic).
I think I've found a subtopic in these excerpts from my research, but I'm not quite sure what to call it: 

The standard advocates that the lips should preferably be tight and of the same colour as the nose, specifically black in the Coton de Tuléar Club of America standard. A Coton de Tuléar's teeth can be either in a scissor bite or pincer bite. Its eyes are normally round, dark in colour, and wide-set. Traditionally, the expression is lively, intelligent, bright, and merry. Typically, the Coton de Tuléar's ears are triangular and set high.

“Coton” is the French word for cotton. Like the name suggests, the most conspicuous feature of the Coton de Tulear is its coat, which is cottony or fluffy rather than silky. It has a long topcoat. The fluffy hair covers the thin, lightly-muscled forelegs. Colors come in white, white with lemon, white with shades of brown, white with black, white with gray or tri-colored. (pure white is preferred by show breeders.) Some have slightly yellowish markings on the ears.

The breed even has a fade gene that causes the colors, which are very dark when a puppy, to fade and turn white at the base of the hair as it lengthens; that is why the Champagne or Champagne Teddy Bear Coton eventually turns white when the adult hair comes in.) The Fédération Cynologique Internationale standard specifies that the Coton's coat should be white but may also have tan or "lemon" color on their ears and body. The coat, however, must be primarily white with no black hair.

Black-and-white is defined as pure white with prominent black patches on the head and body (no white-to-black ratio is specified or favored). Tri-color is described as mostly white with some brown markings and dustings of black on the body and head. A honey bear tri-color has light brown with black tips that gradually fades to an off-white or lemon color.

The coat, however, must be primarily white with no black hair. The US-based Coton de Tuléar Club of America allows for three different but equally favorable colorings: white, black-and-white, and tri-color, including "honey bear". White is described as nearly all white, sometimes with tan or champagne coloring on the ears, face, or back. Black-and-white is defined as pure white with prominent black patches on the head and body (no white-to-black ratio is specified or favored).

The subtopic is described by the following keywords: coton, white, colour, color, cynologique, brown, colors, coat, pink, tuléar
Based on the above information, can you give a short label of the subtopic? Maximum 8 words. [/INST] Short Label:Physical Characteristics, Coat Textures and Colors</s>[INST] You are an expert at labeling subtopics given a main topic and excerpts containing a subtopic. Your task is to generate a short, descriptive label for the subtopic found in the provided excerpts, using 8 words or less. The label should succinctly capture the essence of the subtopic. Focus on the key information and themes from the excerpts to craft an informative and on-topic label. I"m doing some research about {topic} (my main topic).\nI think I"ve found a subtopic in these excerpts from my research, but I"m not quite sure what to call it: \n\n{documents}\n\nThe subtopic is described by the following keywords: {keywords}\nBased on the above information, can you give a short label of the subtopic? Maximum 8 words. [/INST]Short Label:"""