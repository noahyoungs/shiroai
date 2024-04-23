
from langchain.docstore.document import Document
from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter
import numpy as np
import re
import os
import asyncio
from dynamodb import get_sources, update_presentation, get_presentation
from s3 import download_model_from_s3, upload_data_to_s3, upload_model_list_to_s3
from bertopic import BERTopic
from bertopic.representation import KeyBERTInspired
from hdbscan import HDBSCAN
from openai import OpenAI
from portkey_ai import PORTKEY_GATEWAY_URL, createHeaders, AsyncPortkey
from bertopic.backend import OpenAIBackend
from langchain_openai import OpenAIEmbeddings
from outline.label_topic_prompt import get_prompt
from outline.rate_topic_prompt_messages import get_messages as get_rate_relevance_messages
from outline.rate_value_prompt_messages import get_messages as get_rate_value_messages
from copy import deepcopy
from dotenv import load_dotenv
import json
import concurrent.futures
import copy
from uuid_extensions import uuid7str


load_dotenv()


def to_single_string(documents):
    return "".join([
        doc.page_content + "\n\n"
        for doc in documents
    ]).strip()
    
def extract_xml_tag_contents(tag_name, text):
            pattern = r'<{0}>(.*?)</{0}>'.format(tag_name)
            match = re.search(pattern, text, re.DOTALL)
            if match:
                return match.group(1)
            else:
                return None
    

def split_markdown_document(document):
    headers_to_split_on = [
        ("#", "1"),
        ("##", "2"),
        ("###", "3"),
        ("####", "4"),
        ("#####", "5"),
        ("######", "6"),
    ]
    markdown = document.page_content
    metadata = document.metadata
    markdown_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)
    split_docs = markdown_splitter.split_text(markdown)

    for split_doc in split_docs:
        # create a new dictionary to store the metadata for the split document
        split_metadata = {}
        # move everything in split_doc.metadata to split_metadata['headers']
        # and remove the numbering from the headers (e.g. '1. Introduction' -> 'Introduction' and '2\. Background' -> 'Background')
        split_metadata['headers'] = {key: re.sub(r'\d+\\\?\.\\s*', '', value) for key, value in split_doc.metadata.items()}
        # create a shallow copy of the original metadata and update it with the split metadata
        split_metadata.update(metadata.copy())
        # assign the updated metadata to the split document
        split_doc.metadata = split_metadata

    return split_docs

def split_markdown_documents(documents):
    split_docs = []
    for document in documents:
        batch_split_docs = split_markdown_document(document)
        split_docs += batch_split_docs
    return split_docs

async def vectorize_docs(docs):
    portkeyHeaders = createHeaders(
        provider="openai",
        api_key=os.getenv("PORTKEY_API_KEY"),
    )
    openai_embeddings = OpenAIEmbeddings(model="text-embedding-3-small", dimensions=512, base_url=PORTKEY_GATEWAY_URL, default_headers=portkeyHeaders)
    doc_embeddings = await openai_embeddings.aembed_documents([doc.page_content for doc in docs])
    docs = [doc.copy(update={"metadata": {**doc.metadata, "embedding": embedding}}) for doc, embedding in zip(docs, doc_embeddings)]
    return docs 

