
import os
import requests
import json
from dotenv import load_dotenv

# Load env to get server URL
load_dotenv()
SERVER_URL = os.getenv("COLAB_SERVER_URL")

if not SERVER_URL:
    print("❌ COLAB_SERVER_URL not found in .env")
    # user_url = input("Enter Colab URL (e.g., https://xyz.ngrok.app): ")
    # SERVER_URL = user_url
    exit(1)

print(f"🔗 Connecting to {SERVER_URL}...")

def test_exec_simple():
    print("\n[Test 1] Simple Math Execution")
    code = "print('Hello from Remote GPU!'); res = 5 + 10; print(f'5 + 10 = {res}')"
    
    try:
        response = requests.post(f"{SERVER_URL}/exec", json={"code": code}, timeout=10)
        if response.status_code == 200:
            res_json = response.json()
            if res_json['success']:
                print("✅ Success!")
                print("Output:\n" + "-"*20 + "\n" + res_json['output'] + "\n" + "-"*20)
            else:
                print(f"❌ Execution failed: {res_json.get('error')}")
                print(f"Output: {res_json.get('output')}")
        else:
            print(f"❌ HTTP Error: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ Connection Error: {e}")

def test_exec_gpu():
    print("\n[Test 2] GPU Availability Check")
    code = """
import torch
if torch.cuda.is_available():
    print(f"✅ GPU is available: {torch.cuda.get_device_name(0)}")
    print(f"Memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.2f} GB")
else:
    print("❌ GPU NOT available")
"""
    try:
        response = requests.post(f"{SERVER_URL}/exec", json={"code": code}, timeout=20)
        if response.status_code == 200:
            res_json = response.json()
            print("Output:\n" + "-"*20 + "\n" + res_json['output'] + "\n" + "-"*20)
        else:
            print(f"❌ HTTP Error: {response.status_code}")
    except Exception as e:
        print(f"❌ Connection Error: {e}")

if __name__ == "__main__":
    test_exec_gpu() # Prioritize GPU check
    # test_exec_simple()
