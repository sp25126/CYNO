import os
import shutil

SOURCE_DIR = "job-agent-production"
ROOT = os.getcwd()

def flatten():
    if not os.path.exists(SOURCE_DIR):
        print(f"Source dir {SOURCE_DIR} not found.")
        return

    print(f"Flattening from {SOURCE_DIR} to {ROOT}...")
    
    for item in os.listdir(SOURCE_DIR):
        src = os.path.join(SOURCE_DIR, item)
        dst = os.path.join(ROOT, item)
        
        try:
            if os.path.exists(dst):
                print(f"Conflict: {dst} exists. Removing destination.")
                if os.path.isdir(dst):
                    shutil.rmtree(dst)
                else:
                    os.remove(dst)
            
            shutil.move(src, dst)
            print(f"Moved: {item}")
        except Exception as e:
            print(f"Error moving {item}: {e}")

    # Remove empty source dir
    try:
        os.rmdir(SOURCE_DIR)
        print("Removed empty source dir.")
    except:
        pass

if __name__ == "__main__":
    flatten()