def process_topics(chunk_strings, embeddings, portkey_trace=None):
    # embeddings maker for BERTopic, not used to make embeddings for docs
    client = OpenAI(
        base_url=PORTKEY_GATEWAY_URL,
        default_headers=createHeaders(
            provider="openai",
            api_key=os.environ.get("PORTKEY_API_KEY"),
            trace_id=portkey_trace,
        )
    )
    
    representation_model = KeyBERTInspired(nr_repr_docs=5)

    hdbscan_model = HDBSCAN(min_cluster_size=5, metric='euclidean', 
                            cluster_selection_method='leaf', prediction_data=True, min_samples=3)

    embedding_model = OpenAIBackend(client, "text-embedding-3-small", batch_size=2048, generator_kwargs={"dimensions": 512})

    topic_model = BERTopic(hdbscan_model=hdbscan_model, representation_model=representation_model, embedding_model=embedding_model)
    
    topics, probs = topic_model.fit_transform(chunk_strings, embeddings)

    # if len(topic_model.get_topics()) > 11:
    #     topic_model_similar_reduced = copy.deepcopy(topic_model)
    #     # reduce topics that are too similar
    #     print("Reducing topics using auto")
    #     topic_model_similar_reduced.reduce_topics(chunk_strings, nr_topics="auto")
    #     # we need at least 7 topics, dont know how much auto reduces to
    #     if len(topic_model_similar_reduced.get_topics()) >= 8:
    #         topic_model = topic_model_similar_reduced
    #         if len(topic_model.get_topics()) > 11:
    #             # if we still have more than 10 topics, reduce to 10
    #             print("Auto reduced not enough, reducing again to 10")
    #             topic_model.reduce_topics(chunk_strings, nr_topics=11)
    #     else:
    #         print("Auto reduced too much, reducing original topics to 10")
    #         topic_model.reduce_topics(chunk_strings, nr_topics=11)
    # else:
    #     print("Original topics 10 or less")
    
    if len(topic_model.get_topics()) > 11:
        print("Reducing topics to 10")
        topic_model.reduce_topics(chunk_strings, nr_topics=11)

        
    print(f"Final number of topics: {len(topic_model.get_topics())}")

    topic_info = topic_model.get_topic_info()
    document_info = topic_model.get_document_info(chunk_strings)
    return topic_info, document_info
    
