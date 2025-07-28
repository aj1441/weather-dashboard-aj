# Weather Dashboard API Documentation

## Overview

The Weather Dashboard is a comprehensive Python application that provides weather information through a graphical user interface. This document provides detailed API documentation for developers working with the codebase.

## Architecture

The application follows a layered architecture pattern:

```
┌─────────────────┐
│   GUI Layer     │  (tkinter/ttkbootstrap)
├─────────────────┤
│  Service Layer  │  (Business Logic)
├─────────────────┤
│   Core Layer    │  (Data Models & API)
├─────────────────┤
│  Data Layer     │  (Database & Storage)
└─────────────────┘
```

## Core Modules

### 1. Configuration (`config.py`)

The configuration system manages application settings using environment variables.

#### `Config` Class

```python
@dataclass
class Config:
    api_key: str                    # Weather API key
    base_url: str                   # API base URL
    forecast_url: str               # Forecast API URL
    seven_day_history_url: str      # Historical data URL
    units: str                      # Temperature units (imperial/metric)
    database_path: str              # Database file path
    request_timeout: int            # API request timeout
    max_retries: int                # Maximum retry attempts
    min_request_interval: float     # Rate limiting interval
    log_level: str                  # Logging level
```

**Usage:**
```python
from config import Config

# Load from environment variables
config = Config.from_environment()

# Access configuration
api_key = config.api_key
timeout = config.request_timeout
```

### 2. Weather Models (`core/weather_models.py`)

Standardized data structures for weather information.

#### `WeatherData` Class

Represents current weather conditions.

```python
@dataclass
class WeatherData:
    city: str                       # City name
    temperature: Optional[float]    # Current temperature
    humidity: Optional[int]         # Humidity percentage
    weather_main: Optional[str]     # Weather condition
    weather_description: Optional[str]  # Detailed description
    # ... additional fields
```

**Methods:**
- `to_dict()`: Convert to dictionary format
- `from_api_response()`: Create from API response
- `from_dict()`: Create from dictionary

#### `ForecastData` Class

Represents weather forecast information.

```python
@dataclass
class ForecastData:
    city: str                       # City name
    forecast_date: datetime         # Forecast date
    temp_min: Optional[float]       # Minimum temperature
    temp_max: Optional[float]       # Maximum temperature
    # ... additional fields
```

#### `ComprehensiveWeatherData` Class

Combines current weather and forecast data.

```python
@dataclass
class ComprehensiveWeatherData:
    current: WeatherData            # Current weather
    forecast: List[ForecastData]    # Forecast data
    location: Dict[str, Any]        # Location information
    api_source: str                 # Data source
```

### 3. API Client (`core/api.py`)

Handles communication with weather APIs.

#### `WeatherAPI` Class

```python
class WeatherAPI:
    def __init__(self, config: Optional[Config] = None) -> None:
        """Initialize API client with configuration."""
    
    def fetch_weather(self, city: str) -> Optional[Dict[str, Any]]:
        """Fetch current weather for a city."""
    
    def get_coordinates(self, city: str, state: str) -> Optional[Dict[str, Any]]:
        """Get coordinates for a city."""
    
    def fetch_comprehensive_weather(self, city: str, state: str, units: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Fetch comprehensive weather data including forecast."""
```

**Features:**
- Rate limiting and retry logic
- Error handling and logging
- Data validation
- Fallback API support

### 4. Data Validation (`core/data_validator.py`)

Validates and cleans weather data.

#### `WeatherDataValidator` Class

```python
class WeatherDataValidator:
    def __init__(self, rules: Optional[ValidationRules] = None, temperature_unit: str = "imperial") -> None:
        """Initialize validator with rules and temperature unit."""
    
    def validate_and_clean_current_weather(self, raw_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Validate and clean current weather data."""
    
    def validate_weather_data(self, data: Dict[str, Any]) -> bool:
        """Validate weather data against rules."""
```

## Service Layer

### 1. Weather Service (`services/weather_service.py`)

Provides high-level weather operations.

#### `WeatherService` Class

```python
class WeatherService:
    def __init__(self, config: Config) -> None:
        """Initialize weather service."""
    
    def get_current_weather(self, city: str, state: Optional[str] = None, units: Optional[str] = None) -> Optional[WeatherData]:
        """Get current weather for a location."""
    
    def get_comprehensive_weather(self, city: str, state: Optional[str] = None, units: Optional[str] = None) -> Optional[ComprehensiveWeatherData]:
        """Get comprehensive weather data including forecast."""
    
    def get_coordinates(self, city: str, state: Optional[str] = None) -> Optional[Dict[str, float]]:
        """Get coordinates for a city."""
    
    def validate_weather_data(self, weather_data: Dict[str, Any]) -> bool:
        """Validate weather data."""
```

