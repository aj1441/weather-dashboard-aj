"""Useful decorators for the weather dashboard application"""

import time
import logging
from functools import wraps
from typing import Callable, Any

def rate_limit(min_interval: float = 1.0):
    """
    Decorator to enforce rate limiting on API calls
    
    Args:
        min_interval: Minimum seconds between calls
    """
    def decorator(func: Callable) -> Callable:
        last_called = [0.0]  # Use list to allow modification in closure
        
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            current_time = time.time()
            time_since_last = current_time - last_called[0]
            
            if time_since_last < min_interval:
                sleep_time = min_interval - time_since_last
                logging.debug(f"Rate limiting {func.__name__}: sleeping {sleep_time:.2f}s")
                time.sleep(sleep_time)
            
            last_called[0] = time.time()
            return func(*args, **kwargs)
        
        return wrapper
    return decorator

def retry_on_failure(max_retries: int = 3, delay: float = 1.0, backoff: float = 2.0):
    """
    Decorator to retry functions on failure with exponential backoff
    
    Args:
        max_retries: Maximum number of retry attempts
        delay: Initial delay between retries in seconds
        backoff: Multiplier for delay on each retry
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            current_delay = delay
            
            for attempt in range(max_retries + 1):  # +1 for initial attempt
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    
                    if attempt < max_retries:
                        logging.warning(
                            f"{func.__name__} failed (attempt {attempt + 1}/{max_retries + 1}): {e}"
                        )
                        time.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        logging.error(
                            f"{func.__name__} failed after {max_retries + 1} attempts: {e}"
                        )
            
            # Re-raise the last exception if all retries failed
            raise last_exception
        
        return wrapper
    return decorator

def log_execution_time(logger: logging.Logger = None):
    """
    Decorator to log function execution time
    
    Args:
        logger: Logger instance to use (creates default if None)
    """
    def decorator(func: Callable) -> Callable:
        nonlocal logger
        if logger is None:
            logger = logging.getLogger(func.__module__)
        
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                logger.debug(f"{func.__name__} executed in {execution_time:.3f}s")
                return result
            except Exception as e:
                execution_time = time.time() - start_time
                logger.debug(f"{func.__name__} failed after {execution_time:.3f}s: {e}")
                raise
        
        return wrapper
    return decorator

def validate_api_response(required_fields: list = None):
    """
    Decorator to validate API response data
    
    Args:
        required_fields: List of required fields in the response
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            result = func(*args, **kwargs)
            
            # Check if result is an error dict
            if isinstance(result, dict) and "error" in result:
                return result
            
            # Validate required fields if specified
            if required_fields and isinstance(result, dict):
                missing_fields = []
                for field in required_fields:
                    # Support nested field checking with dot notation
                    current = result
                    field_parts = field.split('.')
                    
                    try:
                        for part in field_parts:
                            if isinstance(current, dict):
                                current = current[part]
                            elif isinstance(current, list) and current:
                                current = current[0][part]  # Check first item in list
                            else:
                                raise KeyError(part)
                    except (KeyError, IndexError, TypeError):
                        missing_fields.append(field)
                
                if missing_fields:
                    logging.warning(f"API response missing required fields: {missing_fields}")
                    return {"error": f"Invalid API response: missing {missing_fields}"}
            
            return result
        
        return wrapper
    return decorator
