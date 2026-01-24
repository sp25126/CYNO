from tools.job_matcher import JobMatchingTool
import time

print("Starting debug...")
try:
    start = time.time()
    tool = JobMatchingTool()
    print(f"Tool instantiated in {time.time() - start:.2f}s")
    if tool.model:
        print("Model loaded successfully.")
    else:
        print("Model failed to load.")
except Exception as e:
    print(f"Error instantiating tool: {e}")
except KeyboardInterrupt:
    print("Interrupted.")
