# %%
from s3 import get_object
from portkey_custom_langchain import CustomPortkeyLLM, CustomPortkeyChatModel
from dynamodb_service import update_items_with_user

from llama_index.core import SimpleDirectoryReader
from llama_index.readers.web import MainContentExtractorReader
from llama_index.readers.web import ReadabilityWebPageReader

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAI
from langchain.chains import MapReduceDocumentsChain, ReduceDocumentsChain
from langchain.chains.combine_documents.stuff import StuffDocumentsChain
from langchain.chains.llm import LLMChain
from langchain_core.prompts import PromptTemplate
from langchain_openai import OpenAIEmbeddings

import re
import os
import io
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
import asyncio
import nest_asyncio
import concurrent.futures
from s3fs import S3FileSystem
import asyncio
import time

from session_log_config import get_child_logger
import logging
import os

# Create a logger for this file
logger = get_child_logger(os.path.abspath(__file__), level=logging.INFO)

from portkey_ai import createHeaders, PORTKEY_GATEWAY_URL
from portkey_ai import Portkey, AsyncPortkey

from dotenv import load_dotenv
load_dotenv()

# for token counting
openai = OpenAI(temperature=0)

dumb_model = "anthropic.claude-3-haiku-20240307-v1:0"
smart_model = "anthropic.claude-3-haiku-20240307-v1:0"
portkey_trace = None

portkey_client = Portkey(
    virtual_key="aldeo-portkey-b-5cf75f",
    trace_id=portkey_trace,
    config={
            "cache": {"mode": "simple"},
            "retry": {"attempts": 3}
                },
)

async_portkey_client = AsyncPortkey(
    virtual_key="aldeo-portkey-b-5cf75f",
    trace_id=portkey_trace,
    config={
            "cache": {"mode": "simple"},
            "retry": {"attempts": 3}
                },
)

mistral7b = CustomPortkeyLLM(
    client=portkey_client,
    async_client=async_portkey_client,
    model=dumb_model,
    max_tokens=500,
)

chatMistral7b = CustomPortkeyChatModel(
    client=portkey_client,
    async_client=async_portkey_client,
    model=dumb_model,
    max_tokens=500,
)

chatHaiku = CustomPortkeyChatModel(
    client=portkey_client,
    async_client=async_portkey_client,
    model=smart_model,
    max_tokens=500,
)


def analyze(documents):
    total_characters = sum([len(doc.page_content) for doc in documents])
    total_tokens = openai.get_num_tokens(to_single_string(documents))
    logger.debug(f"Analyzed documents: {len(documents)} docs, {total_tokens} tokens, {total_characters} characters")
    return total_tokens


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


def get_first_sentence(text):
    sentences = re.split(r'(?<=[.!?])\s+', text)
    return sentences[0].strip() if sentences else ""


def split_documents_by_chars(documents, chars):
    text_splitter = RecursiveCharacterTextSplitter(
        separators=["\n\n", "\n", "\t", " ", ""], chunk_size=chars, chunk_overlap=100
    )
    split_docs = text_splitter.create_documents([to_single_string(documents)])
    analyze(split_docs)
    return split_docs


async def summarize_short(documents):
    prompt = f"""Here is the text to summarize:

<text>
{to_single_string(documents)}
</text>

Please summarize the above text in one concise, descriptive sentence. When writing the summary,
refer to the text as "This source".

One Sentence Summary:
This source"""

    logger.info(f"Summarizing short document of {len(documents)} docs")
    response = (await mistral7b.ainvoke(prompt, max_tokens=250)).strip()
    cleaned = response[0].lower() + response[1:]
    if not cleaned.lower().startswith("this source"):
        cleaned = f"This source {cleaned}"
    cleaned = cleaned[0].upper() + cleaned[1:]
    return cleaned


