#### Source: tmpt43elso2
URL: file:///var/folders/jp/99fbbz9959d892jf52cv2c3h0000gn/T/tmpt43elso2

_from: top level_
4  
output values. These are concatenated and once again projected, resulting in the final values, as depicted in Figure 2.  Multi-head attention allows the model to jointly attend to information from different representation subspaces at different positions. With a single attention head, averaging inhibits this.  
Where the projections are parameter matrices W Q   i   ∈ R d model ×dk , W K   i   ∈ R d model ×dk , W V   i   ∈ R d model ×dv  and W O ∈ R hdv×d model.

#### Source: Transformer (deep learning architecture) - Wikipedia
URL: https://en.wikipedia.org/wiki/Transformer_(machine_learning_model)

_from: Architecture > Scaled dot-product attention > Multi-head attention_
Concretely, let the multiple attention heads be indexed by  i {\displaystyle i} , then we have  
MultiheadedAttention ( Q , K , V ) = Concat i ∈ [ # h e a d s ] ( Attention ( X W i Q , X W i K , X W i V ) ) W O {\displaystyle {\text{MultiheadedAttention}}(Q,K,V)={\text{Concat}}_{i\in [\\#heads]}({\text{Attention}}(XW_{i}^{Q},XW_{i}^{K},XW_{i}^{V}))W^{O}}

_from: Subsequent work > Efficient implementation > Multi-Query Attention_
Multi-Query Attention changes the multiheaded attention mechanism. Whereas normally,  
MultiheadedAttention ( Q , K , V ) = Concat i ∈ [ # h e a d s ] ( Attention ( X W i Q , X W i K , X W i V ) ) W O {\displaystyle {\text{MultiheadedAttention}}(Q,K,V)={\text{Concat}}_{i\in [\\#heads]}({\text{Attention}}(XW_{i}^{Q},XW_{i}^{K},XW_{i}^{V}))W^{O}}  
with Multi-Query Attention, there is just one  W K , W V {\displaystyle W^{K},W^{V}} , thus:

#### Source: What is a Transformer?. An Introduction to Transformers and… | by Maxime | Inside Machine learning | Medium
URL: https://medium.com/inside-machine-learning/what-is-a-transformer-d07dd1fbec04

_from: Part 2: The Transformer_
The righthand picture describes how this attention-mechanism can be parallelized into multiple mechanisms that can be used side by side. The attention mechanism is repeated multiple times with linear projections of Q, K and V. This allows the system to learn from different representations of Q, K and V, which is beneficial to the model. These linear representations are done by multiplying Q, K and V by weight matrices W that are learned during the training.

The reason is that we want to attend on either the whole encoder input sequence or a part of the decoder input sequence. The multi-head attention module that connects the encoder and decoder will make sure that the encoder input-sequence is taken into account together with the decoder input-sequence up to a given position.  
After the multi-attention heads in both the encoder and decoder, we have a pointwise feed-forward layer.

#### Source: Transformer Architecture (NLP). From an Natural Language Processing… | by Anmol Talwar | Medium
URL: https://medium.com/@anmoltalwar/transformer-architecture-7e72c89c520d

_from: Transformer Architecture (NLP) > Self-attention_
Multi-head attention is an extension of self-attention, where multiple self-attention mechanisms operate in parallel. In multi-head attention, the input sequence is processed by several separate self-attention heads, each with its own learned parameters. These multiple heads allow the model to capture different types of dependencies and relationships in the data. Each head can focus on different aspects of the input, enabling the model’s ability to understand and process complex sequences

Benefits and Capabilities:  
* Self-attention allows the model to give more attention to words that are contextually relevant and less attention to irrelevant words, crucial for understanding the context of a word within a sentence.

#### Source: Demystifying Transformers Architecture in Machine Learning
URL: https://www.projectpro.io/article/transformers-architecture/840

_from: Demystifying Transformers Architecture in Machine Learning > Understanding Transformers Architecture in machine Learning > Key Components Of Transformers Architecture_
Self-Attention Mechanism  
This is the central component of the original Transformer architecture. Each word embeddings in the input word sequence attend to all the other words to compute a weighted representation of the sequence. The self-attention layers capture long-range dependencies between words and are used in both the encoder block and decoder block of the Transformer.  
Multi-Head Attention

_from: Demystifying Transformers Architecture in Machine Learning > How Do Transformers Work Using Self-Attention Mechanism?_
Self-attention is a mechanism used in neural networks, particularly in transformer architecture, to compute a weighted sum of a sequence of inputs. The similarity between each input and all other inputs in the sequence determines the weights. Self-attention allows the model to attend to different parts of the input sequence when making predictions and is particularly well-suited for processing sequential data, such as natural language text.  
The self-attention mechanism works as follows.