import os
import aiohttp

HEADLESS_API_PATH = os.getenv('HEADLESS_API_PATH')

async def validate_mermaid_diagram(diagram):
    async with aiohttp.ClientSession() as session:
        async with session.post(f'{HEADLESS_API_PATH}/validate-mermaid', json={'diagram': diagram}) as response:
            result = await response.json()

    return result['valid'], result['message']