# %%
async def summarize_medium(documents):

    map_template = """The following is a section of text extracted from a document:
    <section>
    {docs}
    </section>
    Describe this section of the text and the main themes in a few sentences.
    Helpful Answer:"""
    map_prompt = PromptTemplate.from_template(map_template)
    map_chain = LLMChain(llm=chatMistral7b, prompt=map_prompt)

    claude_final_reduce_template = """I broke up a long source document into sections and summarized each section in a few sentences. Here are all the section summaries in order:

<summaries>
{docs}
</summaries>

Please read through all the summaries carefully to get an overall sense of what the full source document that all these summaries are describing is about. Write your thoughts and impressions from the summaries in a <scratchpad></scratchpad> section.

Then, based on your understanding from the summaries, write a single sentence concisely describing what you believe the overall source document is about. You must refer to this source document as "this source". Output this sentence inside <one_sentence_description></one_sentence_description> tags."""

    claude_final_reduce_prompt = PromptTemplate.from_template(
        claude_final_reduce_template)

    mistral_reduce_template = """I broke up a document into sections and summarized each section in a few sentences. Here are all the section summaries in order:

<summaries>
{docs}
</summaries>

Please read through all the summaries carefully to get an overall sense of what the full document that all these summaries are describing is about.

Then, based on your understanding from the summaries, write a few sentences concisely describing what you believe the overall source document is about.

Concise description:
"""
    mistral_reduce_prompt = PromptTemplate.from_template(
        mistral_reduce_template)

    claude_final_reduce_chain = LLMChain(
        llm=chatHaiku, prompt=claude_final_reduce_prompt)
    mistral_reduce_chain = LLMChain(
        llm=chatMistral7b, prompt=mistral_reduce_prompt)

    claude_final_combine_documents_chain = StuffDocumentsChain(
        llm_chain=claude_final_reduce_chain, document_variable_name="docs"
    )

    mistral_reduce_combine_documents_chain = StuffDocumentsChain(
        llm_chain=mistral_reduce_chain, document_variable_name="docs"
    )

    reduce_documents_chain = ReduceDocumentsChain(
        combine_documents_chain=claude_final_combine_documents_chain,
        collapse_documents_chain=mistral_reduce_combine_documents_chain,
        token_max=4000,
    )

    map_reduce_chain = MapReduceDocumentsChain(
        llm_chain=map_chain,
        reduce_documents_chain=reduce_documents_chain,
        document_variable_name="docs",
        return_intermediate_steps=False,
    )

    logger.info(f"Summarizing medium document of {len(documents)} docs")
    return extract_xml_tag_contents("one_sentence_description", (await map_reduce_chain.ainvoke(documents))["output_text"].strip())


async def summarize_long(documents):
    portkeyHeaders = createHeaders(
        provider="openai",
        api_key=os.getenv("PORTKEY_API_KEY"),
        trace_id=portkey_trace
    )
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small", dimensions=512,
                                  base_url=PORTKEY_GATEWAY_URL, default_headers=portkeyHeaders)
    vectors = await embeddings.aembed_documents([x.page_content for x in documents])

    num_clusters = 11

    with concurrent.futures.ProcessPoolExecutor() as executor:
        kmeans_future = executor.submit(
            KMeans(n_clusters=num_clusters, random_state=42).fit, vectors)
        kmeans = kmeans_future.result()

        closest_indices = []
        futures = []
        for i in range(num_clusters):
            future = executor.submit(
                np.linalg.norm, vectors - kmeans.cluster_centers_[i], axis=1)
            futures.append(future)

        for i, future in enumerate(futures):
            distances = future.result()
            closest_index = np.argmin(distances)
            closest_indices.append(closest_index)

    selected_indices = sorted(closest_indices)
    selected_docs = [documents[doc] for doc in selected_indices]

    analyze(selected_docs)

    map_template = """The following is a section of text extracted from a document:

    <section>
    {docs}
    </section>

    Describe this section of the text and the main themes in a few sentences.

    Helpful Answer:"""

    map_prompt = PromptTemplate.from_template(map_template)
    map_chain = LLMChain(llm=chatMistral7b, prompt=map_prompt)

    claude_final_reduce_template = """The following are summaries of some key sections from the source document, capturing the main points and themes:

    <summaries>
    {docs}
    </summaries>

    Please read through these summaries carefully to understand the central ideas and topics covered in the source document. Write your thoughts and impressions from the summaries in a <scratchpad></scratchpad> section.

    Then, based on your understanding from these summaries, write a single sentence concisely describing what the overall source document is about. You must refer to this source document as "this source". Output this sentence inside <one_sentence_description></one_sentence_description> tags."""

    claude_final_reduce_prompt = PromptTemplate.from_template(
        claude_final_reduce_template)
    claude_final_reduce_chain = LLMChain(
        llm=chatHaiku, prompt=claude_final_reduce_prompt)

    claude_final_combine_documents_chain = StuffDocumentsChain(
        llm_chain=claude_final_reduce_chain, document_variable_name="docs"
    )

    map_reduce_chain = MapReduceDocumentsChain(
        llm_chain=map_chain,
        reduce_documents_chain=claude_final_combine_documents_chain,
        document_variable_name="docs",
        return_intermediate_steps=False,
    )

    logger.info(f"Summarizing long document of {len(documents)} docs")
    return extract_xml_tag_contents("one_sentence_description", (await map_reduce_chain.ainvoke(selected_docs))["output_text"].strip())


