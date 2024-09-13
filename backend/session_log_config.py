import logging
from contextvars import ContextVar
import sys
import coloredlogs
import os

# Create a context variable to store the user ID
current_user_id = ContextVar('current_user_id', default=None)

class UserIdFilter(logging.Filter):
    def filter(self, record):
        user_id = current_user_id.get()
        if user_id:
            record.user_id = user_id
        else:
            record.user_id = 'N/A'
        return True

# Configure the root logger
root_logger = logging.getLogger('shiro_ai')
root_logger.setLevel(logging.INFO)

# Create a stream handler that logs to stdout
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)

# Add the UserIdFilter to the handler
handler.addFilter(UserIdFilter())

# Add the handler to the root logger
root_logger.addHandler(handler)

# Configure coloredlogs to make the output human-readable with color
coloredlogs.install(
    level='INFO',
    logger=root_logger,
    fmt='%(asctime)s %(name)s %(levelname)s [User ID: %(user_id)s]: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def set_current_user_id(user_id):
    current_user_id.set(user_id)

def clear_current_user_id():
    current_user_id.set(None)

def get_relative_path(absolute_path):
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    return os.path.relpath(absolute_path, project_root)

def get_module_name(absolute_path):
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    relative_path = os.path.relpath(absolute_path, project_root)
    module_path = os.path.splitext(relative_path)[0].replace(os.path.sep, '.')
    return f'shiro_ai.{module_path}'

def get_child_logger(absolute_path, level=None):
    module_name = get_module_name(absolute_path)
    logger = logging.getLogger(module_name)
    
    if level is not None:
        logger.setLevel(level)
    
    class RelativePathFilter(logging.Filter):
        def filter(self, record):
            # Disable path logging for now
            return True
    
    logger.addFilter(RelativePathFilter())
    return logger

# Function to set log level for a specific module
def set_log_level(module_name, level):
    logger = logging.getLogger(module_name)
    logger.setLevel(level)