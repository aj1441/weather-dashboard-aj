# Weather Dashboard API Reference

## Table of Contents
1. [Core Modules](#core-modules)
2. [GUI Components](#gui-components)
3. [Services](#services)
4. [Utilities](#utilities)
5. [Data Models](#data-models)
6. [Configuration](#configuration)
7. [Decorators](#decorators)
8. [Error Handling](#error-handling)

## Core Modules

### Configuration (`config.py`)

#### `Config` Class
Main configuration class using dataclasses for type safety.

```python
@dataclass
class Config:
    api_key: str
    base_url: str = "https://api.openweathermap.org/data/2.5/weather"
    forecast_url: str = "https://api.openweathermap.org/data/2.5/forecast"
    seven_day_history_url: str = "https://history.openweathermap.org/data/2.5/history/city"
    units: str = "imperial"
    database_path: str = "data/weather.db"
    request_timeout: int = 10
    max_retries: int = 3
    min_request_interval: float = 1.0
    log_level: str = "INFO"
```

**Methods:**
- `from_environment()` → `Config`: Load configuration from environment variables
- `__post_init__()`: Validate configuration after initialization

**Example:**
```python
from config import Config

# Load from environment
config = Config.from_environment()

# Access configuration
api_key = config.api_key
timeout = config.request_timeout
```

### Weather API (`core/api.py`)

#### `WeatherAPI` Class
Main API client for weather data retrieval with built-in caching and retry logic.

```python
class WeatherAPI:
    def __init__(self, config: Config)
```

**Methods:**

##### `get_current_weather(city: str) → WeatherData`
Get current weather for a specified city.

**Parameters:**
- `city` (str): City name or location identifier

**Returns:**
- `WeatherData`: Current weather information

**Raises:**
- `APIError`: If API request fails
- `ValidationError`: If city name is invalid

**Example:**
```python
api = WeatherAPI(config)
weather = api.get_current_weather("New York")
print(f"Temperature: {weather.temperature}°F")
```

##### `get_forecast(city: str) → List[ForecastData]`
Get 7-day weather forecast for a city.

**Parameters:**
- `city` (str): City name or location identifier

**Returns:**
- `List[ForecastData]`: List of forecast data points

**Example:**
```python
forecast = api.get_forecast("London")
for day in forecast:
    print(f"{day.date}: {day.temp_min}°F - {day.temp_max}°F")
```

##### `search_location(query: str) → List[LocationData]`
Search for locations by name.

**Parameters:**
- `query` (str): Location search query

**Returns:**
- `List[LocationData]`: List of matching locations

**Example:**
```python
locations = api.search_location("New York")
for location in locations:
    print(f"{location.name}, {location.country}")
```

### Historical Data API (`core/open_meteo_historical.py`)

#### `OpenMeteoHistoricalAPI` Class
API client for historical weather data using Open-Meteo service.

```python
class OpenMeteoHistoricalAPI:
    def __init__(self)
```

**Methods:**

##### `get_historical_data(lat: float, lon: float, start_date: str, end_date: str) → HistoricalWeatherData`
Get historical weather data for a location and date range.

**Parameters:**
- `lat` (float): Latitude coordinate
- `lon` (float): Longitude coordinate
- `start_date` (str): Start date in YYYY-MM-DD format
- `end_date` (str): End date in YYYY-MM-DD format

**Returns:**
- `HistoricalWeatherData`: Historical weather information

**Example:**
```python
historical_api = OpenMeteoHistoricalAPI()
data = historical_api.get_historical_data(
    lat=40.7128, lon=-74.0060,
    start_date="2023-01-01",
    end_date="2023-01-31"
)
```

### Data Validation (`core/data_validator.py`)

#### `WeatherDataValidator` Class
Comprehensive data validation for weather information.

```python
class WeatherDataValidator:
    @staticmethod
    def validate_temperature(temp: float) → bool
    @staticmethod
    def validate_humidity(humidity: int) → bool
    @staticmethod
    def validate_pressure(pressure: float) → bool
    @staticmethod
    def validate_wind_speed(speed: float) → bool
    @staticmethod
    def validate_city_name(city: str) → bool
```

**Methods:**

##### `validate_weather_data(data: dict) → bool`
Validate complete weather data structure.

**Parameters:**
- `data` (dict): Weather data dictionary

**Returns:**
- `bool`: True if data is valid

**Example:**
```python
validator = WeatherDataValidator()
is_valid = validator.validate_weather_data(weather_dict)
```

### Database Handler (`core/data_handler.py`)

#### `DatabaseHandler` Class
SQLite database operations with connection pooling and transaction support.

```python
class DatabaseHandler:
    def __init__(self, db_path: str)
```

**Methods:**

##### `save_weather_data(data: WeatherData) → bool`
Save weather data to database.

**Parameters:**
- `data` (WeatherData): Weather data to save

**Returns:**
- `bool`: True if save successful

##### `get_saved_locations() → List[str]`
Retrieve list of saved locations.

**Returns:**
- `List[str]`: List of saved city names

##### `save_location(city: str) → bool`
Save a new location to favorites.

**Parameters:**
- `city` (str): City name to save

**Returns:**
- `bool`: True if save successful

##### `remove_location(city: str) → bool`
Remove a location from favorites.

**Parameters:**
- `city` (str): City name to remove

**Returns:**
- `bool`: True if removal successful

**Example:**
```python
db = DatabaseHandler("data/weather.db")
db.save_location("New York")
locations = db.get_saved_locations()
```

### Auto Theme System (`core/auto_theme.py`)

#### `AutoThemeManager` Class
Intelligent theme switching based on sunrise/sunset times.

```python
class AutoThemeManager:
    def __init__(self, config: Config)
```

**Methods:**

##### `get_sunrise_sunset(lat: float, lon: float) → Tuple[str, str]`
Get sunrise and sunset times for a location.

**Parameters:**
- `lat` (float): Latitude coordinate
- `lon` (float): Longitude coordinate

**Returns:**
- `Tuple[str, str]`: (sunrise_time, sunset_time)

##### `should_use_dark_theme(lat: float, lon: float) → bool`
Determine if dark theme should be used based on current time and location.

**Parameters:**
- `lat` (float): Latitude coordinate
- `lon` (float): Longitude coordinate

**Returns:**
- `bool`: True if dark theme should be used

**Example:**
```python
theme_manager = AutoThemeManager(config)
is_dark = theme_manager.should_use_dark_theme(40.7128, -74.0060)
```

### Theme Manager (`core/theme_manager.py`)

#### `ThemeManager` Class
Theme registration and switching functionality.

```python
class ThemeManager:
    def __init__(self)
```

**Methods:**

##### `register_theme(name: str, theme_config: dict) → None`
Register a new theme with the application.

**Parameters:**
- `name` (str): Theme name
- `theme_config` (dict): Theme configuration

##### `switch_theme(theme_name: str) → bool`
Switch to a specific theme.

**Parameters:**
- `theme_name` (str): Name of theme to switch to

**Returns:**
- `bool`: True if switch successful

##### `get_available_themes() → List[str]`
Get list of available themes.

**Returns:**
- `List[str]`: List of theme names

**Example:**
```python
theme_manager = ThemeManager()
theme_manager.switch_theme("aj_darkly")
themes = theme_manager.get_available_themes()
```

## GUI Components

### Main Window (`gui/main_window.py`)

#### `TabbedWeatherDashboard` Class
Main application window with tabbed interface.

```python
class TabbedWeatherDashboard:
    def __init__(self, config: Config)
```

**Methods:**

##### `setup_tabs() → None`
Initialize all application tabs.

##### `update_weather_display(data: WeatherData) → None`
Update weather display with new data.

**Parameters:**
- `data` (WeatherData): Weather data to display

##### `show_error(message: str) → None`
Display error message to user.

**Parameters:**
- `message` (str): Error message to display

### Weather Display Component (`gui/components/weather_display.py`)

#### `WeatherDisplayComponent` Class
Reusable component for displaying weather information.

```python
class WeatherDisplayComponent(ttk.Frame):
    def __init__(self, parent, **kwargs)
```

**Methods:**

##### `update_display(data: WeatherData) → None`
Update component with new weather data.

**Parameters:**
- `data` (WeatherData): Weather data to display

##### `clear_display() → None`
Clear all displayed information.

##### `set_loading_state(loading: bool) → None`
Set loading state with spinner.

**Parameters:**
- `loading` (bool): True to show loading spinner

### Theme Component (`gui/components/theme_component.py`)

#### `ThemeComponent` Class
Theme selection and control component.

```python
class ThemeComponent(ttk.Frame):
    def __init__(self, parent, theme_manager: ThemeManager, **kwargs)
```

**Methods:**

##### `setup_theme_controls() → None`
Initialize theme control buttons.

##### `on_theme_change(theme_name: str) → None`
Handle theme change events.

**Parameters:**
- `theme_name` (str): Name of selected theme

##### `toggle_auto_mode() → None`
Toggle automatic theme switching.

### Saved Cities Component (`gui/components/saved_cities.py`)

#### `SavedCitiesComponent` Class
Component for managing saved locations.

```python
class SavedCitiesComponent(ttk.Frame):
    def __init__(self, parent, db_handler: DatabaseHandler, **kwargs)
```

**Methods:**

##### `load_saved_cities() → None`
Load and display saved cities.

##### `add_city(city: str) → None`
Add a new city to saved list.

**Parameters:**
- `city` (str): City name to add

##### `remove_city(city: str) → None`
Remove a city from saved list.

**Parameters:**
- `city` (str): City name to remove

##### `on_city_selected(city: str) → None`
Handle city selection events.

**Parameters:**
- `city` (str): Selected city name

## Services

### Weather Service (`services/weather_service.py`)

#### `WeatherService` Class
Business logic service for weather operations.

```python
class WeatherService:
    def __init__(self, api: WeatherAPI, db_handler: DatabaseHandler)
```

**Methods:**

##### `get_weather_for_city(city: str) → WeatherData`
Get weather data for a city with caching.

**Parameters:**
- `city` (str): City name

**Returns:**
- `WeatherData`: Weather information

##### `get_forecast_for_city(city: str) → List[ForecastData]`
Get forecast data for a city.

**Parameters:**
- `city` (str): City name

**Returns:**
- `List[ForecastData]`: Forecast data

##### `save_city_to_favorites(city: str) → bool`
Save city to user's favorites.

**Parameters:**
- `city` (str): City name to save

**Returns:**
- `bool`: Success status

### Location Service (`services/location_service.py`)

#### `LocationService` Class
Location management and geocoding service.

```python
class LocationService:
    def __init__(self, api: WeatherAPI)
```

**Methods:**

##### `search_locations(query: str) → List[LocationData]`
Search for locations by name.

**Parameters:**
- `query` (str): Search query

**Returns:**
- `List[LocationData]`: Matching locations

##### `get_location_coordinates(city: str) → Tuple[float, float]`
Get coordinates for a city.

**Parameters:**
- `city` (str): City name

**Returns:**
- `Tuple[float, float]`: (latitude, longitude)

##### `validate_location(city: str) → bool`
Validate if a city exists.

**Parameters:**
- `city` (str): City name to validate

**Returns:**
- `bool`: True if city is valid

## Utilities

### Conversion Utilities (`utils/conversion/conversion_utils.py`)

#### Temperature Conversion Functions

```python
def celsius_to_fahrenheit(celsius: float) → float
def fahrenheit_to_celsius(fahrenheit: float) → float
def kelvin_to_celsius(kelvin: float) → float
def kelvin_to_fahrenheit(kelvin: float) → float
```

**Parameters:**
- Temperature value in source unit

**Returns:**
- Temperature value in target unit

**Example:**
```python
from utils.conversion.conversion_utils import celsius_to_fahrenheit

fahrenheit = celsius_to_fahrenheit(25.0)  # 77.0
```

#### Unit Conversion Functions

```python
def meters_per_second_to_mph(mps: float) → float
def mph_to_meters_per_second(mph: float) → float
def hectopascals_to_inches_hg(hpa: float) → float
def inches_hg_to_hectopascals(inches: float) → float
```

### Performance Optimizer (`utils/performance/performance_optimizer.py`)

#### `PerformanceOptimizer` Class
Performance monitoring and optimization utilities.

```python
class PerformanceOptimizer:
    def __init__(self)
```

**Methods:**

##### `monitor_function(func: Callable) → Callable`
Decorator to monitor function performance.

**Parameters:**
- `func` (Callable): Function to monitor

**Returns:**
- `Callable`: Wrapped function

##### `get_performance_stats() → Dict[str, float]`
Get performance statistics.

**Returns:**
- `Dict[str, float]`: Performance metrics

##### `cleanup_performance_data() → None`
Clean up performance monitoring data.

## Data Models

### Weather Data Models

#### `WeatherData` Class
Data structure for current weather information.

```python
@dataclass
class WeatherData:
    city: str
    temperature: Optional[float]
    feels_like: Optional[float]
    humidity: Optional[int]
    pressure: Optional[float]
    wind_speed: Optional[float]
    wind_direction: Optional[int]
    weather_main: Optional[str]
    weather_description: Optional[str]
    visibility: Optional[int]
    uv_index: Optional[float]
    sunrise: Optional[str]
    sunset: Optional[str]
    last_updated: Optional[str]
```

**Methods:**
- `to_dict() → dict`: Convert to dictionary
- `from_api_response(data: dict) → WeatherData`: Create from API response
- `from_dict(data: dict) → WeatherData`: Create from dictionary

#### `ForecastData` Class
Data structure for weather forecast information.

```python
@dataclass
class ForecastData:
    city: str
    forecast_date: datetime
    temp_min: Optional[float]
    temp_max: Optional[float]
    temp_day: Optional[float]
    temp_night: Optional[float]
    humidity: Optional[int]
    weather_main: Optional[str]
    weather_description: Optional[str]
    wind_speed: Optional[float]
    wind_direction: Optional[int]
    precipitation_chance: Optional[float]
```

#### `HistoricalWeatherData` Class
Data structure for historical weather information.

```python
@dataclass
class HistoricalWeatherData:
    location: str
    start_date: str
    end_date: str
    daily_data: List[DailyWeatherData]
    metadata: Dict[str, Any]
```

#### `LocationData` Class
Data structure for location information.

```python
@dataclass
class LocationData:
    name: str
    country: str
    state: Optional[str]
    lat: float
    lon: float
    timezone: Optional[str]
```

### Database Models

#### `SavedLocation` Class
Database model for saved locations.

```python
@dataclass
class SavedLocation:
    id: int
    city_name: str
    country: str
    latitude: float
    longitude: float
    created_at: datetime
    last_accessed: datetime
```

#### `WeatherRecord` Class
Database model for weather records.

```python
@dataclass
class WeatherRecord:
    id: int
    city_name: str
    temperature: float
    humidity: int
    pressure: float
    wind_speed: float
    weather_description: str
    recorded_at: datetime
```

## Configuration

### Environment Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `API_KEY` | str | - | OpenWeatherMap API key (required) |
| `BASE_URL` | str | OpenWeatherMap URL | Weather API base URL |
| `FORECAST_URL` | str | OpenWeatherMap URL | Forecast API URL |
| `UNITS` | str | `imperial` | Temperature units (imperial/metric) |
| `DATABASE_PATH` | str | `data/weather.db` | SQLite database path |
| `REQUEST_TIMEOUT` | int | `10` | API request timeout (seconds) |
| `MAX_RETRIES` | int | `3` | Maximum retry attempts |
| `MIN_REQUEST_INTERVAL` | float | `1.0` | Rate limiting interval (seconds) |
| `LOG_LEVEL` | str | `INFO` | Logging level |

### Configuration Methods

#### `Config.from_environment() → Config`
Load configuration from environment variables with validation.

**Returns:**
- `Config`: Validated configuration object

**Raises:**
- `ValueError`: If required configuration is missing or invalid

**Example:**
```python
try:
    config = Config.from_environment()
except ValueError as e:
    print(f"Configuration error: {e}")
```

## Decorators

### Rate Limiting (`utils/decorators/rate_limiting.py`)

#### `rate_limit(min_interval: float = 1.0)`
Decorator to enforce rate limiting on API calls.

**Parameters:**
- `min_interval` (float): Minimum time between calls (seconds)

**Example:**
```python
@rate_limit(min_interval=1.0)
def api_call():
    # API call implementation
    pass
```

### Caching (`utils/decorators/caching.py`)

#### `cache_response(ttl: int = 3600)`
Decorator to cache API responses.

**Parameters:**
- `ttl` (int): Time to live in seconds

**Example:**
```python
@cache_response(ttl=3600)  # 1 hour cache
def get_weather_data():
    # API call implementation
    pass
```

### Retry Logic (`utils/decorators/retry.py`)

#### `retry_on_error(max_retries: int = 3, delay: float = 1.0)`
Decorator to automatically retry failed operations.

**Parameters:**
- `max_retries` (int): Maximum retry attempts
- `delay` (float): Delay between retries (seconds)

**Example:**
```python
@retry_on_error(max_retries=3, delay=1.0)
def unreliable_api_call():
    # API call that may fail
    pass
```

### Validation (`utils/decorators/validation.py`)

#### `validate_input(validator_func: Callable)`
Decorator to validate function inputs.

**Parameters:**
- `validator_func` (Callable): Validation function

**Example:**
```python
def validate_city_name(city: str) -> bool:
    return len(city) > 0 and city.isalpha()

@validate_input(validate_city_name)
def get_weather(city: str):
    # Function implementation
    pass
```

## Error Handling

### Exception Hierarchy

```python
class WeatherDashboardError(Exception):
    """Base exception for weather dashboard."""
    pass

class APIError(WeatherDashboardError):
    """Raised when API requests fail."""
    pass

class ValidationError(WeatherDashboardError):
    """Raised when data validation fails."""
    pass

class ConfigurationError(WeatherDashboardError):
    """Raised when configuration is invalid."""
    pass

class DatabaseError(WeatherDashboardError):
    """Raised when database operations fail."""
    pass

class ThemeError(WeatherDashboardError):
    """Raised when theme operations fail."""
    pass
```

### Error Handling Patterns

#### API Error Handling
```python
try:
    weather_data = api.get_current_weather(city)
except APIError as e:
    logger.error(f"API error: {e}")
    # Handle API error
except ValidationError as e:
    logger.error(f"Validation error: {e}")
    # Handle validation error
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    # Handle unexpected error
```

#### Database Error Handling
```python
try:
    db_handler.save_weather_data(data)
except DatabaseError as e:
    logger.error(f"Database error: {e}")
    # Handle database error
```

#### Configuration Error Handling
```python
try:
    config = Config.from_environment()
except ConfigurationError as e:
    logger.error(f"Configuration error: {e}")
    # Handle configuration error
```

### Error Recovery Strategies

#### Automatic Retry
```python
@retry_on_error(max_retries=3, delay=1.0)
def api_call_with_retry():
    # API call that will be retried on failure
    pass
```

#### Fallback Values
```python
def get_weather_with_fallback(city: str) -> WeatherData:
    try:
        return api.get_current_weather(city)
    except APIError:
        # Return cached data or default values
        return get_cached_weather_data(city)
```

#### Graceful Degradation
```python
def get_weather_features(city: str) -> Dict[str, Any]:
    features = {}
    
    try:
        features['current'] = api.get_current_weather(city)
    except APIError:
        features['current'] = None
    
    try:
        features['forecast'] = api.get_forecast(city)
    except APIError:
        features['forecast'] = []
    
    return features
```

---

*This API reference provides comprehensive documentation for all classes, methods, and interfaces in the Weather Dashboard application. For implementation details, refer to the source code and developer guide.*