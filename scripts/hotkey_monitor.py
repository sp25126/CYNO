"""
Hotkey Interaction Monitor.
Tails the hotkey_service.log file to show real-time interactions.
"""
import os
import time
import sys

LOG_FILE = "logs/hotkey_service.log"

def tail_log():
    """Tails the log file and prints new lines."""
    if not os.path.exists(LOG_FILE):
        print(f"Waiting for log file: {LOG_FILE}...")
        while not os.path.exists(LOG_FILE):
            time.sleep(1)
    
    print(f"--- Monitoring {LOG_FILE} ---")
    print("Press Ctrl+C to stop.\n")
    
    with open(LOG_FILE, 'r') as f:
        # Go to the end of the file
        f.seek(0, os.SEEK_END)
        
        while True:
            line = f.readline()
            if not line:
                time.sleep(0.1)
                continue
                
            # Filter and format for professional display
            if "[User Input]" in line:
                print(f"\n👤 [USER]: {line.split('[User Input]')[1].strip()}")
            elif "[Cyno Response]" in line:
                print(f"🤖 [CYNO]: {line.split('[Cyno Response]')[1].strip()}")
            elif "CYNO ACTIVATED" in line:
                print("\n⚡ [EVENT]: Cyno activated via hotkey.")
            elif "Service] Starting" in line:
                print("🟢 [STATUS]: Hotkey service started.")

if __name__ == "__main__":
    try:
        tail_log()
    except KeyboardInterrupt:
        print("\n\nMonitor stopped.")
        sys.exit(0)
