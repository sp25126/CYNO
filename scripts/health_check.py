"""
System health check script.
Verifies Ollama, database, and core components are working.
"""
import sys
import requests
from pathlib import Path

# Add parent dir to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import Config
from tools.memory import PersistentMemory
from tools.registry import ToolRegistry
from colorama import Fore, Style, init

init(autoreset=True)


def check_ollama():
    """Check if Ollama is running."""
    try:
        response = requests.get(f"{Config.OLLAMA_BASE_URL}/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get("models", [])
            model_names = [m["name"] for m in models]
            
            # Check if required models are available
            required = [Config.TOOL_LLM_MODEL, Config.CHAT_LLM_MODEL]
            missing = [m for m in required if m not in model_names]
            
            if missing:
                print(f"{Fore.YELLOW}⚠️  Ollama running but missing models: {', '.join(missing)}")
                return False
            else:
                print(f"{Fore.GREEN}✓ Ollama running with required models")
                return True
        else:
            print(f"{Fore.RED}✗ Ollama returned {response.status_code}")
            return False
    except Exception as e:
        print(f"{Fore.RED}✗ Ollama not accessible: {e}")
        return False


def check_database():
    """Check if database is accessible."""
    try:
        with PersistentMemory() as mem:
            # Try a simple operation
            mem.save_search("health_check", 0)
            recent = mem.get_recent_searches(1)
            if recent:
                print(f"{Fore.GREEN}✓ Database working")
                return True
            else:
                print(f"{Fore.YELLOW}⚠️  Database accessible but query returned empty")
                return False
    except Exception as e:
        print(f"{Fore.RED}✗ Database error: {e}")
        return False


def check_tools():
    """Check if all tools are registered."""
    try:
        tools = ToolRegistry.list_tools()
        expected = 9  # We have 9 registered tools
        
        if len(tools) >= expected:
            print(f"{Fore.GREEN}✓ Tools registered ({len(tools)} tools)")
            return True
        else:
            print(f"{Fore.YELLOW}⚠️  Only {len(tools)} tools registered (expected {expected})")
            return False
    except Exception as e:
        print(f"{Fore.RED}✗ Tool registry error: {e}")
        return False


def check_directories():
    """Check if required directories exist."""
    dirs = [Config.RESUMES_DIR, Config.JOBS_DIR, Config.EMAILS_DIR]
    all_exist = True
    
    for dir_path in dirs:
        if dir_path.exists():
            print(f"{Fore.GREEN}✓ {dir_path.name}/ exists")
        else:
            print(f"{Fore.RED}✗ {dir_path.name}/ missing")
            all_exist = False
    
    return all_exist


def check_config():
    """Validate configuration."""
    is_valid, error = Config.validate()
    if is_valid:
        print(f"{Fore.GREEN}✓ Configuration valid")
        return True
    else:
        print(f"{Fore.RED}✗ Configuration error: {error}")
        return False


def main():
    print(f"\n{Fore.CYAN}{'='*50}")
    print(f"{Fore.CYAN}Cyno System Health Check")
    print(f"{Fore.CYAN}{'='*50}\n")
    
    checks = {
        "Config": check_config(),
        "Ollama": check_ollama(),
        "Database": check_database(),
        "Tools": check_tools(),
        "Directories": check_directories()
    }
    
    print(f"\n{Fore.CYAN}{'='*50}")
    passed = sum(checks.values())
    total = len(checks)
    
    if passed == total:
        print(f"{Fore.GREEN}✓ All checks passed ({passed}/{total})")
        print(f"{Fore.GREEN}System is ready to use!")
        return 0
    else:
        print(f"{Fore.YELLOW}⚠️  {passed}/{total} checks passed")
        print(f"{Fore.YELLOW}Please fix issues above before running Cyno")
        return 1


if __name__ == "__main__":
    sys.exit(main())