### 2. Data Service (`services/data_service.py`)

Handles data persistence operations.

#### `DataService` Class

```python
class DataService:
    def __init__(self, config: Config) -> None:
        """Initialize data service."""
    
    def save_weather_data(self, weather_data: WeatherData) -> bool:
        """Save weather data to storage."""
    
    def save_forecast_data(self, city: str, state: Optional[str], forecast_data: List[ForecastData]) -> bool:
        """Save forecast data to storage."""
    
    def save_city(self, city: str, state: Optional[str] = None, nickname: Optional[str] = None) -> bool:
        """Save a city to favorites."""
    
    def get_saved_cities(self) -> List[SavedCity]:
        """Get list of saved cities."""
    
    def delete_city(self, city: str, state: Optional[str] = None) -> bool:
        """Delete a saved city."""
```

### 3. Theme Service (`services/theme_service.py`)

Manages application theming.

#### `ThemeService` Class

```python
class ThemeService:
    def __init__(self, config: Config, app_instance=None) -> None:
        """Initialize theme service."""
    
    def apply_theme(self, theme_name: str) -> bool:
        """Apply a specific theme."""
    
    def apply_auto_theme(self) -> bool:
        """Apply automatic theme based on time."""
    
    def toggle_auto_mode(self) -> bool:
        """Toggle automatic theme mode."""
    
    def get_current_theme(self) -> str:
        """Get the currently applied theme."""
```

### 4. Validation Service (`services/validation_service.py`)

Provides data validation utilities.

#### `ValidationService` Class

```python
class ValidationService:
    def __init__(self, config: Config) -> None:
        """Initialize validation service."""
    
    def validate_weather_data(self, weather_data: Dict[str, Any]) -> bool:
        """Validate weather data."""
    
    def validate_city_name(self, city: str) -> bool:
        """Validate city name."""
    
    def validate_state_code(self, state: str) -> bool:
        """Validate state code."""
    
    def validate_temperature(self, temperature: float, units: str = "imperial") -> bool:
        """Validate temperature value."""
```

## GUI Components

### 1. Main Window (`gui/tabbed_main_window.py`)

The main application window with tabbed interface.

#### `TabbedWeatherDashboard` Class

```python
class TabbedWeatherDashboard:
    def __init__(self, config: Optional[Any] = None) -> None:
        """Initialize the main dashboard window."""
    
    def setup_gui(self) -> None:
        """Create the tabbed interface."""
    
    def handle_weather_request(self, city: str, state: Optional[str] = None, units: Optional[str] = None, country: Optional[str] = None) -> None:
        """Handle weather data request and display."""
    
    def handle_save_city(self, city_data: Dict[str, Any]) -> None:
        """Handle saving a city."""
    
    def run(self) -> None:
        """Start the application."""
```

### 2. Weather Display Component (`gui/components/weather_display_component.py`)

Displays current weather information.

#### `WeatherDisplayComponent` Class

```python
class WeatherDisplayComponent:
    def __init__(self, parent: tb.Frame) -> None:
        """Initialize weather display component."""
    
    def update_weather_display(self, weather_data: Dict[str, Any], temp_unit: str = "imperial") -> None:
        """Update the display with new weather data."""
    
    def show_error(self, error_message: str) -> None:
        """Display error message."""
    
    def get_current_data(self) -> Optional[Dict[str, Any]]:
        """Get current weather data."""
```

### 3. Weather Input Component (`gui/components/weather_input_component.py`)

Handles user input for weather requests.

#### `WeatherInputComponent` Class

```python
class WeatherInputComponent:
    def __init__(self, parent: tb.Frame) -> None:
        """Initialize weather input component."""
    
    def toggle_units(self) -> None:
        """Toggle between Fahrenheit and Celsius."""
    
    def on_get_weather(self) -> None:
        """Handle get weather button click."""
    
    def get_city(self) -> str:
        """Get the current city value."""
    
    def get_state(self) -> str:
        """Get the current state value."""
    
    def get_units(self) -> str:
        """Get the current units."""
```

## Error Handling

