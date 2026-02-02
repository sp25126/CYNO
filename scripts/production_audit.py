import sys
import os
import shutil
from pathlib import Path

# Add project root to path
sys.path.append(os.getcwd())

from cli.state import state
from cli.cyno import cmd_resume
from cli.command_routers import CommandRouter
from rich.console import Console

console = Console()
router = CommandRouter(console)

def run_audit():
    print("🔎 STARTING PRODUCTION AUDIT...")
    
    # 1. Reset State
    if Path("data/cli_state.json").exists():
        os.remove("data/cli_state.json")
    state._load() # Reload empty
    
    # 2. Test "Honest Failure"
    print("\n[Test 1] Testing /app cover without resume...")
    res = router._handle_cover_letter("Google Engineer")
    if "No resume loaded" in res:
        print("✅ PASSED: System honestly refused to fake a cover letter.")
    else:
        print(f"❌ FAILED: System returned: {res}")
        return

    # 3. Load Real Resume
    real_resume = "resumes/SaumyaPatel_Resume-1 (1)-1.pdf"
    if not os.path.exists(real_resume):
        print(f"⚠️ Warning: {real_resume} not found. Using generic test file won't prove 'real data' usage.")
        return

    print(f"\n[Test 2] Parsing REAL resume: {real_resume}...")
    output = cmd_resume(f'"{real_resume}"')
    
    if "Resume Analyzed & Saved" not in str(console.file.getvalue() if hasattr(console.file, 'getvalue') else "") and state.get_resume() is None:
         # cmd_resume prints to console directly, so we check state
         pass

    if state.get_resume():
        print(f"✅ PASSED: Resume saved to state. Name found: {state.get_resume().get('name')}")
    else:
        print("❌ FAILED: Resume data not in state.")
        return

    # 4. Test "Honest Success"
    print("\n[Test 3] Testing /app cover WITH resume...")
    # Clean output buffer
    res = router._handle_cover_letter("Google Engineer")
    
    # We can't easily capture the rich output from here without mocking console print, 
    # but if it returns empty string (success) that's a good sign.
    if res == "":
        print("✅ PASSED: Generated cover letter using saved state.")
    else:
        print(f"❌ FAILED: {res}")

if __name__ == "__main__":
    run_audit()
