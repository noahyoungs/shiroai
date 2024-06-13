import global_prompts_config
from dynamodb import get_presentation, get_sources
from s3 import download_model_list_from_s3, download_np_array_from_s3
from langchain.docstore.document import Document
import json
import asyncio
from typing import List
from langchain_openai import OpenAIEmbeddings
from portkey_ai import PORTKEY_GATEWAY_URL, createHeaders, AsyncPortkey
import os
import numpy as np

interface = "slides"

class ReadOnlyDocuments:
    def __init__(self, documents: List[dict]):
        self._documents = documents

    @property
    def documents(self) -> List[dict]:
        return self._documents


async def vectorize_docs(docs, embeddings=None):
    if docs is None:
        return None
    
    # convert docs from list of Document objects to list of dictionaries
    if type(docs[0]) == Document:
        docs = [dict(doc) for doc in docs]
        
    if (len(docs) != len(embeddings)):
        print(f"Warning: Number of documents and embeddings do not match (docs: {len(docs)}, embeddings: {len(embeddings)})")
        embeddings = None        
        
    if embeddings is None:
        print("Warning: Generating new embeddings.")
        portkeyHeaders = createHeaders(
            provider="openai",
            api_key=os.getenv("PORTKEY_API_KEY"),
        )
        openai_embeddings = OpenAIEmbeddings(model="text-embedding-3-small", dimensions=512, base_url=PORTKEY_GATEWAY_URL, default_headers=portkeyHeaders)
        vectors = await openai_embeddings.aembed_documents([doc['page_content'] for doc in docs])
        embeddings = np.array(vectors)
        
    if (len(docs) != len(embeddings)):
        raise ValueError(f"Number of documents and embeddings do not match (docs: {len(docs)}, embeddings: {len(embeddings)})")
    for doc, embedding in zip(docs, embeddings):
        doc['metadata']['embedding'] = embedding
    return docs 


async def initialize(presentation_id):
    # get interface keys
    memory = {}

    presentation_task = asyncio.create_task(get_presentation(presentation_id, ['messages', 'status', 'topic', 'outline', 'audience', 'goal', 'slide_generation_status']))
    all_docs_task = asyncio.create_task(download_model_list_from_s3(Document, f"{presentation_id}/all_sources_chunked_docs_with_topics.json"))
    embeddings_task = asyncio.create_task(download_np_array_from_s3(f"{presentation_id}/all_sources_chunked_embeddings.npy"))
    presentation, all_docs, embeddings = await asyncio.gather(presentation_task, all_docs_task, embeddings_task)
    
    all_docs = await vectorize_docs(all_docs, embeddings)

    if all_docs is not None:
        all_docs_readonly = ReadOnlyDocuments(all_docs)
        all_docs = all_docs_readonly.documents
    else:
        # Handle the case when all_docs is None
        print("Failed to download documents from S3")

    # Check if 'messages' exists in the presentation and is not None
    if 'messages' in presentation and presentation['messages'] is not None:
        # If so, parse it from JSON
        print(f"Loading existing messages for presentation {presentation_id}")
        messages = json.loads(presentation['messages'])
    else:
        # Otherwise, use the default list directly
        print(f"No existing messages for presentation {presentation_id}")
        messages = global_prompts_config.initial_messages.copy()

    if 'memory' in presentation and presentation['memory'] is not None:
        memory = json.loads(presentation['memory'])

    # check if slides are created
    if presentation.get('slide_generation_status') == 'complete':
        slides_created = True
    else:
        slides_created = False

    # Messages that enter right after interface change
    if presentation['status'] != interface:
        # Please wait message
        messages.append({'role': 'assistant', 'content': "Please allow me a moment while I create your slides. This can take up to a minute. Thank you for your patience."})

        # background about previous steps
        summary_message = {'role': 'system', 'content': f"Remember, you are working on a presentation with these parameters:\n\nPresentation Topic:\n{presentation['topic']}\n\nTarget Audience:\n{presentation['audience']}\n\nPresentation Goal:\n{presentation['goal']}"}
        messages.append(summary_message)

    interfaceData = {
        'slides_created': slides_created
    }

    return messages, interfaceData, memory, all_docs