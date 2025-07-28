"""
Custom exceptions for the weather dashboard application.

This module defines application-specific exceptions that provide
better error handling and user feedback throughout the application.
"""

from typing import Optional, Dict, Any


class WeatherDashboardError(Exception):
    """Base exception for all weather dashboard errors."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        """Initialize the exception with message and optional details."""
        super().__init__(message)
        self.message = message
        self.details = details or {}
    
    def __str__(self) -> str:
        """Return string representation of the exception."""
        return self.message


class APIError(WeatherDashboardError):
    """Exception raised for API-related errors."""
    
    def __init__(self, message: str, api_name: str = "unknown", status_code: Optional[int] = None, response_data: Optional[Dict[str, Any]] = None):
        """Initialize API error with API details."""
        super().__init__(message, {
            'api_name': api_name,
            'status_code': status_code,
            'response_data': response_data
        })
        self.api_name = api_name
        self.status_code = status_code
        self.response_data = response_data


class WeatherAPIError(APIError):
    """Exception raised for weather API specific errors."""
    
    def __init__(self, message: str, city: Optional[str] = None, status_code: Optional[int] = None, response_data: Optional[Dict[str, Any]] = None):
        """Initialize weather API error."""
        super().__init__(message, "weather_api", status_code, response_data)
        self.city = city


class GeocodingAPIError(APIError):
    """Exception raised for geocoding API errors."""
    
    def __init__(self, message: str, location: Optional[str] = None, status_code: Optional[int] = None, response_data: Optional[Dict[str, Any]] = None):
        """Initialize geocoding API error."""
        super().__init__(message, "geocoding_api", status_code, response_data)
        self.location = location


class ValidationError(WeatherDashboardError):
    """Exception raised for data validation errors."""
    
    def __init__(self, message: str, field: Optional[str] = None, value: Optional[Any] = None, validation_type: Optional[str] = None):
        """Initialize validation error."""
        super().__init__(message, {
            'field': field,
            'value': value,
            'validation_type': validation_type
        })
        self.field = field
        self.value = value
        self.validation_type = validation_type


class DataError(WeatherDashboardError):
    """Exception raised for data-related errors."""
    
    def __init__(self, message: str, operation: Optional[str] = None, data_type: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        """Initialize data error."""
        super().__init__(message, {
            'operation': operation,
            'data_type': data_type,
            **(details or {})
        })
        self.operation = operation
        self.data_type = data_type


class ConfigurationError(WeatherDashboardError):
    """Exception raised for configuration-related errors."""
    
    def __init__(self, message: str, config_key: Optional[str] = None, config_value: Optional[Any] = None):
        """Initialize configuration error."""
        super().__init__(message, {
            'config_key': config_key,
            'config_value': config_value
        })
        self.config_key = config_key
        self.config_value = config_value


class ThemeError(WeatherDashboardError):
    """Exception raised for theme-related errors."""
    
    def __init__(self, message: str, theme_name: Optional[str] = None, theme_type: Optional[str] = None):
        """Initialize theme error."""
        super().__init__(message, {
            'theme_name': theme_name,
            'theme_type': theme_type
        })
        self.theme_name = theme_name
        self.theme_type = theme_type


class NetworkError(WeatherDashboardError):
    """Exception raised for network-related errors."""
    
    def __init__(self, message: str, url: Optional[str] = None, timeout: Optional[float] = None, connection_type: Optional[str] = None):
        """Initialize network error."""
        super().__init__(message, {
            'url': url,
            'timeout': timeout,
            'connection_type': connection_type
        })
        self.url = url
        self.timeout = timeout
        self.connection_type = connection_type


class RateLimitError(APIError):
    """Exception raised when API rate limits are exceeded."""
    
    def __init__(self, message: str, api_name: str = "unknown", retry_after: Optional[int] = None):
        """Initialize rate limit error."""
        super().__init__(message, api_name, 429, {'retry_after': retry_after})
        self.retry_after = retry_after


class ServiceUnavailableError(APIError):
    """Exception raised when a service is temporarily unavailable."""
    
    def __init__(self, message: str, api_name: str = "unknown", retry_after: Optional[int] = None):
        """Initialize service unavailable error."""
        super().__init__(message, api_name, 503, {'retry_after': retry_after})
        self.retry_after = retry_after


class UserInputError(WeatherDashboardError):
    """Exception raised for invalid user input."""
    
    def __init__(self, message: str, input_field: Optional[str] = None, input_value: Optional[Any] = None, suggestions: Optional[list] = None):
        """Initialize user input error."""
        super().__init__(message, {
            'input_field': input_field,
            'input_value': input_value,
            'suggestions': suggestions
        })
        self.input_field = input_field
        self.input_value = input_value
        self.suggestions = suggestions


class DatabaseError(DataError):
    """Exception raised for database-related errors."""
    
    def __init__(self, message: str, operation: Optional[str] = None, table: Optional[str] = None, sql_error: Optional[str] = None):
        """Initialize database error."""
        super().__init__(message, operation, "database", {
            'table': table,
            'sql_error': sql_error
        })
        self.table = table
        self.sql_error = sql_error


class FileError(DataError):
    """Exception raised for file-related errors."""
    
    def __init__(self, message: str, operation: Optional[str] = None, file_path: Optional[str] = None, file_type: Optional[str] = None):
        """Initialize file error."""
        super().__init__(message, operation, "file", {
            'file_path': file_path,
            'file_type': file_type
        })
        self.file_path = file_path
        self.file_type = file_type


# Error message templates for consistent error reporting
class ErrorMessages:
    """Standardized error messages for the application."""
    
    # API Errors
    API_CONNECTION_FAILED = "Failed to connect to {api_name}. Please check your internet connection."
    API_RATE_LIMITED = "API rate limit exceeded. Please wait {retry_after} seconds before trying again."
    API_SERVICE_UNAVAILABLE = "Service temporarily unavailable. Please try again later."
    API_INVALID_RESPONSE = "Received invalid response from {api_name}."
    API_AUTHENTICATION_FAILED = "Authentication failed for {api_name}. Please check your API key."
    
    # Weather API Errors
    WEATHER_CITY_NOT_FOUND = "City '{city}' not found. Please check the spelling or try a different city."
    WEATHER_API_ERROR = "Error fetching weather data for '{city}': {error}"
    WEATHER_NO_DATA = "No weather data available for '{city}'."
    
    # Geocoding Errors
    GEOCODING_LOCATION_NOT_FOUND = "Location '{location}' not found. Please check the spelling."
    GEOCODING_MULTIPLE_RESULTS = "Multiple locations found for '{location}'. Please be more specific."
    
    # Validation Errors
    VALIDATION_INVALID_CITY = "Invalid city name. Please use only letters, spaces, hyphens, and apostrophes."
    VALIDATION_INVALID_STATE = "Invalid state code. Please use a 2-letter state abbreviation."
    VALIDATION_INVALID_TEMPERATURE = "Invalid temperature value: {value}."
    VALIDATION_INVALID_HUMIDITY = "Invalid humidity value. Must be between 0 and 100."
    VALIDATION_INVALID_PRESSURE = "Invalid pressure value. Must be between 800 and 1200 hPa."
    VALIDATION_INVALID_WIND_SPEED = "Invalid wind speed value. Must be non-negative."
    
    # Data Errors
    DATA_SAVE_FAILED = "Failed to save {data_type} data."
    DATA_LOAD_FAILED = "Failed to load {data_type} data."
    DATA_DELETE_FAILED = "Failed to delete {data_type} data."
    DATA_NOT_FOUND = "{data_type} data not found."
    
    # Configuration Errors
    CONFIG_MISSING_KEY = "Missing required configuration key: {key}."
    CONFIG_INVALID_VALUE = "Invalid configuration value for {key}: {value}."
    CONFIG_FILE_NOT_FOUND = "Configuration file not found: {file_path}."
    
    # Theme Errors
    THEME_NOT_FOUND = "Theme '{theme_name}' not found."
    THEME_APPLY_FAILED = "Failed to apply theme '{theme_name}'."
    THEME_INVALID_TYPE = "Invalid theme type: {theme_type}."
    
    # Network Errors
    NETWORK_TIMEOUT = "Network request timed out after {timeout} seconds."
    NETWORK_CONNECTION_FAILED = "Failed to establish network connection."
    NETWORK_DNS_ERROR = "DNS resolution failed for {url}."
    
    # User Input Errors
    INPUT_EMPTY_CITY = "City name cannot be empty."
    INPUT_TOO_LONG = "Input too long. Maximum length is {max_length} characters."
    INPUT_INVALID_CHARACTERS = "Input contains invalid characters."
    INPUT_SUGGESTIONS = "Did you mean: {suggestions}?"
    
    # Database Errors
    DB_CONNECTION_FAILED = "Failed to connect to database."
    DB_QUERY_FAILED = "Database query failed: {sql_error}."
    DB_TABLE_NOT_FOUND = "Database table '{table}' not found."
    
    # File Errors
    FILE_NOT_FOUND = "File not found: {file_path}."
    FILE_PERMISSION_DENIED = "Permission denied accessing file: {file_path}."
    FILE_CORRUPTED = "File appears to be corrupted: {file_path}."
    FILE_TOO_LARGE = "File too large: {file_path}." 