#### Source: tmpt43elso2
URL: file:///var/folders/jp/99fbbz9959d892jf52cv2c3h0000gn/T/tmpt43elso2

_from: top level_
The Transformer follows this overall architecture using stacked self-attention and point-wise, fully connected layers for both the encoder and decoder, shown in the left and right halves of Figure 1, respectively.    3.1     Encoder and Decoder Stacks      Encoder:   The encoder is composed of a stack of N = 6 identical layers. Each layer has two sub-layers. The first is a multi-head self-attention mechanism, and the second is a simple, position- wise fully connected feed-forward network.

#### Source: Transformers In NLP | State-Of-The-Art-Models
URL: https://www.analyticsvidhya.com/blog/2019/06/understanding-transformers-nlp-state-of-the-art-models/

_from: top level_
So, z1 is the self-attention vector for the first word of the input sequence “Action gets results”. We can get the vectors for the rest of the words in the input sequence in the same fashion:  
Self-attention is computed not once but multiple times in the Transformer’s architecture, in parallel and independently. It is therefore referred to as Multi-head Attention. The outputs are concatenated and linearly transformed as shown in the figure below:

#### Source: Transformer (deep learning architecture) - Wikipedia
URL: https://en.wikipedia.org/wiki/Transformer_(machine_learning_model)

_from: Architecture > Scaled dot-product attention > Multi-head attention_
The computations for each attention head can be performed in parallel, which allows for fast processing. The outputs for the attention layer are concatenated to pass into the feed-forward neural network layers.  
Concretely, let the multiple attention heads be indexed by  i {\displaystyle i} , then we have

_from: Architecture > Encoder > Positional encoding_
for any constants  c j {\displaystyle c_{j}} . This allows the transformer to take any encoded position and find a linear sum of the encoded locations of its neighbors. This sum of encoded positions, when fed into the attention mechanism, would create attention weights on its neighbors, much like what happens in a convolutional neural network language model. In the author's words, "we hypothesized it would allow the model to easily learn to attend by relative position."

_from: Subsequent work > Efficient implementation > Multi-Query Attention_
Multi-Query Attention changes the multiheaded attention mechanism. Whereas normally,  
MultiheadedAttention ( Q , K , V ) = Concat i ∈ [ # h e a d s ] ( Attention ( X W i Q , X W i K , X W i V ) ) W O {\displaystyle {\text{MultiheadedAttention}}(Q,K,V)={\text{Concat}}_{i\in [\\#heads]}({\text{Attention}}(XW_{i}^{Q},XW_{i}^{K},XW_{i}^{V}))W^{O}}  
with Multi-Query Attention, there is just one  W K , W V {\displaystyle W^{K},W^{V}} , thus:

#### Source: What is a Transformer?. An Introduction to Transformers and… | by Maxime | Inside Machine learning | Medium
URL: https://medium.com/inside-machine-learning/what-is-a-transformer-d07dd1fbec04

_from: Part 2: The Transformer_
The righthand picture describes how this attention-mechanism can be parallelized into multiple mechanisms that can be used side by side. The attention mechanism is repeated multiple times with linear projections of Q, K and V. This allows the system to learn from different representations of Q, K and V, which is beneficial to the model. These linear representations are done by multiplying Q, K and V by weight matrices W that are learned during the training.

After the multi-attention heads in both the encoder and decoder, we have a pointwise feed-forward layer. This little feed-forward network has identical parameters for each position, which can be described as a separate, identical linear transformation of each element from the given sequence.

#### Source: Transformer Architecture (NLP). From an Natural Language Processing… | by Anmol Talwar | Medium
URL: https://medium.com/@anmoltalwar/transformer-architecture-7e72c89c520d

_from: Transformer Architecture (NLP) > Self-attention_
Multi-head attention is an extension of self-attention, where multiple self-attention mechanisms operate in parallel. In multi-head attention, the input sequence is processed by several separate self-attention heads, each with its own learned parameters. These multiple heads allow the model to capture different types of dependencies and relationships in the data. Each head can focus on different aspects of the input, enabling the model’s ability to understand and process complex sequences

#### Source: Demystifying Transformers Architecture in Machine Learning
URL: https://www.projectpro.io/article/transformers-architecture/840

_from: Demystifying Transformers Architecture in Machine Learning > Understanding Transformers Architecture in machine Learning > Key Components Of Transformers Architecture_
Self-Attention Mechanism  
This is the central component of the original Transformer architecture. Each word embeddings in the input word sequence attend to all the other words to compute a weighted representation of the sequence. The self-attention layers capture long-range dependencies between words and are used in both the encoder block and decoder block of the Transformer.  
Multi-Head Attention