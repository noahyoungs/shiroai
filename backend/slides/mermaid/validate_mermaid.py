import os
import aiohttp
import ssl

HEADLESS_API_PATH = os.getenv('HEADLESS_API_PATH')
HEADLESS_API_INTERNAL_KEY = os.getenv('HEADLESS_API_INTERNAL_KEY')  # Get the API key from environment variable
SSL_VERIFY = False  # Set to True to enable SSL verification, False to disable

# Create an SSL context that disables verification if SSL_VERIFY is False
ssl_context = None
if not SSL_VERIFY:
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

async def validate_mermaid_diagram(diagram):
    headers = {'x-api-key': HEADLESS_API_INTERNAL_KEY}  # Include the API key in the headers
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f'{HEADLESS_API_PATH}/validate-mermaid',
            json={'diagram': diagram},
            headers=headers,  # Pass headers with the API key
            ssl=ssl_context
        ) as response:
            result = await response.json()

    return result['valid'], result['message']