"""
Error handler utility for the weather dashboard application.

This module provides consistent error handling and user feedback
throughout the application, including logging and user-friendly messages.
"""

import logging
import traceback
from typing import Optional, Callable, Any, Dict
from functools import wraps

from utils.error_handling.exceptions import (
    WeatherDashboardError, APIError, ValidationError, DataError,
    ConfigurationError, ThemeError, NetworkError, UserInputError,
    ErrorMessages
)


class ErrorHandler:
    """Centralized error handler for the application."""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """Initialize the error handler."""
        self.logger = logger or logging.getLogger(__name__)
        self.error_callbacks: Dict[str, Callable] = {}
    
    def register_callback(self, error_type: str, callback: Callable) -> None:
        """Register a callback for a specific error type."""
        self.error_callbacks[error_type] = callback
    
    def handle_error(self, error: Exception, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Handle an error and return a user-friendly message.
        
        Args:
            error: The exception that occurred
            context: Additional context information
            
        Returns:
            User-friendly error message
        """
        context = context or {}
        
        # Log the error with full details
        self._log_error(error, context)
        
        # Get user-friendly message
        user_message = self._get_user_message(error, context)
        
        # Call registered callback if available
        error_type = type(error).__name__
        if error_type in self.error_callbacks:
            try:
                self.error_callbacks[error_type](error, context, user_message)
            except Exception as callback_error:
                self.logger.error(f"Error in error callback: {callback_error}")
        
        return user_message
    
    def _log_error(self, error: Exception, context: Dict[str, Any]) -> None:
        """Log the error with full details."""
        error_details = {
            'error_type': type(error).__name__,
            'error_message': str(error),
            'context': context
        }
        
        if isinstance(error, WeatherDashboardError):
            error_details['details'] = error.details
        
        self.logger.error(
            f"Error occurred: {error}",
            extra={
                'error_details': error_details,
                'traceback': traceback.format_exc()
            }
        )
    
    def _get_user_message(self, error: Exception, context: Dict[str, Any]) -> str:
        """Get a user-friendly error message."""
        if isinstance(error, WeatherDashboardError):
            return str(error)
        
        # Handle specific exception types
        if isinstance(error, ConnectionError):
            return ErrorMessages.NETWORK_CONNECTION_FAILED
        
        if isinstance(error, TimeoutError):
            timeout = context.get('timeout', 'unknown')
            return ErrorMessages.NETWORK_TIMEOUT.format(timeout=timeout)
        
        if isinstance(error, FileNotFoundError):
            file_path = context.get('file_path', 'unknown file')
            return ErrorMessages.FILE_NOT_FOUND.format(file_path=file_path)
        
        if isinstance(error, PermissionError):
            file_path = context.get('file_path', 'unknown file')
            return ErrorMessages.FILE_PERMISSION_DENIED.format(file_path=file_path)
        
        if isinstance(error, ValueError):
            return f"Invalid value: {error}"
        
        if isinstance(error, KeyError):
            return f"Missing required data: {error}"
        
        if isinstance(error, TypeError):
            return f"Type error: {error}"
        
        # Generic error message
        return f"An unexpected error occurred: {error}"
    
    def handle_api_error(self, error: APIError) -> str:
        """Handle API-specific errors."""
        if error.status_code == 429:
            retry_after = error.details.get('retry_after', 60)
            return ErrorMessages.API_RATE_LIMITED.format(retry_after=retry_after)
        
        if error.status_code == 503:
            return ErrorMessages.API_SERVICE_UNAVAILABLE
        
        if error.status_code == 401:
            return ErrorMessages.API_AUTHENTICATION_FAILED.format(api_name=error.api_name)
        
        if error.status_code == 404:
            if isinstance(error, WeatherAPIError):
                return ErrorMessages.WEATHER_CITY_NOT_FOUND.format(city=error.city or 'unknown')
            elif isinstance(error, GeocodingAPIError):
                return ErrorMessages.GEOCODING_LOCATION_NOT_FOUND.format(location=error.location or 'unknown')
        
        return ErrorMessages.API_INVALID_RESPONSE.format(api_name=error.api_name)
    
    def handle_validation_error(self, error: ValidationError) -> str:
        """Handle validation errors."""
        if error.field == 'city':
            return ErrorMessages.VALIDATION_INVALID_CITY
        
        if error.field == 'state':
            return ErrorMessages.VALIDATION_INVALID_STATE
        
        if error.field == 'temperature':
            return ErrorMessages.VALIDATION_INVALID_TEMPERATURE.format(value=error.value)
        
        if error.field == 'humidity':
            return ErrorMessages.VALIDATION_INVALID_HUMIDITY
        
        if error.field == 'pressure':
            return ErrorMessages.VALIDATION_INVALID_PRESSURE
        
        if error.field == 'wind_speed':
            return ErrorMessages.VALIDATION_INVALID_WIND_SPEED
        
        return str(error)
    
    def handle_data_error(self, error: DataError) -> str:
        """Handle data-related errors."""
        data_type = error.data_type or 'unknown'
        
        if error.operation == 'save':
            return ErrorMessages.DATA_SAVE_FAILED.format(data_type=data_type)
        
        if error.operation == 'load':
            return ErrorMessages.DATA_LOAD_FAILED.format(data_type=data_type)
        
        if error.operation == 'delete':
            return ErrorMessages.DATA_DELETE_FAILED.format(data_type=data_type)
        
        return ErrorMessages.DATA_NOT_FOUND.format(data_type=data_type)
    
    def handle_configuration_error(self, error: ConfigurationError) -> str:
        """Handle configuration errors."""
        if error.config_key:
            if error.config_value is None:
                return ErrorMessages.CONFIG_MISSING_KEY.format(key=error.config_key)
            else:
                return ErrorMessages.CONFIG_INVALID_VALUE.format(
                    key=error.config_key,
                    value=error.config_value
                )
        
        return str(error)
    
    def handle_theme_error(self, error: ThemeError) -> str:
        """Handle theme errors."""
        if error.theme_name:
            if error.theme_type == 'not_found':
                return ErrorMessages.THEME_NOT_FOUND.format(theme_name=error.theme_name)
            elif error.theme_type == 'apply_failed':
                return ErrorMessages.THEME_APPLY_FAILED.format(theme_name=error.theme_name)
        
        if error.theme_type:
            return ErrorMessages.THEME_INVALID_TYPE.format(theme_type=error.theme_type)
        
        return str(error)
    
    def handle_user_input_error(self, error: UserInputError) -> str:
        """Handle user input errors."""
        if error.input_field == 'city' and not error.input_value:
            return ErrorMessages.INPUT_EMPTY_CITY
        
        if error.suggestions:
            return f"{str(error)} {ErrorMessages.INPUT_SUGGESTIONS.format(suggestions=', '.join(error.suggestions))}"
        
        return str(error)


# Global error handler instance
error_handler = ErrorHandler()


def handle_errors(func: Callable) -> Callable:
    """Decorator to handle errors in functions."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            context = {
                'function': func.__name__,
                'args': str(args),
                'kwargs': str(kwargs)
            }
            user_message = error_handler.handle_error(e, context)
            
            # Re-raise as WeatherDashboardError if it's not already
            if not isinstance(e, WeatherDashboardError):
                raise WeatherDashboardError(user_message) from e
            
            raise
    
    return wrapper


