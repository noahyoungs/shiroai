<assistant_2>
#### Source: tmpt43elso2
URL: file:///var/folders/jp/99fbbz9959d892jf52cv2c3h0000gn/T/tmpt43elso2

_from: top level_
The Transformer follows this overall architecture using stacked self-attention and point-wise, fully connected layers for both the encoder and decoder, shown in the left and right halves of Figure 1, respectively.    3.1     Encoder and Decoder Stacks      Encoder:   The encoder is composed of a stack of N = 6 identical layers. Each layer has two sub-layers. The first is a multi-head self-attention mechanism, and the second is a simple, position- wise fully connected feed-forward network.

For each of these we use  dk = dv = d model /h = 64. Due to the reduced dimension of each head, the total computational cost is similar to that of single-head attention with full dimensionality.    3.2.3     Applications of Attention in our Model    The Transformer uses multi-head attention in three different ways:  • In "encoder-decoder attention" layers, the queries come from the previous decoder layer, and the memory keys and values come from the output of the encoder.

#### Source: Transformers In NLP | State-Of-The-Art-Models
URL: https://www.analyticsvidhya.com/blog/2019/06/understanding-transformers-nlp-state-of-the-art-models/

_from: top level_
It might look intimidating but don’t worry, we will break it down and understand it block by block.  
The above image is a superb illustration of Transformer’s architecture. Let’s first focus on the Encoder and Decoder parts only.  
Now focus on the below image. The Encoder block has 1 layer of a Multi-Head Attention followed by another layer of Feed Forward Neural Network. The decoder, on the other hand, has an extra Masked Multi-Head Attention.

So, z1 is the self-attention vector for the first word of the input sequence “Action gets results”. We can get the vectors for the rest of the words in the input sequence in the same fashion:  
Self-attention is computed not once but multiple times in the Transformer’s architecture, in parallel and independently. It is therefore referred to as Multi-head Attention. The outputs are concatenated and linearly transformed as shown in the figure below:

#### Source: Transformer (deep learning architecture) - Wikipedia
URL: https://en.wikipedia.org/wiki/Transformer_(machine_learning_model)

_from: top level_
Machine learning algorithm used for natural-language processing  
"Transformer architecture" redirects here. For the design of electrical transformers, see Transformer.  
A **transformer** is a deep learning architecture developed by Google and based on the multi-head attention mechanism, proposed in a 2017 paper "Attention Is All You Need". Text is converted to numerical representations called tokens, and each token is converted into a vector via looking up from a word embedding table.

#### Source: What is a Transformer?. An Introduction to Transformers and… | by Maxime | Inside Machine learning | Medium
URL: https://medium.com/inside-machine-learning/what-is-a-transformer-d07dd1fbec04

_from: Part 2: The Transformer_
After the multi-attention heads in both the encoder and decoder, we have a pointwise feed-forward layer. This little feed-forward network has identical parameters for each position, which can be described as a separate, identical linear transformation of each element from the given sequence.

_from: Part 2: The Transformer > Training_
This is specific to the Transformer architecture because we do not have RNNs where we can input our sequence sequentially. Here, we input everything together and if there were no mask, the multi-head attention would consider the whole decoder input sequence at each position.  
The process of feeding the correct shifted input into the decoder is also called Teacher-Forcing, as described in this blog.

#### Source: How do Transformers work? - Hugging Face NLP Course
URL: https://huggingface.co/learn/nlp-course/chapter1/4

_from: top level_
NLP Course documentation  
How do Transformers work?

#### Source: Demystifying Transformers Architecture in Machine Learning
URL: https://www.projectpro.io/article/transformers-architecture/840

_from: Demystifying Transformers Architecture in Machine Learning > Understanding Transformers Architecture in machine Learning > Key Components Of Transformers Architecture_
Self-Attention Mechanism  
This is the central component of the original Transformer architecture. Each word embeddings in the input word sequence attend to all the other words to compute a weighted representation of the sequence. The self-attention layers capture long-range dependencies between words and are used in both the encoder block and decoder block of the Transformer.  
Multi-Head Attention

This extends the self-attention mechanism by allowing the model to attend to multiple representation subspaces in parallel. It works by splitting the query, key, and value vectors into multiple smaller vectors, or "heads," and applying the key feature of the self-attention mechanism to each head separately.
</assistant_2>