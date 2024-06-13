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

portkeyHeaders = createHeaders(
        provider="openai",
        api_key=os.getenv("PORTKEY_API_KEY"),
    )
openai_embeddings = OpenAIEmbeddings(model="text-embedding-3-small", dimensions=512, base_url=PORTKEY_GATEWAY_URL, default_headers=portkeyHeaders)

cohere_portkey = AsyncPortkey(
    api_key=os.getenv("PORTKEY_API_KEY"), 
    virtual_key="production-cohe-928a08" 
)

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

async def add_cosine_similarity(docs, query):
    doc_embeddings = [doc.get('metadata', []).get('embedding', []) for doc in docs]
    if len(doc_embeddings) != len(docs):
        print(f"Warning: Number of documents and embeddings do not match (docs: {len(docs)}, embeddings: {len(doc_embeddings)})")
        print(f"Regenerating embeddings.")
        doc_embeddings = await openai_embeddings.aembed_documents([doc['page_content'] for doc in docs])
    
    query_embedding = await openai_embeddings.aembed_query(query)
    cosine_similarities = np.dot(doc_embeddings, query_embedding) / (np.linalg.norm(doc_embeddings, axis=1) * np.linalg.norm(query_embedding))
    docs = [dict(doc, metadata=dict(doc['metadata'], topic=dict(doc['metadata']['topic'], cosine_similarity=cosine_similarity))) for doc, cosine_similarity in zip(docs, cosine_similarities)]
    return docs
    
async def add_rerank_score(docs, query):
    # Initialize the Portkey client

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
    topic_docs = [doc for doc in all_docs if doc.get('metadata', {}).get('topic', {}).get('id') == topic_id]
    # topic_docs = [dict(doc) for doc in topic_docs]
    
    # print(f"Original number of topic docs: {len(topic_docs)}")
    # print(f"Original character length of topic docs: {len(to_single_string(topic_docs))}")
    # print(f"Original number of sources: {len(set(doc['metadata']['source']['id'] for doc in topic_docs))}")

    original_length = len(to_single_string(topic_docs))
    
    if original_length >= 49999:
        # reduce to 49000 characters with vector similarity
        
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

        print(f"USED RERANKER FOR {topic_name}")
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
