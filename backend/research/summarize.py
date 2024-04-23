# %%
from s3 import get_object
from portkey_custom_langchain import CustomPortkeyLLM, CustomPortkeyChatModel
from dynamodb import update_source

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


from portkey_ai import createHeaders, PORTKEY_GATEWAY_URL
from portkey_ai import Portkey, AsyncPortkey

from dotenv import load_dotenv
load_dotenv()

# for token counting
openai = OpenAI(temperature=0)

mistral7b_model = "mistral.mistral-7b-instruct-v0:2"
haiku_model = "anthropic.claude-3-haiku-20240307-v1:0"
portkey_trace = None

portkey_client = Portkey(
    virtual_key="aldeo-portkey-b-5cf75f",
    trace_id=portkey_trace
)

async_portkey_client = AsyncPortkey(
    virtual_key="aldeo-portkey-b-5cf75f",
    trace_id=portkey_trace
)

mistral7b = CustomPortkeyLLM(
    client=portkey_client,
    async_client=async_portkey_client,
    model=mistral7b_model,
)

chatMistral7b = CustomPortkeyChatModel(
    client=portkey_client,
    async_client=async_portkey_client,
    model=mistral7b_model,
)

chatHaiku = CustomPortkeyChatModel(
    client=portkey_client,
    async_client=async_portkey_client,
    model=haiku_model,
    max_tokens=1000,
)


def analyze(documents):
    total_characters = sum([len(doc.page_content) for doc in documents])
    total_tokens = openai.get_num_tokens(to_single_string(documents))
    # print(f"Total tokens: {total_tokens}")
    # print(f"Total characters: {total_characters}")
    # print(f"Number of documents: {len(documents)}")
    # print(f"Average length: {total_characters / len(documents)}")

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
    # Split the text into sentences using regular expression
    sentences = re.split(r'(?<=[.!?])\s+', text)
    
    if len(sentences) > 0:
        # Return the first sentence
        return sentences[0].strip()
    else:
        # Return an empty string if no sentence is found
        return ""

def split_documents_by_chars(documents, chars):
    text_splitter = RecursiveCharacterTextSplitter(
        separators=["\n\n", "\n", "\t", " ", ""], chunk_size=chars, chunk_overlap=100
    )
    split_docs = text_splitter.create_documents([to_single_string(documents)])

    # print(f"-- After split --")
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

    response = (await mistral7b.ainvoke(prompt, max_tokens=250)).strip()
    cleaned = response[0].lower() + response[1:]
    if not cleaned.lower().startswith("this source"):
        cleaned = f"This source {cleaned}"
    # capitalize first letter
    cleaned = cleaned[0].upper() + cleaned[1:]
    return cleaned


# %%
async def summarize_medium(documents):

    # Map
    map_template = """The following is a section of text extracted from a document:
    <section>
    {docs}
    </section>
    Describe this section of the text and the main themes in a few sentences.
    Helpful Answer:"""
    map_prompt = PromptTemplate.from_template(map_template)
    map_chain = LLMChain(llm=chatMistral7b, prompt=map_prompt)

    # Reduce
    claude_final_reduce_template = """I broke up a long source document into sections and summarized each section in a few sentences. Here are all the section summaries in order:

<summaries>
{docs}
</summaries>

Please read through all the summaries carefully to get an overall sense of what the full source document that all these summaries are describing is about. Write your thoughts and impressions from the summaries in a <scratchpad></scratchpad> section.

Then, based on your understanding from the summaries, write a single sentence concisely describing what you believe the overall source document is about. You must refer to this source document as "this source". Output this sentence inside <one_sentence_description></one_sentence_description> tags."""

    mistral_reduce_template = """I broke up a document into sections and summarized each section in a few sentences. Here are all the section summaries in order:

<summaries>
{docs}
</summaries>

Please read through all the summaries carefully to get an overall sense of what the full document that all these summaries are describing is about.

Then, based on your understanding from the summaries, write a few sentences concisely describing what you believe the overall source document is about.

Concise description:
"""
    claude_final_reduce_prompt = PromptTemplate.from_template(
        claude_final_reduce_template)
    mistral_reduce_prompt = PromptTemplate.from_template(
        mistral_reduce_template)

    claude_final_reduce_chain = LLMChain(
        llm=chatHaiku, prompt=claude_final_reduce_prompt)
    mistral_reduce_chain = LLMChain(
        llm=chatMistral7b, prompt=mistral_reduce_prompt)

    # Takes a list of documents, combines them into a single string, and passes this to an LLMChain

    claude_final_combine_documents_chain = StuffDocumentsChain(
        llm_chain=claude_final_reduce_chain, document_variable_name="docs"
    )

    mistral_reduce_combine_documents_chain = StuffDocumentsChain(
        llm_chain=mistral_reduce_chain, document_variable_name="docs"
    )

    # Combines and iteratively reduces the mapped documents
    reduce_documents_chain = ReduceDocumentsChain(
        # This is final chain that is called.
        combine_documents_chain=claude_final_combine_documents_chain,
        # If documents exceed context for `StuffDocumentsChain`
        collapse_documents_chain=mistral_reduce_combine_documents_chain,
        # The maximum number of tokens to group documents into.
        token_max=4000,
    )

    # Combining documents by mapping a chain over them, then combining results
    map_reduce_chain = MapReduceDocumentsChain(
        # Map chain
        llm_chain=map_chain,
        # Reduce chain
        reduce_documents_chain=reduce_documents_chain,
        # The variable name in the llm_chain to put the documents in
        document_variable_name="docs",
        # Return the results of the map steps in the output
        return_intermediate_steps=False,
    )

    return extract_xml_tag_contents("one_sentence_description", (await map_reduce_chain.ainvoke(documents))["output_text"].strip())


