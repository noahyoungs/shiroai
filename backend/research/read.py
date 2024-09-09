# read_source.py
from s3 import download_file_to_temp, upload_model_to_s3
from research.read_files import parse_pdf, parse_other
from research.read_url import parse_url
from dynamodb import update_source
from research.summarize import summarize_source
import aiohttp
import tempfile 
import asyncio

tabluar_file_types = ['xlsx', 'xls', 'csv', 'tsv']

async def read_source(source, presentation_id):
    """
    Read and process a source file based on its type.

    Args:
        source (dict): A dictionary representing the source file to be read.
                       The dictionary must contain an 'id' field and a 'type' field indicating the file type.
        presentation_id (str): The ID of the presentation associated with the source file.

    Returns:
        tuple: A tuple containing two elements:
               - Document: The parsed Document object representing the source file.
               - int: The character count of the parsed document.

    Raises:
        AssertionError: If the source dictionary does not have an 'id' field.
        ValueError: If the source type is unsupported (e.g., a tabular file type).

    Description:
        This function reads and processes a source file based on its type. It supports the following types:
        - 'web': Parses the source URL using the `parse_url` function and uploads the parsed document to S3.
        - Tabular file types (not supported): Raises a ValueError indicating unsupported file type.
        - Other file types: Downloads the source file from S3 to a temporary file, parses it using the
          appropriate parsing function (`parse_pdf` or `parse_other`), and uploads the parsed document to S3.
        After processing the source file, the function updates the source entry in the database with the
        path to the uploaded whole document using the `update_source` function.
        The function returns the parsed Document object and the character count of the document.
    """
    assert source.get("id", None) is not None

    if source['type'] == 'web':
        url = source['url']
        # if url ends with .pdf
        if url.endswith('.pdf'):
            async with aiohttp.ClientSession() as session:
                async with session.get(url, verify_ssl=False) as response:
                    if response.status == 200:
                        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                            temp_file.write(await response.read())
                            temp_file.seek(0)
                            document = parse_pdf(temp_file.name, source['id'])
                            object_key = f"{presentation_id}/{source['id']}_whole_document.json"
                            await upload_model_to_s3(document, object_key)
                            await update_source(presentation_id, source["id"], whole_document_path=object_key)
                            temp_file.close()
                            return document, len(document.page_content)
                    else:
                        print(f"Error downloading PDF file from URL: {url}")
                        return None, 0
        else:
            try:
                document = await asyncio.wait_for(parse_url(url, source['id'], 2000), timeout=15)
            except asyncio.TimeoutError:
                print(f"Timeout occurred while parsing URL: {url}")
                document = None
            except Exception as e:
                print(f"Error occurred while parsing URL: {url}")
                print(f"Error details: {str(e)}")
                document = None
    
            if document:
                object_key = f"{presentation_id}/{source['id']}_whole_document.json"
                await upload_model_to_s3(document, object_key)
                await update_source(presentation_id, source["id"], whole_document_path=object_key)
                return document, len(document.page_content)
            else:
                return None, 0

    elif source['type'] in tabluar_file_types:
        raise ValueError(f"Unsupported file type: {source['type']}")

    else:
        s3_filepath = f"{presentation_id}/{source['s3_filepath']}"
        with await download_file_to_temp(s3_filepath) as temp_file:
            if source['type'] == 'pdf':
                document = parse_pdf(temp_file.name, source['id'])
            else:
                document = parse_other(temp_file.name, source["id"])
            object_key = f"{presentation_id}/{source['id']}_whole_document.json"
            await upload_model_to_s3(document, object_key)
            await update_source(presentation_id, source["id"], whole_document_path=object_key)
            return document, len(document.page_content)
    

async def read_and_summarize_source(source, presentation_id, callback):
    """
    Read, process, and summarize a source file based on its type.

    Args:
        source (dict): A dictionary representing the source file to be read and summarized.
            The dictionary must contain an 'id' field and a 'type' field indicating the file type.
        presentation_id (str): The ID of the presentation associated with the source file.
        callback (callable): An asynchronous callback function to be executed after the source is summarized.

    Returns:
        int: The character count of the source file.

    Raises:
        ValueError: If the source dictionary does not have an 'id' field or a 'type' field.

    Description:
        This function reads, processes, and summarizes a source file based on its type. It handles two
        categories of source types:
        - Tabular file types: Updates the source entry in the database with a temporary summary indicating
          that the file is being summarized, and then passes the callback function to the `summarize_source`
          function to be executed after the source is summarized. The callback function is also executed
          immediately after updating the source entry.
        - Unstructured file types: Reads the source file using the `read_source` function, updates the source
          entry with a temporary summary indicating the character count and that the source is being summarized,
          and then passes the callback function to the `summarize_source` function to be executed after the
          source is summarized. If the source cannot be read, the callback function is executed immediately.

        The function raises a ValueError if the source dictionary does not have an 'id' field or a 'type' field.
        The reading part of the function is awaited, and the character count of the source file is returned.
        The summarizing part is run asynchronously using `asyncio.create_task`, and the provided callback
        function is executed after the source is summarized or if the source cannot be read.
    """
    if source.get("id", None) is None:
        raise ValueError("Source does not have an id")
    if source.get("type", None) is None:
        raise ValueError("Source does not have a type")

    if source.get("type", None) in tabluar_file_types:
        # tabular file
        temp_summary = "Shiro is summarizing this tabular file..."
        await update_source(presentation_id, source["id"], summary=temp_summary, char_count=1)
        # pass the callback to summarize_source using create_task
        asyncio.create_task(summarize_source(source, presentation_id, None, callback))
        callback()
        return 1
    else:
        # unstructured file or web source
        document, char_count = await read_source(source, presentation_id)
        if document:
            temp_summary = f"Shiro read {char_count} characters and is summarizing the source..."
            await update_source(presentation_id, source["id"], summary=temp_summary, char_count=char_count)
            # pass the callback to summarize_source using create_task
            asyncio.create_task(summarize_source(source, presentation_id, document, callback))
        else:
            temp_summary = "Shiro could not read enough text from this source, so it will be ignored."
            await update_source(presentation_id, source["id"], summary=temp_summary, char_count=0)
        callback()
        return char_count
            