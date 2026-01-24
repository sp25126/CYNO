
import asyncio
import sys
import os
import shutil
import time
import pytest
from typing import List, Dict, Any
from pydantic import ValidationError
import pytest
from typing import List, Dict, Any
from pydantic import ValidationError
# from termcolor import colored # Removed

# Adjust path
sys.path.append(os.getcwd())

from models import Resume, Job 
from agent.state import AgentState
from tools.job_search import DDGS  # Use DDGS directly for smoke test
from langchain_ollama import ChatOllama

# --- Configuration ---
OLLAMA_MODEL = "llama3.2"  # Or mistral
BASE_URL = "http://localhost:11434"

class TestSuite:
    def __init__(self):
        self.results = []
        self.failed = False

    def log(self, message: str, status: str = "INFO"):
        # Simple logging without color dependency
        print(f"[{status}] {message}")
        if status == "FAIL":
            self.failed = True

    def check_ollama(self):
        print("\n--- 1. Infrastructure Check (Ollama) ---")

        try:
            llm = ChatOllama(model=OLLAMA_MODEL, base_url=BASE_URL)
            llm.invoke("Hi")
            self.log("Ollama connectivity verified.", "PASS")
        except Exception as e:
            self.log(f"Ollama connection failed: {e}", "FAIL")

    def verify_schemas(self):
        print("\n--- 2. Pydantic Schema Validation ---")
        try:
            # Resume
            r = Resume(parsed_skills=["Python"], education_level="BACHELORS", years_exp=2, location="India", raw_text="Sample")
            self.log("Resume Schema valid.", "PASS")
            
            # Job
            j = Job(title="Dev", company="Corp", location="Remote", job_url="http://x.com", apply_url="http://y.com", description="Code must be long enough", source="manual")
            self.log("Job Schema valid.", "PASS")
            
        except ValidationError as e:
            self.log(f"Schema Validation Failed: {e}", "FAIL")

    async def verify_tools_smoke(self):
        print("\n--- 3. Tool Smoke Tests ---")
        
        # Job Search
        try:
            print("   Searching for 'Python' via DDGS...")
            results = DDGS().text("Python developer remote", max_results=2)
            if results:
                self.log(f"Job Search returned {len(results)} results.", "PASS")
            else:
                self.log("Job Search returned 0 results (might be network).", "WARN")
        except Exception as e:
            self.log(f"Job Search Tool Failed: {e}", "FAIL")

    def run_pytest(self):
        print("\n--- 4. Full Pytest Suite ---")
        # Run pytest programmatically
        retcode = pytest.main(["-v", "tests/"])
        if retcode == 0:
            self.log("Pytest Suite Passed.", "PASS")
        else:
            self.log(f"Pytest Suite Failed with code {retcode}.", "FAIL")

async def async_main(suite: TestSuite):
    # Run async checks
    suite.check_ollama()
    suite.verify_schemas()
    await suite.verify_tools_smoke()

if __name__ == "__main__":
    suite = TestSuite()
    
    # 1. Async Phase
    try:
        asyncio.run(async_main(suite))
    except Exception as e:
        print(f"Async Phase Error: {e}")
    
    # 2. Sync Phase (Pytest handles its own loop)
    suite.run_pytest()
    
    if suite.failed:
        sys.exit(1)
    sys.exit(0)