async def summarize_long(documents):
    # vectorize
    portkeyHeaders = createHeaders(
        provider="openai",
        api_key=os.getenv("PORTKEY_API_KEY"),
        trace_id=portkey_trace
    )
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small", dimensions=512,
                                  base_url=PORTKEY_GATEWAY_URL, default_headers=portkeyHeaders)
    vectors = await embeddings.aembed_documents([x.page_content for x in documents])

    # Assuming 'embeddings' is a list or array of 1536-dimensional embeddings
    # Choose the number of clusters, this can be adjusted based on the book's content.
    # I played around and found ~10 was the best.
    # Usually if you have 10 passages from a book you can tell what it's about
    num_clusters = 11

    with concurrent.futures.ProcessPoolExecutor() as executor:
        # Perform K-means clustering
        kmeans_future = executor.submit(
            KMeans(n_clusters=num_clusters, random_state=42).fit, vectors)
        kmeans = kmeans_future.result()

        # Find the closest embeddings to the centroids
        # Create an empty list that will hold your closest points
        closest_indices = []

        # Loop through the number of clusters you have
        futures = []
        for i in range(num_clusters):
            future = executor.submit(
                np.linalg.norm, vectors - kmeans.cluster_centers_[i], axis=1)
            futures.append(future)

        for i, future in enumerate(futures):
            distances = future.result()
            # Find the list position of the closest one (using argmin to find the smallest distance)
            closest_index = np.argmin(distances)
            # Append that position to your closest indices list
            closest_indices.append(closest_index)

    selected_indices = sorted(closest_indices)
    selected_docs = [documents[doc] for doc in selected_indices]

    # print("-- After k means clustering filter --")
    analyze(selected_docs)

    # Map
    map_template = """The following is a section of text extracted from a document:

    <section>
    {docs}
    </section>

    Describe this section of the text and the main themes in a few sentences.

    Helpful Answer:"""

    map_prompt = PromptTemplate.from_template(map_template)
    map_chain = LLMChain(llm=chatMistral7b, prompt=map_prompt)

    # Reduce
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

    # Takes a list of documents, combines them into a single string, and passes this to an LLMChain
    claude_final_combine_documents_chain = StuffDocumentsChain(
        llm_chain=claude_final_reduce_chain, document_variable_name="docs"
    )

    # Combining documents by mapping a chain over them, then combining results
    map_reduce_chain = MapReduceDocumentsChain(
        # Map chain
        llm_chain=map_chain,
        # Reduce chain
        reduce_documents_chain=claude_final_combine_documents_chain,
        # The variable name in the llm_chain to put the documents in
        document_variable_name="docs",
        # Return the results of the map steps in the output
        return_intermediate_steps=False,
    )

    return extract_xml_tag_contents("one_sentence_description", (await map_reduce_chain.ainvoke(selected_docs))["output_text"].strip())


