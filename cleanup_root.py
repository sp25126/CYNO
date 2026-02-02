import os
import shutil
import time

KEEP_FOLDERS = [
    "job_6.2complete&working", 
    "jobTILLUPDATION26012026", 
    ".git",
    ".gitignore" # Valid to keep gitignore
]

KEEP_FILES = [
    "cleanup_root.py"
]

def cleanup():
    print("WARNING: Starting Destructive Cleanup...")
    root = os.getcwd()
    
    for item in os.listdir(root):
        if item in KEEP_FOLDERS or item in KEEP_FILES:
            print(f"Skipping Preserved Item: {item}")
            continue
            
        path = os.path.join(root, item)
        try:
            if os.path.isdir(path):
                print(f"Deleting Directory: {item}")
                # Retry loop for Windows file locks
                for i in range(3):
                    try:
                        shutil.rmtree(path)
                        break
                    except Exception as e:
                        print(f"  Retry {i+1} deleting {item}: {e}")
                        time.sleep(1)
            else:
                print(f"Deleting File: {item}")
                os.remove(path)
        except Exception as e:
            print(f"FAILED to delete {item}: {e}")

    print("Cleanup Complete. Self-destructing script.")
    try:
        os.remove(__file__)
    except:
        pass

if __name__ == "__main__":
    cleanup()
