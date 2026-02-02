import subprocess
import time
import requests
import shutil
import os
import sys

OLLAMA_URL = "http://localhost:11434"

def is_ollama_running():
    try:
        requests.get(f"{OLLAMA_URL}/api/tags", timeout=1)
        return True
    except requests.exceptions.ConnectionError:
        return False

def start_ollama():
    if is_ollama_running():
        print("✅ [Infra] Ollama is already running.")
        return True

    print("⚠️ [Infra] Ollama not detected. Attempting to start...")
    
    # Check for executable
    ollama_path = shutil.which("ollama")
    if not ollama_path:
        # Common Windows paths
        default_path = os.path.expanduser("~\\AppData\\Local\\Programs\\Ollama\\ollama.exe")
        if os.path.exists(default_path):
            ollama_path = default_path
            
    if not ollama_path:
        print("❌ [Infra] Could not find 'ollama' executable in PATH or default location.")
        print("   Please install Ollama or start it manually.")
        return False

    print(f"   Using Ollama at: {ollama_path}")
    
    # Start process detached
    try:
        if sys.platform == "win32":
            # CREATE_NEW_CONSOLE uses 0x00000010
            process = subprocess.Popen(
                [ollama_path, "serve"], 
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
        else:
            process = subprocess.Popen(
                [ollama_path, "serve"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True
            )
            
        print("   Waiting for Ollama to initialize (max 20s)...")
        
        # Wait for up to 20 seconds
        for _ in range(10):
            if is_ollama_running():
                print("✅ [Infra] Ollama started successfully!")
                return True
            time.sleep(2)
            print("   ...")
            
        print("❌ [Infra] Ollama process started but API is not responding yet.")
        return False
        
    except Exception as e:
        print(f"❌ [Infra] Failed to start Ollama: {e}")
        return False

if __name__ == "__main__":
    start_ollama()
