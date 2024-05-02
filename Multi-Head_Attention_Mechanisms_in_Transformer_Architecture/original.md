#### Source: tmpt43elso2
URL: file:///var/folders/jp/99fbbz9959d892jf52cv2c3h0000gn/T/tmpt43elso2

_from: top level_
In these models, the number of operations required to relate signals from two arbitrary input or output positions grows in the distance between positions, linearly for ConvS2S and logarithmically for ByteNet. This makes it more difficult to learn dependencies between distant positions [12].

Self-attention, sometimes called intra-attention is an attention mechanism relating different positions of a single sequence in order to compute a representation of the sequence. Self-attention has been used successfully in a variety of tasks including reading comprehension, abstractive summarization, textual entailment and learning task-independent sentence representations [4, 27, 28, 22].

The Transformer follows this overall architecture using stacked self-attention and point-wise, fully connected layers for both the encoder and decoder, shown in the left and right halves of Figure 1, respectively.    3.1     Encoder and Decoder Stacks      Encoder:   The encoder is composed of a stack of N = 6 identical layers. Each layer has two sub-layers. The first is a multi-head self-attention mechanism, and the second is a simple, position- wise fully connected feed-forward network.

We employ a residual connection [11] around each of the two sub-layers, followed by layer normalization [1]. That is, the output of each sub-layer is LayerNorm( x + Sublayer( x )), where Sublayer( x ) is the function implemented by the sub-layer itself.

To facilitate these residual connections, all sub-layers in the model, as well as the embedding layers, produce outputs of dimension d model = 512.    Decoder:   The decoder is also composed of a stack of N = 6 identical layers.

In addition to the two sub-layers in each encoder layer, the decoder inserts a third sub-layer, which performs multi-head attention over the output of the encoder stack. Similar to the encoder, we employ residual connections around each of the sub-layers, followed by layer normalization. We also modify the self-attention sub-layer in the decoder stack to prevent positions from attending to subsequent positions.

This masking, combined with fact that the output embeddings are offset by one position, ensures that the predictions for position i can depend only on the known outputs at positions less than i .

The output is computed as a weighted sum  3  
Figure 2: (left) Scaled Dot-Product Attention. (right) Multi-Head Attention consists of several attention layers running in parallel.  of the values, where the weight assigned to each value is computed by a compatibility function of the query with the corresponding key.    3.2.1     Scaled Dot-Product Attention    We call our particular attention "Scaled Dot-Product Attention" (Figure 2).

The input consists of queries and keys of dimension dk , and values of dimension dv . We compute the dot products of the query with all keys, divide each by √dk , and apply a softmax function to obtain the weights on the values.  In practice, we compute the attention function on a set of queries simultaneously, packed together into a matrix Q .

The keys and values are also packed together into matrices K and V . We compute the matrix of outputs as:  
Attention( Q, K, V ) = softmax( QKT   √dk  ) V  (1)  The two most commonly used attention functions are additive attention [2], and dot-product (multi- plicative) attention. Dot-product attention is identical to our algorithm, except for the scaling factor of 1  √dk .

Additive attention computes the compatibility function using a feed-forward network with a single hidden layer. While the two are similar in theoretical complexity, dot-product attention is much faster and more space-efficient in practice, since it can be implemented using highly optimized matrix multiplication code.

While for small values of dk the two mechanisms perform similarly, additive attention outperforms dot product attention without scaling for larger values of dk [3]. We suspect that for large values of  dk , the dot products grow large in magnitude, pushing the softmax function into regions where it has extremely small gradients 4. To counteract this effect, we scale the dot products by 1  √dk .

3.2.2     Multi-Head Attention    Instead of performing a single attention function with d model-dimensional keys, values and queries, we found it beneficial to linearly project the queries, keys and values h times with different, learned linear projections to dk , dk and dv dimensions, respectively.

On each of these projected versions of queries, keys and values we then perform the attention function in parallel, yielding dv -dimensional  
4To illustrate why the dot products get large, assume that the components of q and k are independent random variables with mean 0 and variance 1. Then their dot product, q · k = � dk   i =1 qiki , has mean 0 and variance dk . 4  
output values. These are concatenated and once again projected, resulting in the final values, as depicted in Figure 2.

