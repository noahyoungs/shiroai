import os
from importlib import import_module

# Dynamically import all modules in the current directory
for filename in os.listdir(os.path.dirname(__file__)):
    if filename.endswith(".py") and filename != "__init__.py":
        module_name = f"background_tasks.tasks.{os.path.splitext(filename)[0]}"
        import_module(module_name)