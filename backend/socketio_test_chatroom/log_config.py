# log_config.py (socketio_test_chatroom)

import logging
from contextvars import ContextVar
from typing import Optional

# Define a ContextVar to hold the current username
current_username: ContextVar[Optional[str]] = ContextVar('current_username', default=None)

class UsernameFilter(logging.Filter):
    def filter(self, record):
        username = current_username.get()
        record.username = username if username is not None else 'Unknown'
        return True

def set_current_username(username: str):
    current_username.set(username)

def clear_current_username():
    current_username.set(None)

def setup_logging():
    logger = logging.getLogger('socketio_chat')
    
    if not logger.handlers:
        logger.setLevel(logging.DEBUG)

        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)

        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - [%(username)s] - %(message)s')

        ch.addFilter(UsernameFilter())
        ch.setFormatter(formatter)

        logger.addHandler(ch)
        logger.propagate = False

    return logger

# Create and export the logger
logger = setup_logging()