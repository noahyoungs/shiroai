from dotenv import load_dotenv
import os
import sys
import matplotlib.pyplot as plt
import seaborn as sns

load_dotenv()
# set the python path
sys.path.append(os.getenv('PYTHON_PATH'))

from s3 import download_model_list_from_s3
from langchain.docstore.document import Document
from format import format_topic
from langchain_openai import OpenAIEmbeddings
from portkey_ai import PORTKEY_GATEWAY_URL, createHeaders, AsyncPortkey
import numpy as np
import pandas as pd
import cohere  
from tqdm import tqdm
from portkey_ai import Portkey

def to_single_string(documents):
    if type(documents[0]) == dict:
        return "\n\n".join([doc['page_content'] for doc in documents])
    else:
        return "\n\n".join([
            doc.page_content 
            for doc in documents
        ]).strip()
        
def save_markdown_file(topic_docs, filename):    
    markdown = format_topic(topic_docs)
    with open(filename, 'w') as f:
        f.write(markdown)
        
def reduce_docs_to_length(docs, key, length, remove_highest_first=False):
    if type(docs[0]) == dict:
        doc_dicts = docs
    else:
        doc_dicts = [doc.to_dict() for doc in docs]

    def get_nested_value(doc_dict, key_path):
        value = doc_dict
        for key in key_path:
            if isinstance(value, dict):
                value = value.get(key)
            else:
                return None
        return value

    doc_dict_pairs = [(i, doc_dict, get_nested_value(doc_dict, key)) for i, doc_dict in enumerate(doc_dicts)]
    
    # Filter out documents with None as the key value
    doc_dict_pairs = [pair for pair in doc_dict_pairs if pair[2] is not None]
    
    # Sort the document-key pairs based on the key value
    if not remove_highest_first:
        doc_dict_pairs.sort(key=lambda x: x[2], reverse=True)
    else:
        doc_dict_pairs.sort(key=lambda x: x[2])

    reduced_docs = []
    current_length = 0

    for i, doc_dict, _ in doc_dict_pairs:
        doc_length = len(doc_dict.get('page_content', ''))
        if current_length + doc_length <= length:
            reduced_docs.append(doc_dict)
            current_length += doc_length

    # Sort the reduced_docs list based on the original order of docs
    reduced_docs.sort(key=lambda doc: docs.index(doc))
    
    return reduced_docs

