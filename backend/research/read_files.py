# research/read_files.py
import openparse
from langchain.docstore.document import Document
import re
import concurrent.futures
from dotenv import load_dotenv
from llama_index.core import SimpleDirectoryReader

load_dotenv()

def parse_other(file_path, id):
    def to_single_string(documents):
        return "".join([
            doc.page_content + "\n\n"
            for doc in documents
        ]).strip()
    
    reader = SimpleDirectoryReader(input_files=[file_path])
    documents = reader.aload_data()
    
    # convert to langchain documents
    documents = [doc.to_langchain_format() for doc in documents]
        
    # combine to one document
    source_metadata = {
        'type': "non_pdf_unstructured",
        'extraction_method': 'simple_directory_reader',
    }

    if id:
        source_metadata['id'] = id

    return Document(
        page_content=to_single_string(documents),
        metadata={
            'source': source_metadata
        }
    )
    
def parse_pdf(file_path, id):
    def clean_text(text):
        # Get rid of br
        text = text.replace("<br>", " ")
        # Get rid of newlines
        text = text.replace("\n", " ")
        # replace * ** and *** with space
        text = text.replace("*", " ")
        text = text.replace("**", " ")
        text = text.replace("***", " ")
        return text

    def get_nodes_text(nodes):
        combined_text = ""
        for node in nodes:
            cleaned_text = clean_text(node.text)
            combined_text += cleaned_text + "\n\n"
        return combined_text

    def find_missing_spaces(text, min_length=30):
        if text is None:
            raise ValueError("Text cannot be None.")
        pattern = r'\S{' + str(min_length) + ',}'
        matches = re.findall(pattern, text)
        return matches

    # first try with no ocr
    parser = openparse.DocumentParser()
    parsed_file = parser.parse(file_path, ocr=False)

    # check if the text is missing spaces
    first_3_nodes_text = get_nodes_text(parsed_file.nodes[:10])
    long_words = find_missing_spaces(first_3_nodes_text)
    num_long_words = len(long_words)

    # probably missing spaces
    # print(f"Found {num_long_words} long words in the first 10 nodes.")
    if num_long_words > 20:
        print(f"Found {num_long_words} long words in the first 10 nodes.")
        print("Missing spaces detected. Trying OCR...")
        parsed_file = parser.parse(file_path, ocr=True)
        
    # for whatever in parsed_file:
    # print({k: v[:50] + f" (len={len(v)})" if isinstance(v, str) else v for k, v in parsed_file.dict().items()})

    extracted_markdown = get_nodes_text(parsed_file.nodes)
    title = file_path.split("/")[-1].split(".")[0]
    url = f"file://{file_path}"
    file_type = file_path.split(".")[-1]

    source_metadata = {
        'title': title,
        'url': url,
        'type': file_type,
        'extraction_method': 'openparse',
    }

    if id:
        source_metadata['id'] = id

    return Document(
        page_content=extracted_markdown,
        metadata={
            'source': source_metadata
        }
    )

# async def parse_pdfs(file_paths):
#     with concurrent.futures.ProcessPoolExecutor() as executor:
#         futures = []
#         for file_path in file_paths:
#             future = executor.submit(parse_pdf, file_path)
#             futures.append(future)

#         documents = []
#         for future in concurrent.futures.as_completed(futures):
#             document = future.result()
#             documents.append(document)

#     return documents

# def main():
#     # test function
#     file_paths = [
#         "data/attention_is_all_you_need.pdf",
#         "data/cultural-differences-in-professional-help-seeking.pdf",
#         "data/7_natural_wonders.pdf",
#     ]

#     documents = parse_pdfs(file_paths)
#     for document in documents:
#         print(f"Title: {document.metadata['source']['title']}")
#         print(f"URL: {document.metadata['source']['url']}")
#         print(f"Type: {document.metadata['source']['type']}")
#         print(f"Extraction Method: {document.metadata['source']['extraction_method']}")
#         print("---")

# if __name__ == "__main__":
#     main()
