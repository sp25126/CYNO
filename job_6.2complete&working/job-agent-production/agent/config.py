import os
from dataclasses import dataclass, field

@dataclass
class OllamaConfig:
    base_url: str = field(default_factory=lambda: os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"))
    model: str = field(default_factory=lambda: os.getenv("OLLAMA_MODEL", "gemma2:2b"))
    timeout_s: int = 30

@dataclass
class GeminiConfig:
    api_key_env_var_name: str = "GEMINI_API_KEY"
    model: str = "gemini-pro"
    
    @property
    def api_key(self) -> str:
        return os.environ.get(self.api_key_env_var_name, "")

@dataclass
class RedditConfig:
    client_id: str = field(default_factory=lambda: os.getenv("REDDIT_CLIENT_ID", ""))
    client_secret: str = field(default_factory=lambda: os.getenv("REDDIT_CLIENT_SECRET", ""))
    user_agent: str = field(default_factory=lambda: os.getenv("REDDIT_USER_AGENT", "python:job-agent:v1.0"))

@dataclass
class AgentConfig:
    ollama: OllamaConfig = field(default_factory=OllamaConfig)
    gemini: GeminiConfig = field(default_factory=GeminiConfig)
    reddit: RedditConfig = field(default_factory=RedditConfig)
    recursion_limit: int = 50
    request_timeout_s: int = 30
    max_steps: int = 10

# Default instance for backward compatibility or direct import usage
default_agent_config = AgentConfig()
# Create default_ollama_config alias for existing code that imports it
default_ollama_config = default_agent_config.ollama
default_gemini_config = default_agent_config.gemini

# Validation Logic
def validate_config(config: AgentConfig = default_agent_config) -> None:
    """Validates the configuration and prints warnings if credentials are missing."""
    if not config.reddit.client_id or not config.reddit.client_secret:
        print("Warning: Reddit credentials missing.")
    if not config.gemini.api_key:
        print("Warning: Gemini API Key missing. Complex reasoning will fallback to Ollama.")
