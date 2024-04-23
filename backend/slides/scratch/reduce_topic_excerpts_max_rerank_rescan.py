from dotenv import load_dotenv
import os
import sys

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

async def vectorize_and_add_similairty(docs, topic):
    # vectorize
    portkeyHeaders = createHeaders(
        provider="openai",
        api_key=os.getenv("PORTKEY_API_KEY"),
    )
    openai_embeddings = OpenAIEmbeddings(model="text-embedding-3-small", dimensions=512, base_url=PORTKEY_GATEWAY_URL, default_headers=portkeyHeaders)
    vectors = await openai_embeddings.aembed_documents([doc['page_content'] for doc in docs])
    doc_embeddings = np.array(vectors)

    query_embedding = await openai_embeddings.aembed_query(topic['name'])

    # try 3 different metrics
    cosine_similarities = np.dot(doc_embeddings, query_embedding) / (np.linalg.norm(doc_embeddings, axis=1) * np.linalg.norm(query_embedding))
    euclidean_distances = np.linalg.norm(doc_embeddings - query_embedding, axis=1)
    dot_products = np.dot(doc_embeddings, query_embedding)

    # add the metrics and the embeddings
    assert len(docs) == len(doc_embeddings) == len(cosine_similarities) == len(euclidean_distances) == len(dot_products)
    for i in range(len(docs)):
        doc = docs[i]
        doc['embedding'] = doc_embeddings[i]
        doc['metadata']['cosine_similarity'] = cosine_similarities[i]
        doc['metadata']['euclidean_distance'] = euclidean_distances[i]
        doc['metadata']['dot_product'] = dot_products[i]
        
    return docs

async def reduce_docs(reduce_length, topic):
    
    # Get chunked and labeled documents from S3 for whole presentation
    all_docs = await download_model_list_from_s3(Document, f"{topic['presentation_id']}/all_sources_chunked_docs_with_topics.json")
    all_docs = [dict(doc) for doc in all_docs]

    # Get topic docs
    topic_docs = [doc for doc in all_docs if 'topic' in doc['metadata'] and doc['metadata']['topic']['name'] == topic['name']]
    topic_docs = [dict(doc) for doc in topic_docs]

    print(f"Character length of bertopic topic docs: {len(to_single_string(topic_docs))}")
    print(f"Number of bertopic topic docs: {len(topic_docs)}")
    print(f"Number of sources in bertopic topic docs: {len(set(doc['metadata']['source']['id'] for doc in topic_docs))}")

    folder = topic['name'].replace(' ', '_')
    if not os.path.exists(folder):
        os.makedirs(folder)
    save_markdown_file(topic_docs, f"{folder}/original.md")

    original_bertopic_docs_length = len(to_single_string(topic_docs))
    
    if original_bertopic_docs_length >= reduce_length * 1.2:
        all_docs = await vectorize_and_add_similairty(all_docs, topic)
        print(f"\nCharacter length of all docs: {len(to_single_string(all_docs))}")
        print(f"Number of all docs: {len(all_docs)}")
        print(f"Number of sources in all docs: {len(set(doc['metadata']['source']['id'] for doc in all_docs))}")
                    
        # reduce by euclidean distance
        reduced_by_vector_similarity = reduce_docs_to_length(all_docs.copy(), ['metadata', 'euclidean_distance'], 49000, remove_highest_first=True)
        
        print(f"\nCharacter length of all docs after reduction by vector similarity: {len(to_single_string(reduced_by_vector_similarity))}")
        print(f"Number of all docs after reduction by vector similarity: {len(reduced_by_vector_similarity)}")
        print(f"Number of sources in all docs after reduction by vector similarity: {len(set(doc['metadata']['source']['id'] for doc in reduced_by_vector_similarity))}")
        print(f"Maximum euclidean distance decreased from {max(doc['metadata']['euclidean_distance'] for doc in all_docs)} to {max(doc['metadata']['euclidean_distance'] for doc in reduced_by_vector_similarity)}")
        
            
        # reduce with reranker
        
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
            documents=[doc['page_content'] for doc in reduced_by_vector_similarity],
        )

        for result in completion.results:
            reduced_by_vector_similarity[result["index"]]['metadata']["rerank_score"] = result["relevance_score"]
            
        reduced_by_rerank_score_docs = reduce_docs_to_length(reduced_by_vector_similarity.copy(), ['metadata','rerank_score'], reduce_length, remove_highest_first=False)
        print(f"\nCharacter length of topic docs after reduction by rerank score: {len(to_single_string(reduced_by_rerank_score_docs))}")
        print(f"Number of topic docs after reduction by rerank score: {len(reduced_by_rerank_score_docs)}")
        print(f"Number of sources after reduction by rerank score: {len(set(doc['metadata']['source']['id'] for doc in reduced_by_rerank_score_docs))}")
        print(f"Minimum rerank score increased from {min(doc['metadata']['rerank_score'] for doc in reduced_by_vector_similarity)} to {min(doc['metadata']['rerank_score'] for doc in reduced_by_rerank_score_docs)}")

        folder = topic['name'].replace(' ', '_')
        if not os.path.exists(folder):
            os.makedirs(folder)
        save_markdown_file(reduced_by_rerank_score_docs, f"{folder}/rerank_reduced_4.md")
        
    else:
        print("\nBerTopic topic docs are already short enough. No need to reduce further.")

async def main():
    
    reduce_length = 4000
    
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
        await reduce_docs(reduce_length, topic)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())