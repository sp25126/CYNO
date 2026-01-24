import requests
import json
import time
import sys

def run_health_check():
    """
    Checks if the Ollama server is running and the model responds within a timeout.
    """
    ollama_url = "http://localhost:11434"
    model_name = "gemma2:2b"
    
    print(f"--- Running Ollama Health Check ---")
    print(f"Target: {ollama_url}")
    print(f"Model: {model_name}")

    try:
        # 1. Check if the server is running by checking a basic endpoint
        response = requests.get(ollama_url, timeout=5)
        response.raise_for_status()
        print("✅ Ollama server is running.")

        # 2. Send a request to the model and time it
        prompt = "Why is the sky blue? Explain it simply in one sentence."
        data = {
            "model": model_name,
            "prompt": prompt,
            "stream": False
        }
        
        start_time = time.time()
        response = requests.post(f"{ollama_url}/api/generate", json=data, timeout=30)
        end_time = time.time()
        
        response.raise_for_status()
        
        duration = end_time - start_time
        response_data = response.json()
        
        generated_text = response_data.get("response", "").strip()
        
        # 3. Check the results
        success = True
        if generated_text and len(generated_text) > 10:
            print(f"✅ Model generated coherent text: '{generated_text}'")
        else:
            print(f"❌ Model response was empty or too short.")
            success = False

        if duration <= 10.0:
            print(f"✅ Model responded in {duration:.2f} seconds (within 10s target).")
        else:
            print(f"⚠️  Model responded in {duration:.2f} seconds (slower than 10s target).")
            # This is a warning, not a failure for the script's purpose
            # But we can make it a failure if strictness is required.
            # For now, let's consider it a "pass" with a warning.
            
        if success:
            print("\n--- Health Check Result: PASSED ---")
        else:
            print("\n--- Health Check Result: FAILED ---")
            sys.exit(1)


    except requests.exceptions.ConnectionError:
        print("❌ Health Check Failed: Could not connect to Ollama server.")
        print("   Please ensure the Ollama server is running on http://localhost:11434.")
        sys.exit(1)
    except requests.exceptions.Timeout:
        print("❌ Health Check Failed: Request timed out.")
        sys.exit(1)
    except requests.exceptions.RequestException as e:
        print(f"❌ Health Check Failed: An HTTP request error occurred: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_health_check()
