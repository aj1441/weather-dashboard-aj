import os
import logging
from dataclasses import dataclass
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

@dataclass
class Config:
    """Application configuration with secure defaults for weather dashboard."""
    
    # Required settings
    api_key: str
    
    # API settings with defaults
    base_url: str = "https://api.openweathermap.org/data/2.5/weather"
    units: str = "imperial"
    
    # Database settings
    database_path: str = "data/weather.db"
    
    # Performance settings with instructor's suggestions
    request_timeout: int = 10
    max_retries: int = 3
    min_request_interval: float = 1.0  # seconds between requests (rate limiting)
    
    # Application settings
    log_level: str = "INFO"
    
    def __post_init__(self):
        """Validate configuration after initialization"""
        if not self.api_key:
            raise ValueError("API key cannot be empty")
        
        # Validate numeric ranges
        if self.request_timeout <= 0:
            raise ValueError("Request timeout must be positive")
        
        if self.max_retries < 1:
            raise ValueError("Max retries must be at least 1")
        
        if self.min_request_interval < 0:
            raise ValueError("Min request interval cannot be negative")
    
    @classmethod
    def from_environment(cls):
        """Create config from environment variables with validation and better error messages."""
        
        # Try multiple environment variable names for API key
        api_key = (os.getenv('API_KEY') or 
                  os.getenv('WEATHER_API_KEY') or 
                  os.getenv('OPENWEATHER_API_KEY'))
        
        if not api_key:
            raise ValueError(
                "Weather API key is required. Please set one of:\n"
                "  - API_KEY\n"
                "  - WEATHER_API_KEY\n"
                "  - OPENWEATHER_API_KEY\n"
                "in your environment or .env file"
            )
        
        try:
            config = cls(
                api_key=api_key,
                base_url=os.getenv('BASE_URL', cls.base_url),
                units=os.getenv('UNITS', cls.units),
                database_path=os.getenv('DATABASE_PATH', cls.database_path),
                request_timeout=int(os.getenv('REQUEST_TIMEOUT', str(cls.request_timeout))),
                max_retries=int(os.getenv('MAX_RETRIES', str(cls.max_retries))),
                min_request_interval=float(os.getenv('MIN_REQUEST_INTERVAL', str(cls.min_request_interval))),
                log_level=os.getenv('LOG_LEVEL', cls.log_level)
            )
            
            return config
            
        except ValueError as e:
            if "invalid literal" in str(e):
                raise ValueError(f"Invalid numeric value in environment variables: {e}")
            raise

# Legacy support - keep your existing variables for backward compatibility
try:
    _config = Config.from_environment()
    API_KEY = _config.api_key
    BASE_URL = _config.base_url
    UNITS = _config.units
except ValueError:
    # Fallback for development with updated API key
    API_KEY = "af9ee38eacf13ac8c9fdf63dbc29893b"
    BASE_URL = "https://api.openweathermap.org/data/2.5/weather"
    UNITS = "imperial"
