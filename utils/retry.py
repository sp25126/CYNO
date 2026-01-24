"""
Retry logic with exponential backoff for flaky external APIs.
"""
import time
import logging
from typing import Callable, TypeVar, Optional
from functools import wraps

T = TypeVar('T')
logger = logging.getLogger(__name__)


def retry_with_backoff(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exceptions: tuple = (Exception,)
):
    """
    Decorator that retries a function with exponential backoff.
    
    Args:
        max_retries: Maximum number of retry attempts
        base_delay: Initial delay in seconds
        max_delay: Maximum delay between retries
        exceptions: Tuple of exceptions to catch and retry
    
    Usage:
        @retry_with_backoff(max_retries=3, base_delay=2.0)
        def flaky_api_call():
            ...
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            last_exception = None
            
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt == max_retries - 1:
                        # Last attempt, re-raise
                        logger.error(
                            f"{func.__name__} failed after {max_retries} attempts",
                            error=str(e)
                        )
                        raise
                    
                    # Calculate delay with exponential backoff
                    delay = min(base_delay * (2 ** attempt), max_delay)
                    logger.warning(
                        f"{func.__name__} failed (attempt {attempt + 1}/{max_retries}), "
                        f"retrying in {delay}s",
                        error=str(e)
                    )
                    time.sleep(delay)
            
            # Should never reach here, but for type safety
            if last_exception:
                raise last_exception
            
        return wrapper
    return decorator


# Async version
async def async_retry_with_backoff(
    func: Callable,
    max_retries: int = 3,
    base_delay: float = 1.0,
    exceptions: tuple = (Exception,)
):
    """
    Async retry with exponential backoff.
    
    Usage:
        result = await async_retry_with_backoff(
            lambda: some_async_func(),
            max_retries=3
        )
    """
    import asyncio
    
    last_exception = None
    for attempt in range(max_retries):
        try:
            return await func()
        except exceptions as e:
            last_exception = e
            if attempt == max_retries - 1:
                raise
            
            delay = base_delay * (2 ** attempt)
            logger.warning(f"Retry attempt {attempt + 1}/{max_retries} after {delay}s")
            await asyncio.sleep(delay)
    
    if last_exception:
        raise last_exception
