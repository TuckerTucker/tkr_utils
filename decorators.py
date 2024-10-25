# decorators.py
import functools
import logging
import asyncio
from typing import Callable, Any

def logs_and_exceptions(logger: logging.Logger) -> Callable:
    """
    Decorator to log and handle exceptions for both synchronous and asynchronous functions.

    Args:
        logger (logging.Logger): The logger instance to use for logging.

    Returns:
        Callable: The decorated function.
    """
    def decorator(func: Callable) -> Callable:
        if asyncio.iscoroutinefunction(func):
            @functools.wraps(func)
            async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
                try:
                    logger.debug("Starting function: %s", func.__name__)
                    result = await func(*args, **kwargs)
                    logger.debug("Finished function: %s", func.__name__)
                    return result
                except Exception as e:
                    logger.error("Exception in function %s: %s", func.__name__, str(e))
                    raise
            return async_wrapper
        else:
            @functools.wraps(func)
            def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
                try:
                    logger.debug("Starting function: %s", func.__name__)
                    result = func(*args, **kwargs)
                    logger.debug("Finished function: %s", func.__name__)
                    return result
                except Exception as e:
                    logger.error("Exception in function %s: %s", func.__name__, str(e))
                    raise
            return sync_wrapper
    return decorator

__all__ = ['logs_and_exceptions']