Multi-head attention allows the model to jointly attend to information from different representation subspaces at different positions. With a single attention head, averaging inhibits this.  
Where the projections are parameter matrices W Q   i   ∈ R d model ×dk , W K   i   ∈ R d model ×dk , W V   i   ∈ R d model ×dv  and W O ∈ R hdv×d model.

In this work we employ h = 8 parallel attention layers, or heads. For each of these we use  dk = dv = d model /h = 64. Due to the reduced dimension of each head, the total computational cost is similar to that of single-head attention with full dimensionality.

This allows every position in the decoder to attend over all positions in the input sequence. This mimics the typical encoder-decoder attention mechanisms in sequence-to-sequence models such as [38, 2, 9].  • The encoder contains self-attention layers. In a self-attention layer all of the keys, values and queries come from the same place, in this case, the output of the previous layer in the encoder. Each position in the encoder can attend to all positions in the previous layer of the encoder.

• Similarly, self-attention layers in the decoder allow each position in the decoder to attend to all positions in the decoder up to and including that position. We need to prevent leftward information flow in the decoder to preserve the auto-regressive property.

We implement this inside of scaled dot-product attention by masking out (setting to −∞ ) all values in the input of the softmax which correspond to illegal connections. See Figure 2.

3.3     Position-wise Feed-Forward Networks    In addition to attention sub-layers, each of the layers in our encoder and decoder contains a fully connected feed-forward network, which is applied to each position separately and identically.

In our model, we share the same weight matrix between the two embedding layers and the pre-softmax linear transformation, similar to [30]. In the embedding layers, we multiply those weights by √d model.  
Table 1: Maximum path lengths, per-layer complexity and minimum number of sequential operations for different layer types. n is the sequence length, d is the representation dimension, k is the kernel size of convolutions and r the size of the neighborhood in restricted self-attention.

Layer Type Complexity per Layer Sequential Maximum Path Length Operations  Self-Attention  O ( n 2 · d )  O (1)  O (1) Recurrent  O ( n · d 2)  O ( n )  O ( n ) Convolutional  O ( k · n · d 2)  O (1)  O ( logk ( n )) Self-Attention (restricted)  O ( r · n · d )  O (1)  O ( n/r )

Motivating our use of self-attention we consider three desiderata.  One is the total computational complexity per layer. Another is the amount of computation that can be parallelized, as measured by the minimum number of sequential operations required.  The third is the path length between long-range dependencies in the network. Learning long-range dependencies is a key challenge in many sequence transduction tasks.

One key factor affecting the ability to learn such dependencies is the length of the paths forward and backward signals have to traverse in the network. The shorter these paths between any combination of positions in the input and output sequences, the easier it is to learn long-range dependencies [12].

Hence we also compare the maximum path length between any two input and output positions in networks composed of the different layer types.  As noted in Table 1, a self-attention layer connects all positions with a constant number of sequentially executed operations, whereas a recurrent layer requires O ( n ) sequential operations.

In terms of computational complexity, self-attention layers are faster than recurrent layers when the sequence

length n is smaller than the representation dimensionality d , which is most often the case with sentence representations used by state-of-the-art models in machine translations, such as word-piece [38] and byte-pair [31] representations.

To improve computational performance for tasks involving very long sequences, self-attention could be restricted to considering only a neighborhood of size r in the input sequence centered around the respective output position. This would increase the maximum path length to O ( n/r ). We plan to investigate this approach further in future work.  A single convolutional layer with kernel width k < n does not connect all pairs of input and output positions.

Doing so requires a stack of O ( n/k ) convolutional layers in the case of contiguous kernels, or O ( logk ( n )) in the case of dilated convolutions [18], increasing the length of the longest paths between any two positions in the network.

Convolutional layers are generally more expensive than recurrent layers, by a factor of k . Separable convolutions [6], however, decrease the complexity considerably, to O ( k · n · d + n · d 2). Even with k = n , however, the complexity of a separable convolution is equal to the combination of a self-attention layer and a point-wise feed-forward layer, the approach we take in our model.  
As side benefit, self-attention could yield more interpretable models.

