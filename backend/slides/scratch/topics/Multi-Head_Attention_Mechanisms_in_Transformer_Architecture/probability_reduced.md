#### Source: tmpt43elso2
URL: file:///var/folders/jp/99fbbz9959d892jf52cv2c3h0000gn/T/tmpt43elso2

_from: top level_
Self-attention, sometimes called intra-attention is an attention mechanism relating different positions of a single sequence in order to compute a representation of the sequence. Self-attention has been used successfully in a variety of tasks including reading comprehension, abstractive summarization, textual entailment and learning task-independent sentence representations [4, 27, 28, 22].

The Transformer follows this overall architecture using stacked self-attention and point-wise, fully connected layers for both the encoder and decoder, shown in the left and right halves of Figure 1, respectively.    3.1     Encoder and Decoder Stacks      Encoder:   The encoder is composed of a stack of N = 6 identical layers. Each layer has two sub-layers. The first is a multi-head self-attention mechanism, and the second is a simple, position- wise fully connected feed-forward network.

Decoder:   The decoder is also composed of a stack of N = 6 identical layers. In addition to the two sub-layers in each encoder layer, the decoder inserts a third sub-layer, which performs multi-head attention over the output of the encoder stack. Similar to the encoder, we employ residual connections around each of the sub-layers, followed by layer normalization. We also modify the self-attention sub-layer in the decoder stack to prevent positions from attending to subsequent positions.

This masking, combined with fact that the output embeddings are offset by one position, ensures that the predictions for position i can depend only on the known outputs at positions less than i .

3.2.1     Scaled Dot-Product Attention    We call our particular attention "Scaled Dot-Product Attention" (Figure 2). The input consists of queries and keys of dimension dk , and values of dimension dv . We compute the dot products of the query with all keys, divide each by √dk , and apply a softmax function to obtain the weights on the values.  In practice, we compute the attention function on a set of queries simultaneously, packed together into a matrix Q .

Dot-product attention is identical to our algorithm, except for the scaling factor of 1  √dk . Additive attention computes the compatibility function using a feed-forward network with a single hidden layer. While the two are similar in theoretical complexity, dot-product attention is much faster and more space-efficient in practice, since it can be implemented using highly optimized matrix multiplication code.

While for small values of dk the two mechanisms perform similarly, additive attention outperforms dot product attention without scaling for larger values of dk [3]. We suspect that for large values of  dk , the dot products grow large in magnitude, pushing the softmax function into regions where it has extremely small gradients 4. To counteract this effect, we scale the dot products by 1  √dk .

3.2.2     Multi-Head Attention    Instead of performing a single attention function with d model-dimensional keys, values and queries, we found it beneficial to linearly project the queries, keys and values h times with different, learned linear projections to dk , dk and dv dimensions, respectively.

On each of these projected versions of queries, keys and values we then perform the attention function in parallel, yielding dv -dimensional  
4To illustrate why the dot products get large, assume that the components of q and k are independent random variables with mean 0 and variance 1. Then their dot product, q · k = � dk   i =1 qiki , has mean 0 and variance dk . 4  
output values. These are concatenated and once again projected, resulting in the final values, as depicted in Figure 2.

Multi-head attention allows the model to jointly attend to information from different representation subspaces at different positions. With a single attention head, averaging inhibits this.  
Where the projections are parameter matrices W Q   i   ∈ R d model ×dk , W K   i   ∈ R d model ×dk , W V   i   ∈ R d model ×dv  and W O ∈ R hdv×d model.

This allows every position in the decoder to attend over all positions in the input sequence. This mimics the typical encoder-decoder attention mechanisms in sequence-to-sequence models such as [38, 2, 9].  • The encoder contains self-attention layers. In a self-attention layer all of the keys, values and queries come from the same place, in this case, the output of the previous layer in the encoder. Each position in the encoder can attend to all positions in the previous layer of the encoder.

• Similarly, self-attention layers in the decoder allow each position in the decoder to attend to all positions in the decoder up to and including that position. We need to prevent leftward information flow in the decoder to preserve the auto-regressive property.

We implement this inside of scaled dot-product attention by masking out (setting to −∞ ) all values in the input of the softmax which correspond to illegal connections. See Figure 2.

3.3     Position-wise Feed-Forward Networks    In addition to attention sub-layers, each of the layers in our encoder and decoder contains a fully connected feed-forward network, which is applied to each position separately and identically.

n is the sequence length, d is the representation dimension, k is the kernel size of convolutions and r the size of the neighborhood in restricted self-attention.  Layer Type Complexity per Layer Sequential Maximum Path Length Operations  Self-Attention  O ( n 2 · d )  O (1)  O (1) Recurrent  O ( n · d 2)  O ( n )  O ( n ) Convolutional  O ( k · n · d 2)  O (1)  O ( logk ( n )) Self-Attention (restricted)  O ( r · n · d )  O (1)  O ( n/r )

The shorter these paths between any combination of positions in the input and output sequences, the easier it is to learn long-range dependencies [12]. Hence we also compare the maximum path length between any two input and output positions in networks composed of the different layer types.  As noted in Table 1, a self-attention layer connects all positions with a constant number of sequentially executed operations, whereas a recurrent layer requires O ( n ) sequential operations.

In terms of computational complexity, self-attention layers are faster than recurrent layers when the sequence

To improve computational performance for tasks involving very long sequences, self-attention could be restricted to considering only a neighborhood of size r in the input sequence centered around the respective output position. This would increase the maximum path length to O ( n/r ). We plan to investigate this approach further in future work.  A single convolutional layer with kernel width k < n does not connect all pairs of input and output positions.

Doing so requires a stack of O ( n/k ) convolutional layers in the case of contiguous kernels, or O ( logk ( n )) in the case of dilated convolutions [18], increasing the length of the longest paths between any two positions in the network.