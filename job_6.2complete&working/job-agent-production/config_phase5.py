"""
Centralized configuration for Cyno Job Agent.
All hardcoded values extracted here for easy management.
"""
import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from credentials_setup.env
env_path = Path(__file__).parent / "credentials_setup.env"
load_dotenv(dotenv_path=env_path)



class Config:
    """Global configuration class."""
    
    # === LLM Settings ===
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    
    # Model choices
    TOOL_LLM_MODEL: str = os.getenv("TOOL_LLM_MODEL", "gemma2:2b")  # JSON mode, low temp
    CHAT_LLM_MODEL: str = os.getenv("CHAT_LLM_MODEL", "qwen2.5:3b")  # Conversational, higher temp
    
    # LLM temperatures
    TOOL_LLM_TEMP: float = 0.1  # Deterministic for tool calls
    CHAT_LLM_TEMP: float = 0.7  # Creative for responses
    
    # === Timeouts & Retries ===
    OLLAMA_STARTUP_TIMEOUT: int = 20  # Seconds to wait for Ollama to start
    JOB_SEARCH_TIMEOUT: int = 90  # Max seconds for job search
    LLM_REQUEST_TIMEOUT: int = 30  # Max seconds for single LLM call
    
    MAX_RETRIES: int = 3  # For flaky APIs (Reddit, DuckDuckGo)
    RETRY_BACKOFF_BASE: float = 2.0  # Exponential backoff multiplier
    
    # === Job Search Limits ===
    MAX_JOBS_PER_SOURCE: int = 20
    MAX_JOBS_TO_MATCH: int = 20
    REDDIT_SEARCH_LIMIT: int = 15
    JOBSPY_RESULTS_WANTED: int = 10
    
    # === File Paths ===
    PROJECT_ROOT: Path = Path(__file__).parent
    RESUMES_DIR: Path = PROJECT_ROOT / "resumes"
    JOBS_DIR: Path = PROJECT_ROOT / "jobs"
    EMAILS_DIR: Path = PROJECT_ROOT / "emails"
    TESTS_DIR: Path = PROJECT_ROOT / "tests"
    
    # === Reddit API ===
    REDDIT_CLIENT_ID: str = os.getenv("REDDIT_CLIENT_ID", "")
    REDDIT_CLIENT_SECRET: str = os.getenv("REDDIT_CLIENT_SECRET", "")
    REDDIT_USER_AGENT: str = "JobAgent/1.0"
    
    # === Resume Parsing ===
    MIN_RESUME_LENGTH: int = 100  # Minimum characters for valid resume
    
    # === Memory & Logging ===
    MEMORY_DB_PATH: Path = PROJECT_ROOT / "data" / "memory.db"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT: str = "json"  # For structlog
    
    # === Safety ===
    ENABLE_AUTO_EMAIL_SEND: bool = False  # Never auto-send emails
    
    @classmethod
    def ensure_directories(cls):
        """Create necessary directories if they don't exist."""
        for dir_path in [cls.RESUMES_DIR, cls.JOBS_DIR, cls.EMAILS_DIR, cls.MEMORY_DB_PATH.parent]:
            dir_path.mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def validate(cls) -> tuple[bool, Optional[str]]:
        """
        Validate configuration.
        Returns: (is_valid, error_message)
        """
        # Check Reddit credentials
        if not cls.REDDIT_CLIENT_ID or not cls.REDDIT_CLIENT_SECRET:
            return False, "Reddit API credentials not found in environment"
        
        # Check Ollama URL format
        if not cls.OLLAMA_BASE_URL.startswith("http"):
            return False, f"Invalid OLLAMA_BASE_URL: {cls.OLLAMA_BASE_URL}"
        
        return True, None


# Auto-create directories on import
Config.ensure_directories()
