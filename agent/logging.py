import structlog
import logging
import sys
from typing import Any

def configure_structlog() -> None:
    """
    Configures structlog for JSON output, suitable for production logging.
    """
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer()
        ],
        logger_factory=structlog.PrintLoggerFactory(),
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        cache_logger_on_first_use=True,
    )

def get_logger(name: str) -> Any:
    """
    Returns a structlog logger with the bound name.
    """
    return structlog.get_logger(name=name)

def log_event(logger: Any, event_name: str, **fields: Any) -> None:
    """
    Helper to log an event with structured data.
    """
    logger.info(event_name, **fields)

# Auto-configure on import if desired, or let the main entrypoint do it.
# The prompt implies providing the function.
# We will not auto-run it at module level to allow upstream configuration, 
# but it's safe to run it if the user wants default behavior.
# Given the previous config had it auto-run, I'll stick to providing the function
# so the orchestrator calls it.
