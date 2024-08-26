import os
import aiohttp
import ssl

HEADLESS_API_PATH = os.getenv('HEADLESS_API_PATH')
SSL_VERIFY = False  # Set to True to enable SSL verification, False to disable

# Create an SSL context that disables verification if SSL_VERIFY is False
ssl_context = None
if not SSL_VERIFY:
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

async def validate_mermaid_diagram(diagram):
    async with aiohttp.ClientSession() as session:
        async with session.post(f'{HEADLESS_API_PATH}/validate-mermaid', json={'diagram': diagram}, ssl=ssl_context) as response:
            result = await response.json()

    return result['valid'], result['message']
