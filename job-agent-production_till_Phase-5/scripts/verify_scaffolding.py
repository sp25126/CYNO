import sys
import os

# Ensure root is in path
sys.path.append(os.getcwd())

try:
    print("Testing agent/state.py...")
    from agent.state import AgentState, RouterDecision, ensure_state_defaults, safe_append_message
    from agent.state import MAX_SEARCH_RETRIES
    print("  AgentState imported.")
    print("  RouterDecision imported.")
    
    print("Testing agent/config.py...")
    from agent.config import OllamaConfig, GeminiConfig, AgentConfig
    print("  Configs imported.")
    
    print("Testing agent/logging.py...")
    from agent.logging import configure_structlog, get_logger, log_event
    configure_structlog()
    logger = get_logger("test")
    log_event(logger, "test_event", foo="bar")
    print("  Logging configured and tested.")
    
    print("All Phase 2D scaffolding verified!")
except Exception as e:
    print(f"VERIFICATION FAILED: {e}")
    sys.exit(1)
