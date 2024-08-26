import openai_multi_tool_use_parallel_patch
from portkey_ai import AsyncPortkey
import os
from openai import AsyncOpenAI
from portkey_ai import PORTKEY_GATEWAY_URL, createHeaders

client = AsyncOpenAI(
    base_url=PORTKEY_GATEWAY_URL,
    default_headers=createHeaders(
        provider="openai",
        api_key=os.environ.get("PORTKEY_API_KEY"),
        config={
            "cache": {"mode": "simple"},
            "retry": {"attempts": 3}
                },
    )
)


groq_client = AsyncOpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=os.getenv("GROQ_API_KEY")
)

perplexity_client = AsyncPortkey(
    virtual_key="perplexity-de187f",
    api_key=os.getenv("PORTKEY_API_KEY"),
    config={
            "cache": {"mode": "simple"},
            "retry": {"attempts": 3}
            }
)
   