from typing import List
import global_prompts_config
from dynamodb_service import get_items_with_user, update_items_with_user
import asyncio
from slides.generate_initial.generate_slides import make_presentation_slides
from s3 import download_model_list_from_s3, download_np_array_from_s3
from portkey_ai import PORTKEY_GATEWAY_URL, createHeaders
from langchain_openai import OpenAIEmbeddings
import numpy as np
from langchain.docstore.document import Document
import os

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

async def load_slides(presentation_id, messages, memory, emitter):
    # in slides interface, interface_data is not used, client fetches data directly from dynamodb. Memory is used to store slide_list on this side. interface_update sio emit is used to send a push message to client.
    newMessages = []

    # first check if candidate topics are already in dynamodb
    # presentation = await get_presentation(presentation_id, ['slide_generation_status'])
    presentation = await get_items_with_user('presentation', {'presentation_id': presentation_id}, ['slide_generation_status'])

    if memory.get('creating_slides_this_session') == True:
        print('Already creating slides this session, skipping...')
        return
        
    if presentation.get('slide_generation_status') == 'invoked':
        memory['creating_slides_this_session'] = True
        # keep polling until the topic extraction is done
        print('Waiting for slide generation to complete (already invoked)...')
        while 'slide_generation_status' not in presentation or presentation.get('slide_generation_status') != 'complete':
            await asyncio.sleep(5)
            # presentation = await get_presentation(presentation_id, ['slide_generation_status'])
            presentation = await get_items_with_user('presentation', [{'presentation_id': presentation_id}], ['slide_generation_status'])
    else:
        # Get all_docs
        all_docs_task = asyncio.create_task(download_model_list_from_s3(Document, f"{presentation_id}/all_sources_chunked_docs_with_topics.json"))
        embeddings_task = asyncio.create_task(download_np_array_from_s3(f"{presentation_id}/all_sources_chunked_embeddings.npy"))
        all_docs, embeddings = await asyncio.gather(all_docs_task, embeddings_task)
        all_docs = await vectorize_docs(all_docs, embeddings)
        
        if all_docs is not None:
            all_docs_readonly = ReadOnlyDocuments(all_docs)
            all_docs = all_docs_readonly.documents
        else:
            # Handle the case when all_docs is None
            print("Failed to download documents from S3")
            
        # await update_presentation(presentation_id, slide_generation_status='invoked')
        await update_items_with_user('presentation', [{'presentation_id': presentation_id, 'slide_generation_status': 'invoked'}])
        
        slide_list = await make_presentation_slides(presentation_id, emitter, all_docs)

    memory['slides_created'] = True
    memory['slide_list'] = slide_list

    newMessages += [message for message in global_prompts_config.get_interface_changed_messages(
        "slides") if message['role'] == 'assistant']
    messages += global_prompts_config.get_interface_changed_messages("slides")

    for message in newMessages:
        await emitter('message', message)

    return