async def summarize_tabular_file(file_path):
    file_data = await get_object(file_path)

    if file_data is None:
        logger.error(f"Failed to retrieve file '{file_path}' from S3")
        return None

    file_like = io.BytesIO(file_data)

    if file_path.endswith('.csv'):
        df = pd.read_csv(file_like)
    elif file_path.endswith('.xlsx') or file_path.endswith('.xls'):
        df = pd.read_excel(file_like)
    elif file_path.endswith('.tsv'):
        df = pd.read_csv(file_like, sep='\t')
    else:
        logger.error("Unsupported file format")
        return None

    logger.info(f"Summarizing tabular file: {file_path} ({df.shape[0]} rows, {df.shape[1]} cols)")
    
    prompt = f"""I will provide you with some information about a spreadsheet. Your task is to carefully examine this information and provide a brief one-sentence summary describing the contents and nature of the spreadsheet.

    Here is the output of the number of rows and columns:
    <df_shape>
    {df.shape}
    </df_shape>

    Here is a sample of the data from the top of the spreadsheet:
    <df_head>
    {df.head()}
    </df_head>

    Here is a sample of the data from the bottom of the spreadsheet:
    <df_tail>
    {df.tail()}
    </df_tail>

    Here is information about the columns and data types:
    <df_info>
    {df.info()}
    </df_info>

    Here is information about the completeness of the data (number of missing values per column):
    <df_isnull_sum>
    {df.isnull().sum()}
    </df_isnull_sum>

    And finally, here are summary statistics for numerical columns:
    <df_describe>
    {df.describe()}
    </df_describe>

    Please provide a one-sentence summary of the spreadsheet based on the provided information in a <summary></summary>, focusing on the overall contents and nature of the data. Begin your response with "This spreadsheet".
    """

    response = (await chatHaiku.ainvoke(prompt, max_tokens=1000)).content.strip()
    return extract_xml_tag_contents("summary", response).strip()


async def load_web_source(url):
    scrape_success = False
    documents = None

    try:
        loader1 = MainContentExtractorReader()
        documents = loader1.load_langchain_documents(urls=[url])
        if len(to_single_string(documents)) < 1200:
            logger.warning(f"Small amount of text extracted from MainContentExtractorReader for URL: {url}")
        else:
            scrape_success = True
    except Exception as e:
        logger.error(f"Error scraping using MainContentExtractorReader: {e}")

    if not scrape_success:
        try:
            loader2 = ReadabilityWebPageReader(wait_until="networkidle")
            documents = await loader2.async_load_data(url=url)
            documents = [
                doc.to_langchain_format()
                for doc in documents
            ]
            if len(to_single_string(documents)) < 1200:
                logger.warning(f"Small amount of text extracted from ReadabilityWebPageReader for URL: {url}")
            else:
                scrape_success = True
        except Exception as e:
            logger.error(f"Error scraping using ReadabilityWebPageReader: {e}")

    if not scrape_success:
        return None

    logger.info(f"Successfully loaded web source from URL: {url} with {len(documents)} documents")
    return documents


def load_file_source(filepath):
    bucket_name = os.getenv("SOURCES_BUCKET_NAME")
    s3_filepath = f"{bucket_name}/{filepath}"
    s3 = S3FileSystem(key=os.getenv("AWS_ACCESS_KEY_ID"),
                      secret=os.getenv("AWS_SECRET_ACCESS_KEY")
                      )
    reader = SimpleDirectoryReader(fs=s3, input_files=[s3_filepath])
    documents = reader.load_data()
    documents = [doc.to_langchain_format() for doc in documents]
    logger.info(f"Loaded file source: {filepath} with {len(documents)} documents")
    return documents