### Custom Exceptions (`core/exceptions.py`)

The application uses custom exceptions for better error handling:

- `WeatherDashboardError`: Base exception class
- `APIError`: API-related errors
- `WeatherAPIError`: Weather API specific errors
- `ValidationError`: Data validation errors
- `DataError`: Data-related errors
- `ConfigurationError`: Configuration errors
- `ThemeError`: Theme-related errors
- `NetworkError`: Network-related errors
- `UserInputError`: User input validation errors

### Error Handler (`utils/error_handler.py`)

Centralized error handling with user-friendly messages.

```python
class ErrorHandler:
    def handle_error(self, error: Exception, context: Optional[Dict[str, Any]] = None) -> str:
        """Handle an error and return a user-friendly message."""
    
    def handle_api_error(self, error: APIError) -> str:
        """Handle API-specific errors."""
    
    def handle_validation_error(self, error: ValidationError) -> str:
        """Handle validation errors."""
```

## Utilities

### 1. Conversion Utils (`utils/conversion_utils.py`)

Temperature and unit conversion utilities.

### 2. Weather Utils (`utils/weather_utils.py`)

Weather data parsing and formatting utilities.

### 3. State Utils (`utils/state_utils.py`)

State abbreviation normalization utilities.

### 4. Unit Label Utils (`utils/unit_label_utils.py`)

Unit label formatting utilities.

### 5. Decorators (`utils/decorators.py`)

Utility decorators for rate limiting, retry logic, and logging.

## Testing

### Test Structure

The application includes comprehensive tests:

- `test/test_services.py`: Service layer tests
- `test/test_weather_models.py`: Data model tests
- `test/run_tests.py`: Test runner script

### Running Tests

```bash
# Run all tests
python test/run_tests.py

# Run specific test categories
python test/run_tests.py services
python test/run_tests.py models
```

## Usage Examples

### Basic Weather Retrieval

```python
from config import Config
from services import WeatherService

# Initialize
config = Config.from_environment()
weather_service = WeatherService(config)

# Get current weather
weather = weather_service.get_current_weather("New York", "NY")
if weather:
    print(f"Temperature: {weather.temperature}°F")
    print(f"Humidity: {weather.humidity}%")
```

### Data Persistence

```python
from services import DataService
from core.weather_models import WeatherData

# Initialize
data_service = DataService(config)

# Save weather data
weather = WeatherData(city="Los Angeles", temperature=75.0)
success = data_service.save_weather_data(weather)

# Get saved cities
saved_cities = data_service.get_saved_cities()
for city in saved_cities:
    print(f"Saved: {city.display_name}")
```

### Theme Management

```python
from services import ThemeService

# Initialize
theme_service = ThemeService(config, app_instance)

# Apply theme
theme_service.apply_theme("dark_theme")

# Toggle auto mode
auto_enabled = theme_service.toggle_auto_mode()
```

## Configuration

### Environment Variables

The application uses the following environment variables:

- `API_KEY`: Weather API key (required)
- `WEATHER_API_KEY`: Alternative API key variable
- `OPENWEATHER_API_KEY`: Alternative API key variable
- `BASE_URL`: API base URL
- `UNITS`: Temperature units (imperial/metric)
- `DATABASE_PATH`: Database file path
- `REQUEST_TIMEOUT`: API request timeout
- `MAX_RETRIES`: Maximum retry attempts
- `MIN_REQUEST_INTERVAL`: Rate limiting interval
- `LOG_LEVEL`: Logging level

### .env File Example

```env
API_KEY=your_api_key_here
UNITS=imperial
DATABASE_PATH=data/weather.db
REQUEST_TIMEOUT=10
MAX_RETRIES=3
LOG_LEVEL=INFO
```

## Best Practices

1. **Error Handling**: Always use the error handler for consistent error management
2. **Type Hints**: Use type hints for better code documentation and IDE support
3. **Logging**: Use structured logging with appropriate log levels
4. **Validation**: Validate all user input and API responses
5. **Configuration**: Use environment variables for configuration
6. **Testing**: Write comprehensive tests for all components
7. **Documentation**: Maintain up-to-date docstrings and API documentation

## Contributing

When contributing to the project:

1. Follow the existing code style and patterns
2. Add comprehensive docstrings to new functions and classes
3. Write tests for new functionality
4. Update this documentation for any API changes
5. Use type hints for all new code
6. Handle errors gracefully with appropriate logging 