import http.cookies
from auth.verify_jwt import verify_token_get_user_id
import os 

async def authorize(cookie_str, handle_refusal=None):
    
    session_token_name = os.environ.get("SESSION_TOKEN_NAME")

    # Load cookies from the incoming request
    cookies = http.cookies.SimpleCookie()
    cookies.load(cookie_str)

    # Check if the session token cookie is present
    if cookies.get(session_token_name) is None:
        if handle_refusal:
            await handle_refusal(401, "Authorization error: Access token not found. (Cookie not found) Please try logging out and logging back in.")
        return None

    accessToken = cookies.get(session_token_name).value

    if not accessToken:
        if handle_refusal:
            await handle_refusal(400, "Authorization error: Access token not found. (No cookie value) Please try logging out and logging back in.")
        return None

    # Validate access token and get user ID
    try:
        user_id = await verify_token_get_user_id(accessToken)
        return user_id
    except Exception as e:
        if handle_refusal:
            await handle_refusal(403, f"Authorization error: {e} (Access token invalid) Please try logging out and logging back in.")
        return None