async def reduce_docs(reduce_length_1, reduce_length_2, topic):
    
    # Get chunked and labeled documents from S3 for whole presentation
    all_docs = await download_model_list_from_s3(Document, f"{topic['presentation_id']}/all_sources_chunked_docs_with_topics.json")

    # Get topic docs
    topic_docs = [doc for doc in all_docs if 'topic' in doc.metadata and doc.metadata['topic']['name'] == topic['name']]
    topic_docs = [dict(doc) for doc in topic_docs]

    print(f"Original character length of topic docs: {len(to_single_string(topic_docs))}")
    print(f"Original number of topic docs: {len(topic_docs)}")
    print(f"Original number of sources: {len(set(doc['metadata']['source']['id'] for doc in topic_docs))}")

    folder = topic['name'].replace(' ', '_')
    if not os.path.exists(folder):
        os.makedirs(folder)
    save_markdown_file(topic_docs, f"{folder}/original.md")

    original_length = len(to_single_string(topic_docs))

    # vectorize
    portkeyHeaders = createHeaders(
        provider="openai",
        api_key=os.getenv("PORTKEY_API_KEY"),
    )
    openai_embeddings = OpenAIEmbeddings(model="text-embedding-3-small", dimensions=512, base_url=PORTKEY_GATEWAY_URL, default_headers=portkeyHeaders)
    vectors = await openai_embeddings.aembed_documents([doc['page_content'] for doc in topic_docs])
    doc_embeddings = np.array(vectors)

    query_embedding = await openai_embeddings.aembed_query(topic['name'])

    # try 3 different metrics
    cosine_similarities = np.dot(doc_embeddings, query_embedding) / (np.linalg.norm(doc_embeddings, axis=1) * np.linalg.norm(query_embedding))
    euclidean_distances = np.linalg.norm(doc_embeddings - query_embedding, axis=1)
    dot_products = np.dot(doc_embeddings, query_embedding)

    # add the metrics and the embeddings
    assert len(topic_docs) == len(doc_embeddings) == len(cosine_similarities) == len(euclidean_distances) == len(dot_products)
    for i in range(len(topic_docs)):
        doc = topic_docs[i]
        doc['embedding'] = doc_embeddings[i]
        doc['metadata']['topic']['cosine_similarity'] = cosine_similarities[i]
        doc['metadata']['topic']['euclidean_distance'] = euclidean_distances[i]
        doc['metadata']['topic']['dot_product'] = dot_products[i]
            
    if original_length > reduce_length_1 * 1.1:
        
        # reduce by probability
        reduced_by_probability_docs = reduce_docs_to_length(topic_docs.copy(), ['metadata','topic', 'probability'], reduce_length_1, remove_highest_first=False)
        print(f"\nCharacter length of topic docs after reduction by probability: {len(to_single_string(reduced_by_probability_docs))}")
        print(f"Number of topic docs after reduction by probability: {len(reduced_by_probability_docs)}")
        print(f"Number of sources after reduction by probability: {len(set(doc['metadata']['source']['id'] for doc in reduced_by_probability_docs))}")
        print(f"Minimum probability increased from {min(doc['metadata']['topic']['probability'] for doc in topic_docs)} to {min(doc['metadata']['topic']['probability'] for doc in reduced_by_probability_docs)}")
        folder = topic['name'].replace(' ', '_')
        
        # reduce by probability doesnt always work because many docs can have probability 1
        if len(to_single_string(reduced_by_probability_docs)) > reduce_length_1 * 1.1:
            print("Reducing by probability did not reduce the length enough, reducing more by euclidean distance")
            # so reduce by euclidean distance
            reduced_by_probability_docs = reduce_docs_to_length(reduced_by_probability_docs, ['metadata','topic', 'euclidean_distance'], reduce_length_1, remove_highest_first=True)
            print(f"Character length of topic docs after reduction by euclidean distance: {len(to_single_string(reduced_by_probability_docs))}")
            print(f"Number of topic docs after reduction by euclidean distance: {len(reduced_by_probability_docs)}")
            print(f"Number of sources after reduction by euclidean distance: {len(set(doc['metadata']['source']['id'] for doc in reduced_by_probability_docs))}")
            print(f"Maximum euclidean distance decreased from {max(doc['metadata']['topic']['euclidean_distance'] for doc in topic_docs)} to {max(doc['metadata']['topic']['euclidean_distance'] for doc in reduced_by_probability_docs)}")
        if not os.path.exists(folder):
            os.makedirs(folder)
        save_markdown_file(reduced_by_probability_docs, f"{folder}/probability_reduced.md")

        # reduce by vector similarity

        reduced_by_cosine_similarity_docs = reduce_docs_to_length(topic_docs.copy(), ['metadata','topic', 'cosine_similarity'], reduce_length_1, remove_highest_first=False)
        print(f"\nCharacter length of topic docs after reduction by cosine similarity: {len(to_single_string(reduced_by_cosine_similarity_docs))}")
        print(f"Number of topic docs after reduction by cosine similarity: {len(reduced_by_cosine_similarity_docs)}")
        print(f"Number of sources after reduction by cosine similarity: {len(set(doc['metadata']['source']['id'] for doc in reduced_by_cosine_similarity_docs))}")
        print(f"Minimum cosine similarity increased from {min(doc['metadata']['topic']['cosine_similarity'] for doc in topic_docs)} to {min(doc['metadata']['topic']['cosine_similarity'] for doc in reduced_by_cosine_similarity_docs)}")

        folder = topic['name'].replace(' ', '_')
        if not os.path.exists(folder):
            os.makedirs(folder)
        save_markdown_file(reduced_by_cosine_similarity_docs, f"{folder}/cosine_reduced.md")

        reduced_by_euclidean_distance_docs = reduce_docs_to_length(topic_docs.copy(), ['metadata','topic', 'euclidean_distance'], reduce_length_1, remove_highest_first=True)
        print(f"\nCharacter length of topic docs after reduction by euclidean distance: {len(to_single_string(reduced_by_euclidean_distance_docs))}")
        print(f"Number of topic docs after reduction by euclidean distance: {len(reduced_by_euclidean_distance_docs)}")
        print(f"Number of sources after reduction by euclidean distance: {len(set(doc['metadata']['source']['id'] for doc in reduced_by_euclidean_distance_docs))}")
        print(f"Maximum euclidean distance decreased from {max(doc['metadata']['topic']['euclidean_distance'] for doc in topic_docs)} to {max(doc['metadata']['topic']['euclidean_distance'] for doc in reduced_by_euclidean_distance_docs)}")

        folder = topic['name'].replace(' ', '_')
        if not os.path.exists(folder):
            os.makedirs(folder)
        save_markdown_file(reduced_by_euclidean_distance_docs, f"{folder}/euclidean_reduced.md")

        reduced_by_dot_product_docs = reduce_docs_to_length(topic_docs.copy(), ['metadata','topic', 'dot_product'], reduce_length_1, remove_highest_first=False)
        print(f"\nCharacter length of topic docs after reduction by dot product: {len(to_single_string(reduced_by_dot_product_docs))}")
        print(f"Number of topic docs after reduction by dot product: {len(reduced_by_dot_product_docs)}")
        print(f"Number of sources after reduction by dot product: {len(set(doc['metadata']['source']['id'] for doc in reduced_by_dot_product_docs))}")
        print(f"Minimum dot product increased from {min(doc['metadata']['topic']['dot_product'] for doc in topic_docs)} to {min(doc['metadata']['topic']['dot_product'] for doc in reduced_by_dot_product_docs)}")

        folder = topic['name'].replace(' ', '_')
        if not os.path.exists(folder):
            os.makedirs(folder)
        save_markdown_file(reduced_by_dot_product_docs, f"{folder}/dot_reduced.md")
        
        # plot correlation of probability, cosine similarity, euclidean distance, and dot product here
        df = pd.DataFrame({
            'probability': [doc['metadata']['topic']['probability'] for doc in topic_docs],
            'cosine_similarity': [doc['metadata']['topic']['cosine_similarity'] for doc in topic_docs],
            'euclidean_distance': [doc['metadata']['topic']['euclidean_distance'] for doc in topic_docs],
            'dot_product': [doc['metadata']['topic']['dot_product'] for doc in topic_docs]
        })
        
        plt.figure(figsize=(10, 8))
        sns.heatmap(df.corr(), annot=True, cmap='coolwarm', vmin=-1, vmax=1)
        plt.title('Correlation Matrix')
        plt.tight_layout()
        plt.savefig(f"{folder}/correlation_matrix_1.png")
        plt.close()
        
    else:
        print("\nDid not reduce by probability, vector similarity, or euclidean distance because the original length was not long enough")

    if ('reduced_by_euclidean_distance_docs' in locals() and len(to_single_string(reduced_by_euclidean_distance_docs)) > reduce_length_2 * 1.1) or ('reduced_by_euclidean_distance_docs' not in locals() and original_length > reduce_length_2 * 1.1):
        # Reduce further by eucledean distance
        if 'reduced_by_euclidean_distance_docs' in locals():
            source_docs = reduced_by_euclidean_distance_docs
        else:
            source_docs = topic_docs
        reduced_further_by_euclidean_distance_docs = reduce_docs_to_length(source_docs.copy(), ['metadata','topic', 'euclidean_distance'], reduce_length_2, remove_highest_first=True)
        print(f"\nCharacter length of topic docs after reduction by euclidean distance: {len(to_single_string(reduced_further_by_euclidean_distance_docs))}")
        print(f"Number of topic docs after reduction by euclidean distance: {len(reduced_further_by_euclidean_distance_docs)}")
        print(f"Number of sources after reduction by euclidean distance: {len(set(doc['metadata']['source']['id'] for doc in reduced_further_by_euclidean_distance_docs))}")
        print(f"Maximum euclidean distance decreased from {max(doc['metadata']['topic']['euclidean_distance'] for doc in source_docs)} to {max(doc['metadata']['topic']['euclidean_distance'] for doc in reduced_further_by_euclidean_distance_docs)}")

        folder = topic['name'].replace(' ', '_')
        if not os.path.exists(folder):
            os.makedirs(folder)
        save_markdown_file(reduced_further_by_euclidean_distance_docs, f"{folder}/euclidean_reduced_2.md")

        # Reduce further by reranker
        co = cohere.Client()

        # count query tokens
        response = co.tokenize(text=f"What can be said about {topic['name']}?", model="rerank-english-v2.0", offline=False)
        query_tokens = len(response.tokens)

        for doc in source_docs:
            response = co.tokenize(text=doc['page_content'], model="rerank-english-v2.0", offline=False)
            if len(response.tokens) + query_tokens > 512:
                print(f"Document {doc.metadata['source']['title']} has {len(response.tokens)} tokens")

        # Initialize the Portkey client
        cohere_portkey = Portkey(
            api_key=os.getenv("PORTKEY_API_KEY"), 
            virtual_key="trial-cohere-679b13" 
        )

        completion = cohere_portkey.post(
            '/rerank',
            return_documents=False,
            max_chunks_per_doc=1,
            model="rerank-english-v2.0",
            query=f"What can be said about {topic['name']}?",
            documents=[doc['page_content'] for doc in source_docs]
        )

        for result in completion.results:
            source_docs[result["index"]]['metadata']['topic']["rerank_score"] = result["relevance_score"]
            
        reduced_by_rerank_score_docs = reduce_docs_to_length(source_docs.copy(), ['metadata','topic', 'rerank_score'], reduce_length_2, remove_highest_first=False)
        print(f"\nCharacter length of topic docs after reduction by rerank score: {len(to_single_string(reduced_by_rerank_score_docs))}")
        print(f"Number of topic docs after reduction by rerank score: {len(reduced_by_rerank_score_docs)}")
        print(f"Number of sources after reduction by rerank score: {len(set(doc['metadata']['source']['id'] for doc in reduced_by_rerank_score_docs))}")
        print(f"Minimum rerank score increased from {min(doc['metadata']['topic']['rerank_score'] for doc in source_docs)} to {min(doc['metadata']['topic']['rerank_score'] for doc in reduced_by_rerank_score_docs)}")

        folder = topic['name'].replace(' ', '_')
        if not os.path.exists(folder):
            os.makedirs(folder)
        save_markdown_file(reduced_by_rerank_score_docs, f"{folder}/rerank_reduced_2.md")
        
        df = pd.DataFrame({
            'euclidean_distance': [doc['metadata']['topic']['euclidean_distance'] for doc in source_docs],
            'rerank_score': [doc['metadata']['topic']['rerank_score'] for doc in source_docs]
        })
        
        plt.figure(figsize=(8, 6))
        sns.scatterplot(data=df, x='euclidean_distance', y='rerank_score')
        plt.title('Euclidean Distance vs Rerank Score')
        plt.xlabel('Euclidean Distance')
        plt.ylabel('Rerank Score')
        plt.tight_layout()
        plt.savefig(f"{folder}/correlation_plot_2.png")
        plt.close()
        
    else:
        print("\nDid not reduce further by euclidean distance or reranker because the original length was not long enough")

