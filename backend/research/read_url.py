# research/read_url.py
import asyncio
import aiohttp
from main_content_extractor import MainContentExtractor
from bs4 import BeautifulSoup
from langchain.docstore.document import Document

from playwright.async_api import async_playwright

urls = [
        "https://en.wikipedia.org/wiki/Seven_Natural_Wonders_(CNN)",
        "https://www.exoticca.com/us/blog/what-are-the-7-natural-wonders-of-the-world/",
        "https://www.sciencedirect.com/science/article/abs/pii/S0749597898928175",
        "https://www.worldatlas.com/places/the-7-natural-wonders-of-the-world.html",
        "https://www.farandwide.com/s/facts-natural-wonders-world-1d6446a483ca4288",
        "https://www.planetware.com/magic-travel-a-guide-to-the-seven-natural-wonders-of-the-world.htm",
        "https://www.analyticsvidhya.com/blog/2019/06/understanding-transformers-nlp-state-of-the-art-models/",
        "https://en.wikipedia.org/wiki/Transformer_(machine_learning_model)",
        "https://medium.com/inside-machine-learning/what-is-a-transformer-d07dd1fbec04",
        "http://jalammar.github.io/illustrated-transformer/",
        "https://ai.googleblog.com/2017/08/transformer-novel-neural-network.html",
        "https://www.roadtrips.com/blog/cultural-differences-between-japan-and-the-usa/",
        "https://www.mybucketlistevents.com/cultural-differences-between-us-and-japan/",
        "https://www.thrillist.com/travel/nation/japanese-customs-cultural-differences",
        "https://ksemoving.com/cultural-differences-usa-japan/",
        "https://www.worldometers.info/world-population/#:~:text=The%20current%20world%20population%20is,currently%20living)%20of%20the%20world.",
    ]

async def download_html(url):
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, verify_ssl=False) as response:
                html = None
                title = None
                download_method = "requests"
                if response.status == 200:
                    html = await response.text()

                    # Get the title of the webpage
                    soup = BeautifulSoup(html, 'html.parser')
                    title = soup.title.string.strip() if soup.title else "No title found"
                else:
                    download_method = "playwright"
                    # print(f"Received status code {response.status}. Trying with Playwright...")
                    async with async_playwright() as p:
                        browser = await p.chromium.launch()
                        page = await browser.new_page()
                        try:
                            await page.goto(url, wait_until='networkidle', timeout=10000)
                            html = await page.content()

                            # Get the title of the webpage
                            soup = BeautifulSoup(html, 'html.parser')
                            title = soup.title.string if soup.title else None

                            await browser.close()
                        except Exception as e:
                            print(
                                f"Failed to download HTML using requests and Playwright: {e}")
                            await browser.close()
                            return None, None, None

                if len(html) == 0:
                    print(f"HTML is empty for {url}")
                    return None, None, None
                else:
                    # print(f"HTML downloaded successfully from {url}")
                    # save html to file
                    with open("output.html", "w") as f:
                        f.write(html)
                    return title, html, download_method
        except Exception as e:
            print(f"Failed to download HTML using aiohttp: {e}")
            download_method = "playwright"
            async with async_playwright() as p:
                browser = await p.chromium.launch()
                page = await browser.new_page()
                try:
                    await page.goto(url, wait_until='networkidle', timeout=10000)
                    html = await page.content()

                    # Get the title of the webpage
                    soup = BeautifulSoup(html, 'html.parser')
                    title = soup.title.string if soup.title else None

                    await browser.close()
                except Exception as e:
                    print(
                        f"Failed to download HTML using requests and Playwright: {e}")
                    await browser.close()
                    return None, None, None

                if len(html) == 0:
                    print(f"HTML is empty for {url}")
                    return None, None, None
                else:
                    # print(f"HTML downloaded successfully from {url}")
                    # # save html to file
                    # with open("output.html", "w") as f:
                    #     f.write(html)
                    return title, html, download_method



async def scrape(url):
    title, html, download_method = await download_html(url)

    if html:
        # print(f"HTML downloaded successfully from {url}")

        extraction_method_dict = {}

        extracted_markdown = await asyncio.to_thread(
            MainContentExtractor.extract,
            html=html,
            output_format="markdown",
            ref_extraction_method=extraction_method_dict,
            bodywidth=0,
            skip_article=True,
        )

        extraction_method = extraction_method_dict.get('extraction_method', 'unknown')

        return title, extracted_markdown, extraction_method, download_method
    else:
        return None, None, None, None,

# single version of get_langchain_documents
async def parse_url(url, id, min_length=None):
    """
    Retrieves a document from a single URL and returns a langchain Document object.

    Args:
        url (str): The URL to scrape.
        min_length (int, optional): Minimum length of extracted markdown (chars). Defaults to None.

    Returns:
        Document: A langchain Document object, or None if the extraction failed or the content is too short.

    """
    title, extracted_markdown, extraction_method, download_method = await scrape(url)
    if extracted_markdown:
        if not min_length or len(extracted_markdown) >= min_length:
            source_metadata = {
                'title': title,
                'url': url,
                'type': 'web',
                'extraction_method': extraction_method,
                'download_method': download_method,
                'id': id
            }

            if id:
                source_metadata['id'] = id

            doc = Document(
                page_content=extracted_markdown,
                metadata={
                    'source': source_metadata
                }
            )
            return doc
    return None

# async def get_langchain_documents(urls, min_length=None):
#     """
#     Retrieves documents from a list of URLs and returns a list of Document objects.

#     Args:
#         urls (list): A list of URLs to scrape.
#         min_length (int, optional): Minimum length of extracted markdown (chars). Defaults to None.

#     Returns:
#         list: A list of langchain Document objects.

#     """
#     tasks = []
#     for url in urls:
#         task = asyncio.create_task(parse_url(url, min_length))
#         tasks.append(task)

#     documents = await asyncio.gather(*tasks)
#     documents = [doc for doc in documents if doc is not None]

#     return documents

        
        
        
