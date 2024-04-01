import json
import os
from typing import Any, Dict
from hkdf import Hkdf
from jose.jwe import decrypt, encrypt
from dotenv import load_dotenv
import asyncio

load_dotenv()

def __encryption_key():
    secret = os.getenv("NEXTAUTH_SECRET")
    if secret:
        return Hkdf("", bytes(secret, "utf-8")).expand(b"NextAuth.js Generated Encryption Key", 32)
    else:
        raise ValueError("NEXTAUTH_SECRET environment variable is not set.")

async def decode_jwe(__token__: str):
    loop = asyncio.get_running_loop()
    decrypted = await loop.run_in_executor(None, decrypt, __token__, __encryption_key())
    if decrypted:
        return json.loads(bytes.decode(decrypted, "utf-8"))
    else:
        return None

async def verify_token(__token__: str) -> str:
    decoded = await decode_jwe(__token__)
    if decoded:
        return decoded.get("email")
    else:
        return None