async def _label_documents_and_extract_topics(presentationID):
    print(f"Labeling documents and extracting topics for presentation {presentationID}")
    
    portkey_trace = None 
    
    # get presentation and sources concurrently
    presentation_task = get_presentation(presentationID, ['topic', 'audience', 'goal'])
    sources_task = get_sources(presentationID)
    
    presentation, sources = await asyncio.gather(presentation_task, sources_task)

    whole_document_paths = [source['whole_document_path'] for source in sources if 'whole_document_path' in source]

    documents = []
    documents = await asyncio.gather(*[download_model_from_s3(Document, path) for path in whole_document_paths])
            
    # Splits  by markdown heading
    docs_split_by_header = split_markdown_documents(documents)
    
    # Delete any documents where any heading has 'References' in it
    docs_split_by_header = [doc for doc in docs_split_by_header if not any(re.search(r'References', header, re.IGNORECASE) for header in doc.metadata['headers'].values())]

    text_splitter = RecursiveCharacterTextSplitter(
        separators=[r"(?<=\n\n)|(?<=\n)|(?<=\.)\s|(?<=!)\s|(?<=\?)\s"],
        chunk_size=500,
        # chunk_overlap=0,
        length_function=len,
        is_separator_regex=True,
    )

    # splits further by about 500 characters at clean breaks
    docs_split_recursive = text_splitter.split_documents(docs_split_by_header)

    # remove short documents
    final_chunked_docs = [doc for doc in docs_split_recursive if len(doc.page_content) > 30]    
    # vectorize the documents
    final_chunked_docs = await vectorize_docs(final_chunked_docs)
    
    # sources = [doc.metadata.get("source", "Unknown") for doc in final_chunked_docs]

    # print(f"Total number of chunks: {len(bertopic_docs)}")
    # print(f"Total text length in chars (including spaces): {sum([len(text) for text in bertopic_docs])}")
    # print(f"Length of shortest chunk: {min([len(doc) for doc in bertopic_docs])} chars")
    # print(f"Length of longest chunk: {max([len(doc) for doc in bertopic_docs])} chars")

    #Bertopic only takes strings and embeddings no metadata
    chunk_strings = [doc.page_content for doc in final_chunked_docs]
    embeddings = np.array([doc.metadata['embedding'] for doc in final_chunked_docs])
    
    loop = asyncio.get_running_loop()
    with concurrent.futures.ProcessPoolExecutor() as process_executor:
        topic_info, document_info = await loop.run_in_executor(process_executor, process_topics, chunk_strings, embeddings)
        
    # # for debugging
    # topic_info, document_info = process_topics(chunk_strings, embeddings)
    
    # print(len(topic_info_df['Representative_Docs'].iloc[0]))
    # print(len(topic_model.get_representative_docs()[0]))

    async_portkey_bedrock = AsyncPortkey(
        virtual_key="aldeo-portkey-b-5cf75f",
        trace_id=portkey_trace,
        config={"cache": {"mode": "simple"}},
    )

    # Mistral 7B names the topics
    async def name_topic(keywords, documents):
        response = await async_portkey_bedrock.completions.create(
            model = "mistral.mistral-7b-instruct-v0:2",
            prompt = get_prompt(documents, keywords, presentation['topic']),
            temperature=0,
            max_tokens=30,
            stop=["\n"]
        )
        label = response.choices[0].text.strip()
        no_numbering = re.sub(r'\d+\.\s*', '', label).strip()
        no_quotes = re.sub(r'^[\'"]|[\'"]$', '', no_numbering).strip()
        no_periods = no_quotes.rstrip('.')
        return no_periods

    # Claude 3 Haiku rates the topics for relevance
    async def rate_topic_relevance(keywords, documents, label):
        
        response = await async_portkey_bedrock.chat.completions.create(
            model="anthropic.claude-3-haiku-20240307-v1:0",
            messages=get_rate_relevance_messages(presentation_topic=presentation['topic'], audience=presentation['audience'], goal=presentation['goal'], subtopic_label=label, documents=documents, keywords=keywords),
            temperature=0,
            stop=["</score>"],
            max_tokens=1000,
        )
        
        response_text = "<reasoning>" + response.choices[0].message.content.strip() + "</score>"
        rating = extract_xml_tag_contents("score", response_text)
        reasoning = extract_xml_tag_contents("reasoning", response_text)
        # replace '<reasoning> with '' and '</reasoning>' with ''
        reasoning = re.sub(r'<reasoning>|</reasoning>', '', reasoning)
        return rating, reasoning.strip()
    
    # Claude 3 Haiku rates the topics for value
    async def rate_topic_value(documents):
        
        response = await async_portkey_bedrock.chat.completions.create(
            model="anthropic.claude-3-haiku-20240307-v1:0",
            messages=get_rate_value_messages(topic=presentation['topic'], text=documents),
            temperature=0,
            stop=["</score>"],
            max_tokens=1000,
        )
        
        response_text = response.choices[0].message.content.strip() + "</score>"
        rating = extract_xml_tag_contents("score", response_text)
        reasoning = extract_xml_tag_contents("reasoning", response_text)
        # replace '<reasoning> with '' and '</reasoning>' with ''
        # reasoning = re.sub(r'<reasoning>|</reasoning>', '', reasoning)
        return rating, reasoning.strip()


    async def name_and_rate_topics(topic_info_df, n=10):
        names = {}
        relevance_ratings = {}
        relevance_reasonings = {}
        value_ratings = {}
        value_reasonings = {}

        if topic_info_df['Topic'].iloc[0] == -1:
            relevant_topics = topic_info_df.iloc[1:n+1]  # Select rows starting from index 1
        else:
            relevant_topics = topic_info_df.iloc[:n]

        async def process_row(row):
            topic_id = row['Topic']  # Get the topic ID from the 'Topic' column
            keywords = row['Representation']
            documents = row['Representative_Docs']
            keywords_formatted = ", ".join(keywords)
            documents_formatted = "\n\n".join(documents)

            topic_name = await name_topic(keywords_formatted, documents_formatted)

            relevance_task = asyncio.create_task(rate_topic_relevance(keywords_formatted, documents_formatted, topic_name))
            value_task = asyncio.create_task(rate_topic_value(documents_formatted))

            (topic_relevance_rating, relevance_reasoning), (topic_value_rating, value_reasoning) = await asyncio.gather(
                relevance_task, value_task
            )

            return topic_id, topic_name, topic_relevance_rating, relevance_reasoning, topic_value_rating, value_reasoning

        tasks = []
        for _, row in relevant_topics.iterrows():
            task = asyncio.create_task(process_row(row))
            tasks.append(task)

        results = await asyncio.gather(*tasks)

        for topic_id, topic_name, topic_relevance_rating, relevance_reasoning, topic_value_rating, value_reasoning in results:
            names[topic_id] = topic_name
            relevance_ratings[topic_id] = topic_relevance_rating
            relevance_reasonings[topic_id] = relevance_reasoning
            value_ratings[topic_id] = topic_value_rating
            value_reasonings[topic_id] = value_reasoning

        return names, relevance_ratings, relevance_reasonings, value_ratings, value_reasonings

    names, relevance_ratings, relevance_reasonings, value_ratings, value_reasonings = await name_and_rate_topics(topic_info, 10)
    topic_info['CustomName'] = topic_info['Topic'].map(names)
    document_info['CustomName'] = document_info['Topic'].map(names)
    
    # calculate prevalence of topics per class and show a graph
    # topics_per_class = topic_model.topics_per_class(bertopic_docs, classes=sources)
    # topic_model.visualize_topics_per_class(topics_per_class, top_n_topics=10, custom_labels=True)

    # aggregate a list of documents with topics in metadata
    docs_with_topics = deepcopy(final_chunked_docs)
    
    document_topic_data = document_info[['Topic', 'CustomName', 'Probability']].rename(columns={'Topic':'TopicNumber', 'CustomName': 'TopicName'})
    assert len(docs_with_topics) == len(document_topic_data)
    for i in range(len(docs_with_topics)):
        if document_topic_data.iloc[i]['TopicNumber'] != -1:
            docs_with_topics[i].metadata["topic"] = {
                "number": int(document_topic_data.iloc[i]['TopicNumber']),
                "name": document_topic_data.iloc[i]['TopicName'],
                "probability": float(document_topic_data.iloc[i]['Probability']),
            }
    # docs_with_topics is now filled with topics in metadata (list of Document objects)
    
    # add a uuidv7 to each document
    for doc in docs_with_topics:
        doc.metadata['id'] = uuid7str()
    
    # upload docs_with_topics to S3
    docs_with_topics_s3_key = f"{presentationID}/all_sources_chunked_docs_with_topics.json"
    
    await upload_model_list_to_s3(docs_with_topics, docs_with_topics_s3_key)
    
    # get all the rows in topic_info except where Topic is -1
    valid_topic_info = topic_info[topic_info['Topic'] != -1]
    
    # aggregate a list of topics with relevance ratings and reasonings
    topic_names = list(valid_topic_info['CustomName'])
    representative_docs = list(valid_topic_info['Representative_Docs'])
    keywords = list(valid_topic_info['Representation'])
    
    # transform representative_docs from list of strings to list of dicts with 'source' and 'content' keys
    
    topics = []
    for i in range(len(topic_names)):
        # look for each represenative doc in docs_with_topics
        excerpts = []
        for string in representative_docs[i]:
            doc = next((doc for doc in docs_with_topics if doc.page_content == string), None)
            if doc is not None:
                # if found, replace the string with a dict with 'source' and 'content' keys
                excerpt = {
                    'source': doc.metadata.get('source', 'Unknown'),
                    'content': string,
                }
            else:
                # if not found, replace the string with a dict with 'source' and 'content' keys
                excerpt = {
                    'source': 'Unknown',
                    'content': string,
                }
            excerpts.append(excerpt)
        
        topic = {
            'id': uuid7str(),
            'name': topic_names[i],
            'relevance_rating': relevance_ratings[i],
            'relevance_reasoning': relevance_reasonings[i],
            'value_rating': value_ratings[i],
            'value_reasoning': value_reasonings[i],
            'keywords': keywords[i],
            'excerpts': excerpts,
        }
        topics.append(topic)
    # topics is now filled with topics and their relevance ratings and reasonings (list of dicts)
    
    # upload topics to DynamoDB
    await update_presentation(presentationID, candidate_topics=json.dumps(topics))
    
    print(f"Finished labeling documents and extracting topics for presentation {presentationID}")
    return topics
    
# test function
async def label_documents_extract_topics(presentationID):
    loop = asyncio.get_running_loop()
    with concurrent.futures.ThreadPoolExecutor() as executor:
        topics = await loop.run_in_executor(executor, asyncio.run, _label_documents_and_extract_topics(presentationID))
    return topics
    
    
if __name__ == "__main__":
    asyncio.run(label_documents_extract_topics("018f0604-74de-7d5f-ab9b-de88b9804f9a"))