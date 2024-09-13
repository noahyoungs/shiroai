import openai_multi_tool_use_parallel_patch
from portkey_ai import AsyncPortkey
import os
from openai import AsyncOpenAI
from portkey_ai import PORTKEY_GATEWAY_URL, createHeaders


# Client for Chat Interface (Uses Function Calling)
chat_client = AsyncOpenAI(
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


# Client for Research Q&A
perplexity_client = AsyncPortkey(
    virtual_key="perplexity-de187f",
    api_key=os.getenv("PORTKEY_API_KEY"),
    config={
            "cache": {"mode": "simple"},
            "retry": {"attempts": 3}
            }
)
   
# Client for Content Generations (Uses XML Tags)

content_gen_client = AsyncPortkey(
    virtual_key="anthropic-b4a29a",
    config={
        "cache": {"mode": "simple"},
        "retry": {"attempts": 5,
                  "on_status_codes": [429, 500, 502, 503, 504, 424],
                  }
            },
)

content_gen_model = "claude-3-haiku-20240307"