We inspect attention distributions from our models and present and discuss examples in the appendix. Not only do individual attention heads clearly learn to perform different tasks, many appear to exhibit behavior related to the syntactic and semantic structure of the sentences.    5     Training    This section describes the training regime for our models.

#### Source: Transformers In NLP | State-Of-The-Art-Models
URL: https://www.analyticsvidhya.com/blog/2019/06/understanding-transformers-nlp-state-of-the-art-models/

_from: top level_
The Encoder block has 1 layer of a Multi-Head Attention followed by another layer of Feed Forward Neural Network. The decoder, on the other hand, has an extra Masked Multi-Head Attention.  
The encoder and decoder blocks are actually multiple identical encoders and decoders stacked on top of each other. Both the encoder stack and the decoder stack have the same number of units.  
The number of encoder and decoder units is a hyperparameter. In the paper, 6 encoders and decoders have been used.

Let’s see how this setup of the encoder and the decoder stack works:  
An important thing to note here – in addition to the self-attention and feed-forward layers, the decoders also have one more layer of Encoder-Decoder Attention layer.

Excellent question! This is arguably the most crucial component in the entire setup so let’s understand this concept.  
According to the paper:  
“Self-attention, sometimes called intra-attention, is an attention mechanism relating different positions of a single sequence in order to compute a representation of the sequence.”  
Take a look at the above image. Can you figure out what the term “it” in this sentence refers to?  
Is it referring to the street or to the animal?

It’s a simple question for us but not for an algorithm. When the model is processing the word “it”, self-attention tries to associate “it” with “animal” in the same sentence.  
Self-attention allows the model to look at the other words in the input sequence to get a better understanding of a certain word in the sequence.

Now, let’s see how we can calculate self-attention.  
I have divided this section into various steps for ease of understanding.  
First, we need to create three vectors from each of the encoder’s input vectors:  
These vectors are trained and updated during the training process. We’ll know more about their roles once we are done with this section

Next, we will calculate self-attention for every word in the input sequence  
Consider this phrase – “Action gets results”. To calculate the self-attention for the first word “Action”, we will calculate scores for all the words in the phrase with respect to “Action”.

This score determines the importance of other words when we are encoding a certain word in an input sequence  
1\. The score for the first word is calculated by taking the dot product of the Query vector (q1) with the keys vectors (k1, k2, k3) of all the words:  
2\.

4\. These normalized scores are then multiplied by the value vectors (v1, v2, v3) and sum up the resultant vectors to arrive at the final vector (z1). This is the output of the self-attention layer. It is then passed on to the feed-forward network as input.  
So, z1 is the self-attention vector for the first word of the input sequence “Action gets results”. We can get the vectors for the rest of the words in the input sequence in the same fashion:

Self-attention is computed not once but multiple times in the Transformer’s architecture, in parallel and independently. It is therefore referred to as Multi-head Attention. The outputs are concatenated and linearly transformed as shown in the figure below:

#### Source: Transformer (deep learning architecture) - Wikipedia
URL: https://en.wikipedia.org/wiki/Transformer_(machine_learning_model)

_from: Architecture > Encoder-decoder architecture_
The function of each encoder layer is to generate contextualized token representations, where each representation corresponds to a token that "mixes" information from other input tokens via self-attention mechanism.

Each decoder layer contains two attention sublayers: (1) cross-attention for incorporating the output of encoder (contextualized input token representations), and (2) self-attention for "mixing" information among the input tokens to the decoder (i.e., the tokens generated so far during inference time).  
Both the encoder and decoder layers have a feed-forward neural network for additional processing of the outputs and contain residual connections and layer normalization steps.

_from: Architecture > Scaled dot-product attention_
For each token  i {\displaystyle i} , the input token representation  x i {\displaystyle x_{i}} is multiplied with each of the three weight matrices to produce a query vector  q i = x i W Q {\displaystyle q_{i}=x_{i}W_{Q}} , a key vector  k i = x i W K {\displaystyle k_{i}=x_{i}W_{K}} , and a value vector  v i = x i W V {\displaystyle v_{i}=x_{i}W_{V}} .

