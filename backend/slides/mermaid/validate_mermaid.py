import os
import aiohttp
import ssl
from session_log_config import current_user_id

HEADLESS_API_URL = os.getenv('HEADLESS_API_URL')
HEADLESS_API_INTERNAL_KEY = os.getenv('HEADLESS_API_INTERNAL_KEY')  # Get the API key from environment variable

# Get the DISABLE_SSL_VERIFY value from environment variables
DISABLE_SSL_VERIFY = os.getenv('DISABLE_SSL_VERIFY', 'false').lower() == 'true'

SSL_VERIFY = not DISABLE_SSL_VERIFY

# Create an SSL context that disables verification if SSL_VERIFY is False
ssl_context = None
if not SSL_VERIFY:
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

async def validate_mermaid_diagram(diagram):
    context_user_id = current_user_id.get()
    headers = {
        'x-api-key': HEADLESS_API_INTERNAL_KEY,
        'x-user-id': context_user_id
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f'{HEADLESS_API_URL}/validate-mermaid',
            json={'diagram': diagram},
            headers=headers,
            ssl=ssl_context
        ) as response:
            result = await response.json()

    return result['valid'], result['message']