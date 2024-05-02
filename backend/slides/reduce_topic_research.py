from dotenv import load_dotenv
import os
from s3 import download_np_array_from_s3
from slides.format import format_topic
from langchain_openai import OpenAIEmbeddings
from portkey_ai import PORTKEY_GATEWAY_URL, createHeaders, AsyncPortkey
import numpy as np
from dotenv import load_dotenv
from botocore.exceptions import ClientError

load_dotenv()

def to_single_string(documents):
    if type(documents[0]) == dict:
        return "\n\n".join([doc['page_content'] for doc in documents])
    else:
        return "\n\n".join([
            doc.page_content 
            for doc in documents
        ]).strip()
        
        
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

async def vectorize_docs(presentation_id, docs):
    
    embeddings_s3_key = f"{presentation_id}/all_sources_chunked_embeddings.npy"
    
    try:
        # Call the download_np_array_from_s3 function
        embeddings_array = await download_np_array_from_s3(embeddings_s3_key)
    
    except ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchKey':
            print("Warning: Embeddings file not found in S3. Generating new embeddings.")
        else:
            print("Warning: Error downloading array from S3. Generating new embeddings. Error:", str(e))
    
    except Exception as e:
        print("Warning Error downloading array from S3. Generating new embeddings. Error:", str(e))
        
    if embeddings_array is None:
        portkeyHeaders = createHeaders(
            provider="openai",
            api_key=os.getenv("PORTKEY_API_KEY"),
        )
        openai_embeddings = OpenAIEmbeddings(model="text-embedding-3-small", dimensions=512, base_url=PORTKEY_GATEWAY_URL, default_headers=portkeyHeaders)
        vectors = await openai_embeddings.aembed_documents([doc['page_content'] for doc in docs])
        embeddings_array = np.array(vectors)
        
    assert len(docs) == len(embeddings_array)
    for doc, embedding in zip(docs, embeddings_array):
        doc['metadata']['embedding'] = embedding
    return docs 

async def add_cosine_similarity(docs, query):
    portkeyHeaders = createHeaders(
        provider="openai",
        api_key=os.getenv("PORTKEY_API_KEY"),
    )
    openai_embeddings = OpenAIEmbeddings(model="text-embedding-3-small", dimensions=512, base_url=PORTKEY_GATEWAY_URL, default_headers=portkeyHeaders)
    query_embedding = await openai_embeddings.aembed_query(query)
    doc_embeddings = np.array([doc['metadata']['embedding'] for doc in docs])
    cosine_similarities = np.dot(doc_embeddings, query_embedding) / (np.linalg.norm(doc_embeddings, axis=1) * np.linalg.norm(query_embedding))
    docs = [dict(doc, metadata=dict(doc['metadata'], topic=dict(doc['metadata']['topic'], cosine_similarity=cosine_similarity))) for doc, cosine_similarity in zip(docs, cosine_similarities)]
    return docs
    
async def add_rerank_score(docs, query):
    # Initialize the Portkey client
    cohere_portkey = AsyncPortkey(
        api_key=os.getenv("PORTKEY_API_KEY"), 
        virtual_key="trial-cohere-679b13" 
    )

    completion = await cohere_portkey.post(
        '/rerank',
        return_documents=False,
        max_chunks_per_doc=1,
        model="rerank-english-v2.0",
        query=query,
        documents=[doc['page_content'] for doc in docs],
    )

    for result in completion.results:
        docs[result["index"]]['metadata']['topic']["rerank_score"] = result["relevance_score"]
    return docs
    

async def reduce_docs(presentation_id, all_docs, reduce_length, topic_name, topic_id):
    
    # Get topic docs
    topic_docs = [doc for doc in all_docs if doc.metadata.get('topic', {}).get('id') == topic_id]
    topic_docs = [dict(doc) for doc in topic_docs]
    
    # print(f"Original number of topic docs: {len(topic_docs)}")
    # print(f"Original character length of topic docs: {len(to_single_string(topic_docs))}")
    # print(f"Original number of sources: {len(set(doc['metadata']['source']['id'] for doc in topic_docs))}")

    original_length = len(to_single_string(topic_docs))
    
    if original_length >= 49999:
        # reduce to 49000 characters with vector similarity
        # vectroize docs
        topic_docs = await vectorize_docs(presentation_id, topic_docs)
        
        # add cosine similarity
        topic_docs = await add_cosine_similarity(topic_docs, topic_name)
            
        # reduce by cosine similarity
        reduced_by_vector_similarity = reduce_docs_to_length(topic_docs.copy(), ['metadata','topic', 'cosine_similarity'], 49000, remove_highest_first=True)
        
        # print(f"\nCharacter length of topic docs after reduction by vector similarity: {len(to_single_string(reduced_by_vector_similarity))}")
        # print(f"Number of topic docs after reduction by vector similarity: {len(reduced_by_vector_similarity)}")
        # print(f"Number of sources after reduction by vector similarity: {len(set(doc['metadata']['source']['id'] for doc in reduced_by_vector_similarity))}")
        
        original_length = len(to_single_string(reduced_by_vector_similarity))
        topic_docs = reduced_by_vector_similarity
            
    if original_length > reduce_length * 1.2:
        source_docs = topic_docs
        # reduce with reranker
        
        # co = cohere.Client()

        # # count query tokens
        # response = co.tokenize(text=f"What can be said about {topic['name']}?", model="rerank-english-v2.0", offline=False)
        # query_tokens = len(response.tokens)

        # for doc in source_docs:
        #     response = co.tokenize(text=doc['page_content'], model="rerank-english-v2.0", offline=False, request_options={"max_retries": 3})
        #     if len(response.tokens) + query_tokens > 512:
                # print(f"Document {doc.metadata['source']['title']} has {len(response.tokens)} tokens")

        source_docs = await add_rerank_score(source_docs, f"What can be said about {topic_name}?")
            
        reduced_by_rerank_score_docs = reduce_docs_to_length(source_docs.copy(), ['metadata','topic', 'rerank_score'], reduce_length, remove_highest_first=False)
        # print(f"\nCharacter length of topic docs after reduction by rerank score: {len(to_single_string(reduced_by_rerank_score_docs))}")
        # print(f"Number of topic docs after reduction by rerank score: {len(reduced_by_rerank_score_docs)}")
        # print(f"Number of sources after reduction by rerank score: {len(set(doc['metadata']['source']['id'] for doc in reduced_by_rerank_score_docs))}")
        # print(f"Minimum rerank score increased from {min(doc['metadata']['topic']['rerank_score'] for doc in source_docs)} to {min(doc['metadata']['topic']['rerank_score'] for doc in reduced_by_rerank_score_docs)}")
        
        return reduced_by_rerank_score_docs
        
    else:
        # print("\nDid not reduce by reranker because the original length was not long enough")
        return topic_docs

