import hashlib
import asyncio

async def hash_email(email: str) -> str:
    if not email:
        raise ValueError('Email is required')

    loop = asyncio.get_running_loop()
    hash_object = hashlib.sha256()

    await loop.run_in_executor(None, hash_object.update, email.encode('utf-8'))

    return hash_object.hexdigest()