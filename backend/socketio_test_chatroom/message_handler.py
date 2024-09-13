from log_config import logger

async def handle_message(message: str, username: str, message_count: int, emit_func):
    new_message_count = message_count + 1
    
    # Log the message
    logger.info(f"Message received: {message}")
    
    # Simulate an error for demonstration (remove in production)
    if message.lower() == 'error':
        raise ValueError("Simulated error in message handling")
    
    # Emit the message to all clients
    await emit_func('chat_message', {'username': username, 'message': message}, room=None)
    
    return new_message_count