Attention weights are calculated using the query and key vectors: the attention weight  a i j {\displaystyle a_{ij}} from token  i {\displaystyle i} to token  j {\displaystyle j} is the dot product between  q i {\displaystyle q_{i}} and  k j {\displaystyle k_{j}} . The attention weights are divided by the square root of the dimension of the key vectors,  d k {\displaystyle {\sqrt {d_{k}}}} , which stabilizes gradients during training, and passed through a softmax which normalizes the weights.

The fact that  W Q {\displaystyle W_{Q}} and  W K {\displaystyle W_{K}} are different matrices allows attention to be non-symmetric: if token  i {\displaystyle i} attends to token  j {\displaystyle j} (i.e.  q i ⋅ k j {\displaystyle q_{i}\cdot k_{j}} is large), this does not necessarily mean that token  j {\displaystyle j} will attend to token  i {\displaystyle i} (i.e.  q j ⋅ k i {\displaystyle q_{j}\cdot k_{i}} could be small).

The output of the attention unit for token  i {\displaystyle i} is the weighted sum of the value vectors of all tokens, weighted by  a i j {\displaystyle a_{ij}} , the attention from token  i {\displaystyle i} to each token.

The attention calculation for all tokens can be expressed as one large matrix calculation using the softmax function, which is useful for training due to computational matrix operation optimizations that quickly compute matrix operations.

The matrices  Q {\displaystyle Q} ,  K {\displaystyle K} and  V {\displaystyle V} are defined as the matrices where the  i {\displaystyle i} th rows are vectors  q i {\displaystyle q_{i}} ,  k i {\displaystyle k_{i}} , and  v i {\displaystyle v_{i}} respectively. Then we can represent the attention as

Attention ( Q , K , V ) = softmax ( Q K T d k ) V {\displaystyle {\begin{aligned}{\text{Attention}}(Q,K,V)={\text{softmax}}\left({\frac {QK^{\mathrm {T} }}{\sqrt {d_{k}}}}\right)V\end{aligned}}}  
where softmax is taken over the horizontal axis.

_from: Architecture > Scaled dot-product attention > Multi-head attention_
The computations for each attention head can be performed in parallel, which allows for fast processing. The outputs for the attention layer are concatenated to pass into the feed-forward neural network layers.  
Concretely, let the multiple attention heads be indexed by  i {\displaystyle i} , then we have

