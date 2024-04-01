import openai_multi_tool_use_parallel_patch
from portkey_ai import AsyncPortkey
import os
# client = AsyncPortkey(
#     virtual_key="aldeo-portkey-41bbe0"
# )



from openai import AsyncOpenAI
from portkey_ai import PORTKEY_GATEWAY_URL, createHeaders

client = AsyncOpenAI(
    base_url=PORTKEY_GATEWAY_URL,
    default_headers=createHeaders(
        provider="openai",
        api_key=os.environ.get("PORTKEY_API_KEY"),
    )
)