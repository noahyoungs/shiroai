from contextvars import ContextVar
from typing import Dict, Any
from log_config import set_current_username, clear_current_username

current_user_data = ContextVar('current_user_data', default=None)

def get_user_data() -> Dict[str, Any]:
    return current_user_data.get()

def update_user_data(updates: Dict[str, Any]):
    user_data = get_user_data()
    user_data.update(updates)
    current_user_data.set(user_data)
    if 'username' in updates:
        set_current_username(updates['username'])

def set_user_data(data: Dict[str, Any]):
    current_user_data.set(data)
    if 'username' in data:
        set_current_username(data['username'])

def clear_user_data():
    current_user_data.set(None)
    clear_current_username()

def get_username() -> str:
    user_data = get_user_data()
    return user_data.get('username', 'Unknown') if user_data else 'Unknown'