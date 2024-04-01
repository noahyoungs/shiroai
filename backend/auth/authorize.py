import asyncio

from auth.verify_jwt import verify_token
from dynamodb import get_presentation
from auth.hash_email import hash_email

async def authorize(presentationID, jwt):
    async def get_user():
        try:
            presentation = await get_presentation(presentationID, ['user'])
            if presentation:
                user = presentation['user']
                print(user)
                return user
            else:
                return None
        except TypeError:
            print(f"Presentation not found for ID: {presentationID}")
            return None

    async def verify_and_hash_email():
        try:
            email = await verify_token(jwt)
            if email:
                hashed_email = await hash_email(email)
                return hashed_email
            else:
                return None
        except Exception as e:
            print(f"Error during authentication: {str(e)}")
            return None

    user, hashed_email = await asyncio.gather(get_user(), verify_and_hash_email())

    if user is None:
        print("Invalid presentation ID")
        return False, False, None

    if hashed_email:
        if hashed_email == user:
            print("Access granted")
            return True, True, user
        else:
            print("Access denied")
            return False, True, None
    else:
        print("Invalid token")
        return False, False, None

# Test use case
async def main():
    isAuthorized, isAuthenticated = await authorize("64332c6a-1645-4c4f-b06a-502b6fbc2004", "eyJhbGciOiJkaXIiLCJlbmMiOiJBMjU2R0NNIn0..9MTEsLc5tYlMY1hx.0mHqg4he5he8zt71g0GN0VoVtHBWO2rDcQiNWUJuLSDhtfOZIaBkMIhGXe-Vb9FvZvfV6LapkWDln2MHlcK0ixCcYPxPxWu0dVa3afo-bL1JYlHi0T1tFZ5e8350yTmlttGtti7gZgn-Taa6m1LdG-w6J2iYTqGBpwE8njo57aKTH1Hh1mSYSJUvGVa1ittEJWXVOLTpxotUZUfB-fEW-VBnVsDRN6Pm3lEPX4On.L1xkCoMCDhzvVDkwsnQCHQ")
    print(f"isAuthorized: {isAuthorized}")
    print(f"isAuthenticated: {isAuthenticated}")

if __name__ == "__main__":
    asyncio.run(main())