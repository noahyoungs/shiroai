import asyncio

from auth.verify_jwt import verify_token_get_user_id
from dynamodb import get_presentation

async def authorize(presentation_id, jwt):
    async def get_db_user():
        try:
            presentation = await get_presentation(presentation_id, ['user'])
            if presentation:
                user = presentation['user']
                print(user)
                return user
            else:
                return None
        except TypeError:
            print(f"Presentation not found for ID: {presentation_id}")
            return None

    async def try_verify_jwt():
        try:
            return await verify_token_get_user_id(jwt)
        except Exception as e:
            print('Error verifying token:', e)
            return None

    db_user, token_user_id = await asyncio.gather(get_db_user(), try_verify_jwt())

    if db_user is None:
        print("Invalid presentation ID (from db)")
        return False, False, None

    if token_user_id:
        if token_user_id == db_user:
            print("Access granted")
            return True, True, db_user
        else:
            print("Access denied")
            return False, True, None
    else:
        print("Invalid token")
        return False, False, None