# async def main():
    
#     reduce_length = 4000
    
#         # test data
#     topics = [
#         {
#             "presentation_id": "018efa53-2169-7dc0-ad63-e7084a09afc4",
#             "presentation_topic": "Exploring Cultural Contrasts: Japan vs. the USA - Insights for American Expats",
#             "presentation_audience": "American expats living in Japan",
#             "presentation_goal": "To inform and offer practical tips to American expats living in Japan about the cultural contrasts between Japan and the USA",
#             "id": "066236b0-e1e0-77d4-8000-590e777d7d29",
#             "name": "Cultural Influence on Help Seeking and Support from Professionals and Others"
#         },
#         {
#             "presentation_id": "018efa53-2169-7dc0-ad63-e7084a09afc4",
#             "presentation_topic": "Exploring Cultural Contrasts: Japan vs. the USA - Insights for American Expats",
#             "presentation_audience": "American expats living in Japan",
#             "presentation_goal": "To inform and offer practical tips to American expats living in Japan about the cultural contrasts between Japan and the USA",
#             "id": "066236b0-e1e0-7967-8000-39e03b240974",
#             "name": "Indirect Communication in Japanese Culture"
#         },
#         {
#             "presentation_id": "018efa6a-2208-79d3-a905-958f91b06da7",
#             "presentation_topic": "Antitrust pressure against Apple: History, Antitrust Arguments, and Apple's Counterarguments",
#             "presentation_audience": "Tech enthusiasts and consumers",
#             "presentation_goal": "Just inform the audience without a persuasive bias",
#             "id": "06623708-33af-7e71-8000-883e8038cf64",
#             "name": "Apple's Antitrust Allegations and Competition Concerns"
#         },
#         {
#             "presentation_id": "018efa76-2369-7861-b1b7-592b3e5c275f",
#             "presentation_topic": "The 7 Natural Wonders of the World",
#             "presentation_audience": "Travelers and nature enthusiasts",
#             "presentation_goal": "To inform the audience about the 7 natural wonders of the world, their locations, and what makes them special",
#             "id": "0662373e-4a90-7df1-8000-eaae8e2f7505",
#             "name": "Mount Everest - The Tallest Peak in the World"
#         },
#         {
#             "presentation_id": "018efa76-2369-7861-b1b7-592b3e5c275f",
#             "presentation_topic": "The 7 Natural Wonders of the World",
#             "presentation_audience": "Travelers and nature enthusiasts",
#             "presentation_goal": "To inform the audience about the 7 natural wonders of the world, their locations, and what makes them special",
#             "id": "06623734-5459-7ea5-8000-1842ed1b986e",
#             "name": "Youngest Volcano in Northern Hemisphere - Paricutin, Mexico"
#         },
#         {
#             "presentation_id": "018efa80-4216-71c9-b37c-b55cb8e17a2d",
#             "presentation_topic": "Understanding the Transformer Model Architecture: Revolutionizing Natural Language Processing\n\nTo give an informative high-level overview of the Transformer model architecture.",
#             "presentation_audience": "Artificial Intelligence and Machine Learning researchers and students",
#             "presentation_goal": "To give an informative high-level overview of the Transformer model architecture.",
#             "id": "0662375b-e9fe-7154-8000-0e67ffd84570",
#             "name": "Multi-Head Attention Mechanisms in Transformer Architecture"
#         }
#     ]
    
#     # Get chunked and labeled documents from S3 for whole presentation
#     all_docs = await download_model_list_from_s3(Document, f"{topic['presentation_id']}/all_sources_chunked_docs_with_topics.json")
    
#     # for topic in tqdm(topics):
#     for topic in topics:
#         await reduce_docs(reduce_length, topic)


# if __name__ == "__main__":
#     import asyncio
#     asyncio.run(main())