async def summarize_tabular_file(file_path):
    # Get the file data from S3
    file_data = await get_object(file_path)

    if file_data is None:
        print(f"Failed to retrieve file '{file_path}' from S3.")
        return None

    # Create a file-like object from the file data
    file_like = io.BytesIO(file_data)

    # Read the file into a DataFrame based on the file extension
    if file_path.endswith('.csv'):
        df = pd.read_csv(file_like)
    elif file_path.endswith('.xlsx') or file_path.endswith('.xls'):
        df = pd.read_excel(file_like)
    elif file_path.endswith('.tsv'):
        df = pd.read_csv(file_like, sep='\t')
    else:
        print("Unsupported file format. Please provide a CSV, XLS, XLSX, or TSV file.")
        return None

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
            print("Small amount of text extracted from MainContentExtractorReader.")
        else:
            scrape_success = True
    except Exception as e:
        print(f"Error scraping using MainContentExtractorReader: {e}")

    if not scrape_success:
        try:
            loader2 = ReadabilityWebPageReader(wait_until="networkidle")
            documents = await loader2.async_load_data(url=url)
            documents = [
                doc.to_langchain_format()
                for doc in documents
            ]
            if len(to_single_string(documents)) < 1200:
                print("Small amount of text extracted from ReadabilityWebPageReader.")
            else:
                scrape_success = True
        except Exception as e:
            print(f"Error scraping using ReadabilityWebPageReader: {e}")

    if not scrape_success:
        return None

    # print(f"Extracted Text:\n{to_single_string(documents)}")

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
    return documents

async def load_file_source_async(filepath):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(load_file_source, filepath)
        result = await asyncio.wrap_future(future)
    
    return result


async def summarize_documents(documents):
    # print("-- Before split --")
    tokens = analyze(documents)

    if tokens <= 5000:
        print("This is a short document so we will summarize it in one go.")
        # Short so we sumamrize in one go
        summary = await summarize_short(documents)
    elif tokens <= 50000:
        print("This is a medium document so we will use map reduce.")
        # Medium length so recursive map reduce
        split_docs = split_documents_by_chars(documents, 10000)
        summary = await summarize_medium(split_docs)
    else:
        # Long so vectorize and summarize key chunks
        print("This is a long document so we will use clustering.")
        split_docs = split_documents_by_chars(documents, 10000)
        summary = await summarize_long(split_docs)

    return summary


async def summarize_source(source, presentationID, document=None, callback=None):
    """
   Summarize a source file based on its type and update the source with the generated summary.

   Args:
       source (dict): A dictionary representing the source file to be summarized.
           The dictionary must contain an 'id' field and a 'type' field indicating the file type.
       presentationID (str): The ID of the presentation associated with the source file.
       document (Optional[Document]): A Document object representing the loaded source file.
           This argument is required for non-tabular source files.
       callback (Optional[callable]): An optional asynchronous callback function to be executed
           after the source is summarized and updated.

   Returns:
       str: The generated summary of the source file.

   Raises:
       ValueError: If the source dictionary does not have an 'id' field or if the document argument
           is not provided for non-tabular source files.

   Description:
       This function summarizes a source file based on its type (tabular or non-tabular) and updates
       the corresponding source entry in the database with the generated summary. The function
       determines the summarization method based on the file type:
       - For tabular files (CSV, XLS, XLSX, TSV), it calls the `summarize_tabular_file` function.
       - For non-tabular files, it requires a `document` argument and calls the `summarize_documents`
         function.

       After generating the summary, the function updates the source entry in the database using the
       `update_source` function, associating the summary with the source.

       If a `callback` function is provided, it is executed asynchronously after the source is
       summarized and updated.

   Example:
       source = {"id": "source123", "type": "csv", "s3_filepath": "data.csv"}
       summary = await summarize_source(source, "presentation456")
       print(summary)
   """
    # print(f"Summarizing source {source}...")
    
    if source.get("id", None) is None:
        raise ValueError("Source must have an 'id' field.")

    if source["type"] in ["csv", "xls", "xlsx", "tsv"]:
        s3_path = f"{presentationID}/{source['s3_filepath']}"
        summary = await summarize_tabular_file(s3_path)
    else:
        if document is None:
            raise ValueError("Document must be provided for non-tabular sources.")
        summary = await summarize_documents([document])
    
    await update_source(presentationID, source["id"], summary=summary)
    
    print("Finished summarizing one source.")
    # run callback
    if callback:
        await callback()
    return summary


async def test_tabular():
    path = "fb18a73f-80a8-483a-8cfe-150c9fc58049/wonders_of_world.csv"
    summary = await summarize_tabular_file(path)
    print(f"Summary: {summary}")

async def test_s3_file():
    path = "018e9dc7-2584-7c66-a45e-889ac6e5aece/Japan.pdf"
    documents = await load_file_source_async(path)
    summary = await summarize_documents(documents)
    print(f"Summary: {summary}")

async def test_web_source():
    url = "https://www.blueprintcreativegroup.com/generative-ai-and-its-ethical-implications-navigating-the-future-of-artificial-intelligence"
    documents = await load_web_source(url)
    summary = await summarize_documents(documents)
    print(f"Summary: {summary}")

if __name__ == "__main__":
    nest_asyncio.apply()
    asyncio.run(test_web_source())


# %%
