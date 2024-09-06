import json
import os
from typing import Any, Dict
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes
from jose import jwe
from dotenv import load_dotenv
import asyncio
import logging

# Create a logger specific to this module
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def get_derived_encryption_key(secret: str, salt: str) -> bytes:
    """
    Derives a 64-byte encryption key using HKDF for A256CBC-HS512.
    
    Args:
    secret (str): The secret key material (Auth.js secret).
    salt (str): The salt to use in key derivation.
    
    Returns:
    bytes: A 64-byte derived key.
    """
    logger.debug(f"Starting key derivation with salt: {salt}")

    # Define the salt for HKDF
    salt_bytes = salt.encode('utf-8')

    # Correct info string format with salt in parentheses
    info_string = f"Auth.js Generated Encryption Key ({salt})".encode('utf-8')

    # Derive a 64-byte key using HKDF for A256CBC-HS512
    hkdf = HKDF(
        algorithm=hashes.SHA256(),
        length=64,  # 64 bytes for A256CBC-HS512
        salt=salt_bytes,
        info=info_string
    )

    # Derive the key using the provided secret
    key = hkdf.derive(secret.encode('utf-8'))
    
    # Check if the derived key length is 64 bytes (512 bits)
    if len(key) != 64:
        logger.error(f"Derived key length is incorrect. Expected 64 bytes, got {len(key)} bytes.")
        raise ValueError(f"Derived key length is incorrect. Expected 64 bytes, got {len(key)} bytes.")
    
    logger.info("Key derivation successful.")
    return key

def decode_nextauth_session(token: str) -> Dict[str, Any]:
    logger.info(f"Decoding token: {token}")
    
    # Fetch the Auth.js secret and salt from the environment
    authjs_secret = os.environ.get('AUTHJS_SECRET')
    authjs_salt = os.environ.get('AUTHJS_SALT')
    
    if not authjs_secret:
        logger.error("AUTHJS_SECRET environment variable is not set.")
        raise ValueError("AUTHJS_SECRET environment variable is not set.")
    if not authjs_salt:
        logger.error("AUTHJS_SALT environment variable is not set.")
        raise ValueError("AUTHJS_SALT environment variable is not set.")
    
    # Derive the encryption key using the secret and salt
    key = get_derived_encryption_key(authjs_secret, authjs_salt)

    # Decrypt the token using the derived key
    try:
        data = jwe.decrypt(token, key)
        logger.info("Token decryption successful.")
        
        # Parse the decrypted data into JSON
        decoded_token = json.loads(data.decode('utf-8'))
        logger.debug(f"Decoded token data: {decoded_token}")
        return decoded_token
    except Exception as e:
        logger.error(f"Error during decryption: {e}")
        raise e

async def verify_token_get_user_id(token: str) -> str:
    """
    Verifies the Auth.js session token and extracts the user ID.
    
    Args:
    token (str): The encrypted session token.

    Returns:
    str: The extracted user ID (cognito_sub) if successful.
    
    Raises:
    ValueError: If the token is invalid or user ID is not found.
    """
    try:
        # Decode the Auth.js session token
        decoded_token = decode_nextauth_session(token)
        
        # Extract the user ID from the decoded token
        user_id = decoded_token.get("cognito_sub")
        if user_id:
            logger.info(f"User ID extracted from token: {user_id}")
            return user_id
        else:
            logger.warning("Invalid token: cognito_sub (user_id) not found.")
            raise ValueError("Invalid token, cognito_sub (user_id) not found.")
    except Exception as e:
        logger.error(f"Error verifying token: {e}")
        raise e