async def load_file_source_async(filepath):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(load_file_source, filepath)
        result = await asyncio.wrap_future(future)
    
    return result


async def summarize_documents(documents):
    """
   Summarize a source file based on its type and update the source with the generated summary.

   Args:
       source (dict): A dictionary representing the source file to be summarized.
           The dictionary must contain an 'source_id' field and a 'type' field indicating the file type.
       presentation_id (str): The ID of the presentation associated with the source file.
       document (Optional[Document]): A Document object representing the loaded source file.
           This argument is required for non-tabular source files.
       callback (Optional[callable]): An optional asynchronous callback function to be executed
           after the source is summarized and updated.

   Returns:
       str: The generated summary of the source file.

   Raises:
       ValueError: If the source dictionary does not have an 'source_id' field or if the document argument
           is not provided for non-tabular source files.

   Description:
       This function summarizes a source file based on its type (tabular or non-tabular) and updates
       the corresponding source entry in the database with the generated summary. The function
       determines the summarization method based on the file type:
       - For tabular files (CSV, XLS, XLSX, TSV), it calls the `summarize_tabular_file` function.
       - For non-tabular files, it requires a `document` argument and calls the `summarize_documents`
         function.

       After generating the summary, the function updates the source entry in dynamodb, associating the summary with the source.

       If a `callback` function is provided, it is executed asynchronously after the source is
       summarized and updated.

   Example:
       source = {"id": "source123", "type": "csv", "s3_filepath": "data.csv"}
       summary = await summarize_source(source, "presentation456")
       print(summary)
   """
    try:
        tokens = analyze(documents)

        if tokens <= 5000:
            logger.info(f"Summarizing short document with {tokens} tokens")
            summary = await summarize_short(documents)
        elif tokens <= 50000:
            logger.info(f"Summarizing medium document with {tokens} tokens")
            split_docs = split_documents_by_chars(documents, 10000)
            summary = await summarize_medium(split_docs)
        else:
            logger.info(f"Summarizing long document with {tokens} tokens")
            split_docs = split_documents_by_chars(documents, 10000)
            summary = await summarize_long(split_docs)
        return summary
    except Exception as e:
        logger.warning("Error summarizing documents: %s", str(e))
        return f"Shiro was able to read this document, but could not generate a summary."


async def summarize_source(source, presentation_id, document=None, callback=None):
    if source.get("source_id", None) is None:
        raise ValueError("Source must have an 'source_id' field.")

    if source["type"] in ["csv", "xls", "xlsx", "tsv"]:
        s3_path = f"{presentation_id}/{source['s3_filepath']}"
        summary = await summarize_tabular_file(s3_path)
    else:
        if document is None:
            raise ValueError("Document must be provided for non-tabular sources.")
        summary = await summarize_documents([document])
    
    await update_items_with_user('source', [{'presentation_id': presentation_id, 'source_id': source['source_id'], 'summary': summary}])
    
    logger.info(f"Finished summarizing source {source['source_id']} for presentation {presentation_id}")
    
    if callback:
        await callback()
    return summary


async def test_tabular():
    path = "fb18a73f-80a8-483a-8cfe-150c9fc58049/wonders_of_world.csv"
    summary = await summarize_tabular_file(path)
    logger.info(f"Tabular file summary: {summary}")


async def test_s3_file():
    path = "018e9dc7-2584-7c66-a45e-889ac6e5aece/Japan.pdf"
    documents = await load_file_source_async(path)
    summary = await summarize_documents(documents)
    logger.info(f"S3 file summary: {summary}")


async def test_web_source():
    url = "https://www.blueprintcreativegroup.com/generative-ai-and-its-ethical-implications-navigating-the-future-of-artificial-intelligence"
    documents = await load_web_source(url)
    summary = await summarize_documents(documents)
    logger.info(f"Web source summary: {summary}")


if __name__ == "__main__":
    nest_asyncio.apply()
    asyncio.run(test_web_source())