def safe_execute(func: Callable, *args, default_return: Any = None, **kwargs) -> Any:
    """
    Safely execute a function and return default value on error.
    
    Args:
        func: Function to execute
        *args: Function arguments
        default_return: Value to return on error
        **kwargs: Function keyword arguments
        
    Returns:
        Function result or default_return on error
    """
    try:
        return func(*args, **kwargs)
    except Exception as e:
        context = {
            'function': func.__name__,
            'args': str(args),
            'kwargs': str(kwargs)
        }
        error_handler.handle_error(e, context)
        return default_return


def validate_input(value: Any, field_name: str, validation_func: Callable, **validation_kwargs) -> None:
    """
    Validate input and raise ValidationError if invalid.
    
    Args:
        value: Value to validate
        field_name: Name of the field being validated
        validation_func: Function to perform validation
        **validation_kwargs: Additional validation parameters
        
    Raises:
        ValidationError: If validation fails
    """
    try:
        if not validation_func(value, **validation_kwargs):
            raise ValidationError(
                f"Invalid {field_name}: {value}",
                field=field_name,
                value=value,
                validation_type=validation_func.__name__
            )
    except Exception as e:
        if isinstance(e, ValidationError):
            raise
        raise ValidationError(
            f"Validation error for {field_name}: {e}",
            field=field_name,
            value=value,
            validation_type=validation_func.__name__
        ) from e 