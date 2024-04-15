from background_tasks.celery_app import app
import time

@app.task
def run_test_task(duration):
    print(f"Starting long-running task for {duration} seconds...")
    time.sleep(duration)
    with open("test.txt", "w") as f:
        f.write("Hello, World!")
    print("Long-running task completed.")
    return f"Task completed after {duration} seconds."