MultiheadedAttention ( Q , K , V ) = Concat i ∈ [ # h e a d s ] ( Attention ( X W i Q , X W i K , X W i V ) ) W O {\displaystyle {\text{MultiheadedAttention}}(Q,K,V)={\text{Concat}}_{i\in [\\#heads]}({\text{Attention}}(XW_{i}^{Q},XW_{i}^{K},XW_{i}^{V}))W^{O}}

where the matrix  X {\displaystyle X} is the concatenation of word embeddings, and the matrices  W i Q , W i K , W i V {\displaystyle W_{i}^{Q},W_{i}^{K},W_{i}^{V}} are "projection matrices" owned by individual attention head  i {\displaystyle i} , and  W O {\displaystyle W^{O}} is a final projection matrix owned by the whole multi-headed attention head.

_from: Architecture > Scaled dot-product attention > Masked attention_
It may be necessary to cut out attention links between some word-pairs. For example, the decoder for token position  t {\displaystyle t} should not have access to token position  t + 1 {\displaystyle t+1} . This may be accomplished before the softmax stage by adding a mask matrix  M {\displaystyle M} that is  − ∞ {\displaystyle -\infty } at entries where the attention link must be cut, and  0 {\displaystyle 0} at other places:

For example, the following mask matrix is used in autoregressive modeling:  
M = [ 0 − ∞ − ∞ … − ∞ 0 0 − ∞ … − ∞ 0 0 0 … − ∞ ⋮ ⋮ ⋮ ⋱ ⋮ 0 0 0 … 0 ] {\displaystyle M={\begin{bmatrix}0&-\infty &-\infty &\dots &-\infty \\\0&0&-\infty &\dots &-\infty \\\0&0&0&\dots &-\infty \\\\\vdots &\vdots &\vdots &\ddots &\vdots \\\0&0&0&\dots &0\end{bmatrix}}}  
In words, it means that each token can pay attention to itself, and every token before it, but not any after it.

_from: Architecture > Encoder_
Each encoder consists of two major components: a self-attention mechanism and a feed-forward neural network. The self-attention mechanism accepts input encodings from the previous encoder and weights their relevance to each other to generate output encodings. The feed-forward neural network further processes each output encoding individually. These output encodings are then passed to the next encoder as its input, as well as to the decoders.

_from: Architecture > Encoder > Positional encoding_
for any constants  c j {\displaystyle c_{j}} . This allows the transformer to take any encoded position and find a linear sum of the encoded locations of its neighbors. This sum of encoded positions, when fed into the attention mechanism, would create attention weights on its neighbors, much like what happens in a convolutional neural network language model. In the author's words, "we hypothesized it would allow the model to easily learn to attend by relative position."

In typical implementations, all operations are done over the real numbers, not the complex numbers, but since complex multiplication can be implemented as real 2-by-2 matrix multiplication, this is a mere notational difference.

_from: Architecture > Decoder_
Each decoder consists of three major components: a self-attention mechanism, an attention mechanism over the encodings, and a feed-forward neural network. The decoder functions in a similar fashion to the encoder, but an additional attention mechanism is inserted which instead draws relevant information from the encodings generated by the encoders. This mechanism can also be called the _encoder-decoder attention_.

_from: Subsequent work > Alternative positional encodings > ALiBi_
ALiBi (Attention with Linear Biases) is not a _replacement_ for the positional encoder on the original transformer. Instead, it is an _additional_ positional encoder that is directly plugged into the attention mechanism. Specifically, the ALiBi attention mechanism is  
Attention ( Q , K , V ) = softmax ( Q K T d k + s B ) V {\displaystyle {\begin{aligned}{\text{Attention}}(Q,K,V)={\text{softmax}}\left({\frac {QK^{\mathrm {T} }}{\sqrt {d_{k}}}}+sB\right)V\end{aligned}}}

Here,  s {\displaystyle s} is a real number ("scalar"), and  B {\displaystyle B} is the _linear bias_ matrix defined by  
B = ( 0 1 2 3 ⋯ − 1 0 1 2 ⋯ − 2 − 1 0 1 ⋯ − 3 − 2 − 1 0 ⋯ ⋮ ⋮ ⋮ ⋮ ⋱ ) {\displaystyle B={\begin{pmatrix}0&1&2&3&\cdots \\\\-1&0&1&2&\cdots \\\\-2&-1&0&1&\cdots \\\\-3&-2&-1&0&\cdots \\\\\vdots &\vdots &\vdots &\vdots &\ddots \\\\\end{pmatrix}}}  
in other words,  B i , j = j − i {\displaystyle B_{i,j}=j-i} .

ALiBi allows pretraining on short context windows, then finetuning on longer context windows. Since it is directly plugged into the attention mechanism, it can be combined with any positional encoder that is plugged into the "bottom" of the entire network (which is where the sinusoidal encoder on the original transformer, as well as RoPE and many others, are located).

_from: Subsequent work > Alternative positional encodings > Relative Position Encodings_
Relative Position Encodings is similar to ALiBi, but more generic:  
Attention ( Q , K , V ) = softmax ( Q K T d k + B ) V {\displaystyle {\begin{aligned}{\text{Attention}}(Q,K,V)={\text{softmax}}\left({\frac {QK^{\mathrm {T} }}{\sqrt {d_{k}}}}+B\right)V\end{aligned}}}  
where  B {\displaystyle B} is a Toeplitz matrix, that is,  B i , j = B i ′ , j ′ {\displaystyle B_{i,j}=B_{i',j'}} whenever  i − j = i ′ − j ′ {\displaystyle i-j=i'-j'} .

_from: Subsequent work > Efficient implementation > Multi-Query Attention_
Multi-Query Attention changes the multiheaded attention mechanism. Whereas normally,  
MultiheadedAttention ( Q , K , V ) = Concat i ∈ [ # h e a d s ] ( Attention ( X W i Q , X W i K , X W i V ) ) W O {\displaystyle {\text{MultiheadedAttention}}(Q,K,V)={\text{Concat}}_{i\in [\\#heads]}({\text{Attention}}(XW_{i}^{Q},XW_{i}^{K},XW_{i}^{V}))W^{O}}  
with Multi-Query Attention, there is just one  W K , W V {\displaystyle W^{K},W^{V}} , thus:

MultiQueryAttention ( Q , K , V ) = Concat i ∈ [ # h e a d s ] ( Attention ( X W i Q , X W K , X W V ) ) W O {\displaystyle {\text{MultiQueryAttention}}(Q,K,V)={\text{Concat}}_{i\in [\\#heads]}({\text{Attention}}(XW_{i}^{Q},XW^{K},XW^{V}))W^{O}}  
This has a neutral effect on model quality and training speed, but increases inference speed.

_from: Subsequent work > Sub-quadratic transformers_
where  w 1 , . . . , w D {\displaystyle w_{1},...,w_{D}} are independent samples from the normal distribution  N ( 0 , σ 2 I ) {\displaystyle N(0,\sigma ^{2}I)} . This choice of parameters satisfy  E [ ⟨ φ ( x ) , φ ( y ) ⟩ ] = e ‖ x − y ‖ 2 2 σ 2 {\displaystyle \mathbb {E} [\langle \varphi (x),\varphi (y)\rangle ]=e^{\frac {\|x-y\|^{2}}{2\sigma ^{2}}}} , or

e ⟨ x , y ⟩ / σ 2 = E [ ⟨ e ‖ x ‖ 2 / 2 σ 2 φ ( x ) , e ‖ y ‖ 2 / 2 σ 2 φ ( y ) ⟩ ] ≈ ⟨ e ‖ x ‖ 2 / 2 σ 2 φ ( x ) , e ‖ y ‖ 2 / 2 σ 2 φ ( y ) ⟩ {\displaystyle e^{\langle x,y\rangle /\sigma ^{2}}=\mathbb {E} [\langle e^{\|x\|^{2}/2\sigma ^{2}}\varphi (x),e^{\|y\|^{2}/2\sigma ^{2}}\varphi (y)\rangle ]\approx \langle e^{\|x\|^{2}/2\sigma ^{2}}\varphi (x),e^{\|y\|^{2}/2\sigma ^{2}}\varphi (y)\rangle }  
Consequently, the one-headed attention, with one query, can be written as

Attention ( q , K , V ) = softmax ( q K T d k ) V ≈ φ ( q ) T ∑ i e ‖ k i ‖ 2 / 2 σ 2 φ ( k i ) v i T φ ( q ) T ∑ i e ‖ k i ‖ 2 / 2 σ 2 φ ( k i ) {\displaystyle {\text{Attention}}(q,K,V)={\text{softmax}}\left({\frac {qK^{\mathrm {T} }}{\sqrt {d_{k}}}}\right)V\approx {\frac {\varphi (q)^{T}\sum _{i}e^{\|k_{i}\|^{2}/2\sigma ^{2}}\varphi (k_{i})v_{i}^{T}}{\varphi (q)^{T}\sum _{i}e^{\|k_{i}\|^{2}/2\sigma ^{2}}\varphi (k_{i})}}}  
where  σ = d K 1 / 4 {\displaystyle \sigma =d_{K}^{1/4}} .

Similarly for multiple queries, and for multiheaded attention.  
This approximation can be computed in linear time, as we can compute the matrix  φ ( k i ) v i T {\displaystyle \varphi (k_{i})v_{i}^{T}} first, then multiply it with the query. In essence, we have managed to obtain a more precise version of

Attention ( Q , K , V ) = softmax ( Q K T d k ) V ≈ Q ( K T V / d k ) {\displaystyle {\text{Attention}}(Q,K,V)={\text{softmax}}\left({\frac {QK^{\mathrm {T} }}{\sqrt {d_{k}}}}\right)V\approx Q(K^{T}V/{\sqrt {d_{k}}})}  
Performer (2022) uses the same Random Feature Attention, but  w 1 , . . .

, w D {\displaystyle w_{1},...,w_{D}} are first independently sampled from the normal distribution  N ( 0 , σ 2 I ) {\displaystyle N(0,\sigma ^{2}I)} , then they are Gram-Schmidt processed.

#### Source: What is a Transformer?. An Introduction to Transformers and… | by Maxime | Inside Machine learning | Medium
URL: https://medium.com/inside-machine-learning/what-is-a-transformer-d07dd1fbec04

_from: Part 1: Sequence to Sequence Learning and Attention_
The attention-mechanism looks at an input sequence and decides at each step which other parts of the sequence are important. It sounds abstract, but let me clarify with an easy example: When reading this text, you always focus on the word you read but at the same time your mind still holds the important keywords of the text in memory in order to provide context.  
An attention-mechanism works similarly for a given sequence.

_from: Part 2: The Transformer_
Both Encoder and Decoder are composed of modules that can be stacked on top of each other multiple times, which is described by Nx in the figure. We see that the modules consist mainly of Multi-Head Attention and Feed Forward layers. The inputs and outputs (target sentences) are first embedded into an n-dimensional space since we cannot use strings directly.  
One slight but important part of the model is the positional encoding of the different words.

Let’s start with the left description of the attention-mechanism. It’s not very complicated and can be described by the following equation:  
Q is a matrix that contains the query (vector representation of one word in the sequence), K are all the keys (vector representations of all the words in the sequence) and V are the values, which are again the vector representations of all the words in the sequence.

For the encoder and decoder, multi-head attention modules, V consists of the same word sequence than Q. However, for the attention module that is taking into account the encoder and the decoder sequences, V is different from the sequence represented by Q.  
To simplify this a little bit, we could say that the values in V are multiplied and summed with some attention-weights a, where our weights are defined by:

This means that the weights a are defined by how each word of the sequence (represented by Q) is influenced by all the other words in the sequence (represented by K). Additionally, the SoftMax function is applied to the weights a to have a distribution between 0 and 1.

Those weights are then applied to all the words in the sequence that are introduced in V (same vectors than Q for encoder and decoder but different for the module that has encoder and decoder inputs).  
The righthand picture describes how this attention-mechanism can be parallelized into multiple mechanisms that can be used side by side.

The attention mechanism is repeated multiple times with linear projections of Q, K and V. This allows the system to learn from different representations of Q, K and V, which is beneficial to the model. These linear representations are done by multiplying Q, K and V by weight matrices W that are learned during the training.

Those matrices Q, K and V are different for each position of the attention modules in the structure depending on whether they are in the encoder, decoder or in-between encoder and decoder. The reason is that we want to attend on either the whole encoder input sequence or a part of the decoder input sequence.

The multi-head attention module that connects the encoder and decoder will make sure that the encoder input-sequence is taken into account together with the decoder input-sequence up to a given position.  
After the multi-attention heads in both the encoder and decoder, we have a pointwise feed-forward layer.

This little feed-forward network has identical parameters for each position, which can be described as a separate, identical linear transformation of each element from the given sequence.

#### Source: How do Transformers work? - Hugging Face NLP Course
URL: https://huggingface.co/learn/nlp-course/chapter1/4

_from: How do Transformers work? > Introduction_
The model is primarily composed of two blocks:  
* **Encoder (left)** : The encoder receives an input and builds a representation of it (its features). This means that the model is optimized to acquire understanding from the input.
* **Decoder (right)** : The decoder uses the encoder’s representation (features) along with other inputs to generate a target sequence. This means that the model is optimized for generating outputs.

Each of these parts can be used independently, depending on the task:  
* **Encoder-only models** : Good for tasks that require understanding of the input, such as sentence classification and named entity recognition.
* **Decoder-only models** : Good for generative tasks such as text generation.

* **Encoder-decoder models** or **sequence-to-sequence models** : Good for generative tasks that require an input, such as translation or summarization.  
We will dive into those architectures independently in later sections.

_from: How do Transformers work? > The original architecture_
The _attention mask_ can also be used in the encoder/decoder to prevent the model from paying attention to some special words — for instance, the special padding word used to make all the inputs the same length when batching together sentences.

#### Source: Transformer Architecture (NLP). From an Natural Language Processing… | by Anmol Talwar | Medium
URL: https://medium.com/@anmoltalwar/transformer-architecture-7e72c89c520d

_from: Transformer Architecture (NLP)_
Transformer model is based on an encoder-decoder architecture. Both the encoder and decoder consist of sub-layers, described below:

_from: Transformer Architecture (NLP) > Self-attention_
In simpler terms, self attention helps us create similar connections within the same sentence. Look at the following example:  
`"She found her lost keys in the kitchen, and it made her day."
it => finding keys
"She found her lost keys in the kitchen, and it was a mess."
it=> kitchen`  
By changing the emotion from “made her day” → “was a mess” the reference object for “it” changed.  
Mechanism:

Self-attention is like a spotlight that moves across each word, focusing on its neighboring words to figure out how important they are.

Attention weights are generated during self-attention and can be visualized as “attention maps.” These maps show how much attention each word pays to every other word in the sequence, providing insights into what the model is focusing on when processing a given word.

Multi-head attention is an extension of self-attention, where multiple self-attention mechanisms operate in parallel. In multi-head attention, the input sequence is processed by several separate self-attention heads, each with its own learned parameters. These multiple heads allow the model to capture different types of dependencies and relationships in the data. Each head can focus on different aspects of the input, enabling the model’s ability to understand and process complex sequences

Benefits and Capabilities:  
* Self-attention allows the model to give more attention to words that are contextually relevant and less attention to irrelevant words, crucial for understanding the context of a word within a sentence.

_from: Transformer Architecture (NLP) > Feed-Forward Neural Network_
These layers further process the outputs of the self-attention layer before passing them on to the next encoder or decoder. They help the model capture different levels of abstraction, non — linear interactions between words in the sequence and complex dependencies within the data.

#### Source: Demystifying Transformers Architecture in Machine Learning
URL: https://www.projectpro.io/article/transformers-architecture/840

_from: Demystifying Transformers Architecture in Machine Learning > Understanding Transformers Architecture in machine Learning > Key Components Of Transformers Architecture_
Self-Attention Mechanism  
This is the central component of the original Transformer architecture. Each word embeddings in the input word sequence attend to all the other words to compute a weighted representation of the sequence. The self-attention layers capture long-range dependencies between words and are used in both the encoder block and decoder block of the Transformer.  
Multi-Head Attention

It works by splitting the query, key, and value vectors into multiple smaller vectors, or "heads," and applying the key feature of the self-attention mechanism to each head separately. This allows the network to capture multiple perspectives on the input sequence and improves the model's ability to capture different types of relationships between words in the input sequence.  
Feed-Forward Neural Network

The feed-forward neural network processes the output sequence length out of the attention vectors and generates the final output sequence. It typically comprises multiple layers of fully connected layers with ReLU activation functions. This component lets the network capture non-linear relationships between words in the input sequence.  
Positional Encoding

_from: Demystifying Transformers Architecture in Machine Learning > Understanding Transformers Architecture in machine Learning > Key Components Of Transformers Architecture > Here's what valued users are saying about ProjectPro_
Residual connection adds the input to the output of each sub-layer, and layer normalization is used to normalize the inputs to each sub-layer.  
Encoder-Decoder Structure  
The encoder-decoder structure is one of the building blocks used in sequence-to-sequence tasks, such as language translation.

The encoder model processes the input sequence using the self-attention layer and position-wise feed-forward network components to create a fixed-length representation of the input sequence, the encoder's output.

_from: Demystifying Transformers Architecture in Machine Learning > How Do Transformers Work Using Self-Attention Mechanism?_
Self-attention is a mechanism used in neural networks, particularly in transformer architecture, to compute a weighted sum of a sequence of inputs. The similarity between each input and all other inputs in the sequence determines the weights. Self-attention allows the model to attend to different parts of the input sequence when making predictions and is particularly well-suited for processing sequential data, such as natural language text.  
The self-attention mechanism works as follows.

Given a sequence of inputs:  
The self-attention mechanism computes a set of key, query, and value vectors for each input. The key and value vectors are used to determine a weighted sum of the value vectors, where the similarity between the query vector and the key vectors determines the weights. The resulting sum is then passed through a feed-forward layer to produce the output for that input.

Given a sequence of input vectors:  
We first compute a set of key, query, and value matrices K, Q, and V, respectively, by multiplying X by learnable weight matrices W_k, W_q, and W_v:  
Next, we compute the attention weights A between each pair of query and key vectors using the dot product between the key and query vectors, scaled by the square root of the dimensionality of the query and key vectors:  
Where d_k is the dimensionality of the key vectors.