async def main():
    
    reduce_length_1 = 8000
    reduce_length_2 = 4000
    
    # test data
    topics = [
        {
            "presentation_id": "018efa53-2169-7dc0-ad63-e7084a09afc4",
            "presentation_topic": "Exploring Cultural Contrasts: Japan vs. the USA - Insights for American Expats",
            "presentation_audience": "American expats living in Japan",
            "presentation_goal": "To inform and offer practical tips to American expats living in Japan about the cultural contrasts between Japan and the USA",
            "id": "066236b0-e1e0-77d4-8000-590e777d7d29",
            "name": "Cultural Influence on Help Seeking and Support from Professionals and Others"
        },
        {
            "presentation_id": "018efa53-2169-7dc0-ad63-e7084a09afc4",
            "presentation_topic": "Exploring Cultural Contrasts: Japan vs. the USA - Insights for American Expats",
            "presentation_audience": "American expats living in Japan",
            "presentation_goal": "To inform and offer practical tips to American expats living in Japan about the cultural contrasts between Japan and the USA",
            "id": "066236b0-e1e0-7967-8000-39e03b240974",
            "name": "Indirect Communication in Japanese Culture"
        },
        {
            "presentation_id": "018efa6a-2208-79d3-a905-958f91b06da7",
            "presentation_topic": "Antitrust pressure against Apple: History, Antitrust Arguments, and Apple's Counterarguments",
            "presentation_audience": "Tech enthusiasts and consumers",
            "presentation_goal": "Just inform the audience without a persuasive bias",
            "id": "06623708-33af-7e71-8000-883e8038cf64",
            "name": "Apple's Antitrust Allegations and Competition Concerns"
        },
        {
            "presentation_id": "018efa76-2369-7861-b1b7-592b3e5c275f",
            "presentation_topic": "The 7 Natural Wonders of the World",
            "presentation_audience": "Travelers and nature enthusiasts",
            "presentation_goal": "To inform the audience about the 7 natural wonders of the world, their locations, and what makes them special",
            "id": "0662373e-4a90-7df1-8000-eaae8e2f7505",
            "name": "Mount Everest - The Tallest Peak in the World"
        },
        {
            "presentation_id": "018efa76-2369-7861-b1b7-592b3e5c275f",
            "presentation_topic": "The 7 Natural Wonders of the World",
            "presentation_audience": "Travelers and nature enthusiasts",
            "presentation_goal": "To inform the audience about the 7 natural wonders of the world, their locations, and what makes them special",
            "id": "06623734-5459-7ea5-8000-1842ed1b986e",
            "name": "Youngest Volcano in Northern Hemisphere - Paricutin, Mexico"
        },
        {
            "presentation_id": "018efa80-4216-71c9-b37c-b55cb8e17a2d",
            "presentation_topic": "Understanding the Transformer Model Architecture: Revolutionizing Natural Language Processing\n\nTo give an informative high-level overview of the Transformer model architecture.",
            "presentation_audience": "Artificial Intelligence and Machine Learning researchers and students",
            "presentation_goal": "To give an informative high-level overview of the Transformer model architecture.",
            "id": "0662375b-e9fe-7154-8000-0e67ffd84570",
            "name": "Multi-Head Attention Mechanisms in Transformer Architecture"
        }
    ]
    
    # for topic in tqdm(topics):
    for topic in topics:
        await reduce_docs(reduce_length_1, reduce_length_2, topic)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())