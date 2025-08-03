# Weather Dashboard Developer Guide

## Table of Contents
1. [Architecture Overview](#architecture-overview)
2. [Project Structure](#project-structure)
3. [Core Components](#core-components)
4. [Development Setup](#development-setup)
5. [Coding Standards](#coding-standards)
6. [Adding New Features](#adding-new-features)
7. [Testing](#testing)
8. [Performance Optimization](#performance-optimization)
9. [API Integration](#api-integration)
10. [Deployment](#deployment)

## Architecture Overview

The Weather Dashboard follows a **layered architecture** pattern with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────────┐
│                    Presentation Layer                      │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐        │
│  │   GUI       │ │   Themes    │ │ Components  │        │
│  │ (tkinter)   │ │ (ttkbootstrap)│ │ (Reusable)  │        │
│  └─────────────┘ └─────────────┘ └─────────────┘        │
├─────────────────────────────────────────────────────────────┤
│                    Business Logic Layer                    │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐        │
│  │   Services  │ │   Handlers  │ │   Managers  │        │
│  │ (API calls) │ │ (Data proc) │ │ (Theme/DB)  │        │
│  └─────────────┘ └─────────────┘ └─────────────┘        │
├─────────────────────────────────────────────────────────────┤
│                      Core Layer                           │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐        │
│  │    Models   │ │   Validators│ │   Utilities │        │
│  │ (Data struct)│ │ (Input val) │ │ (Helpers)   │        │
│  └─────────────┘ └─────────────┘ └─────────────┘        │
├─────────────────────────────────────────────────────────────┤
│                     Data Layer                            │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐        │
│  │   Database  │ │   Cache     │ │   Storage   │        │
│  │ (SQLite)    │ │ (Memory)    │ │ (Files)     │        │
│  └─────────────┘ └─────────────┘ └─────────────┘        │
└─────────────────────────────────────────────────────────────┘
```

### Design Principles

1. **Separation of Concerns**: Each layer has a specific responsibility
2. **Dependency Injection**: Components receive dependencies rather than creating them
3. **Decorator Pattern**: Cross-cutting concerns implemented via decorators
4. **Configuration-Driven**: Settings externalized to configuration files
5. **Error Handling**: Comprehensive error handling at all layers
6. **Performance**: Caching and optimization built into the architecture

## Project Structure

```
weather-dashboard/
├── main.py                     # Application entry point
├── config.py                   # Configuration management
├── requirements.txt            # Python dependencies
├── .env.example               # Environment template
├── .gitignore                 # Git ignore rules
│
├── core/                       # Core business logic
│   ├── __init__.py
│   ├── api.py                 # Weather API client
│   ├── open_meteo_historical.py # Historical data API
│   ├── data_validator.py      # Data validation
│   ├── data_handler.py        # Database operations
│   ├── auto_theme.py          # Auto theme system
│   ├── theme_manager.py       # Theme management
│   ├── custom_themes.py       # Theme definitions
│   └── utils.py              # Utility functions
│
├── gui/                       # User interface
│   ├── __init__.py
│   ├── main_window.py         # Main application window
│   ├── tabbed_main_window.py  # Tabbed interface
│   └── components/           # Reusable GUI components
│       ├── __init__.py
│       ├── theme_component.py
│       ├── weather_display.py
│       ├── saved_cities.py
│       └── historical_data.py
│
├── services/                  # Business logic services
│   ├── __init__.py
│   ├── weather_service.py    # Weather data service
│   ├── location_service.py   # Location management
│   └── theme_service.py      # Theme management service
│
├── utils/                     # Utility modules
│   ├── __init__.py
│   ├── conversion/           # Unit conversion utilities
│   │   ├── __init__.py
│   │   └── conversion_utils.py
│   ├── performance/          # Performance monitoring
│   │   ├── __init__.py
│   │   └── performance_optimizer.py
│   └── decorators/          # Custom decorators
│       ├── __init__.py
│       ├── rate_limiting.py
│       ├── caching.py
│       └── validation.py
│
├── data/                      # Application data
│   ├── weather.db           # SQLite database
│   ├── weather_history.json # Historical data cache
│   ├── user_settings.json   # User preferences
│   └── weather_dashboard.log # Application logs
│
├── test/                      # Test suite
│   ├── __init__.py
│   ├── test_api_data_samples.py
│   ├── test_comprehensive_validation.py
│   ├── test_pop_validation.py
│   └── fixtures/            # Test data
│
├── docs/                      # Documentation
│   ├── USER_GUIDE.md
│   ├── DEVELOPER_GUIDE.md
│   ├── API_DOCUMENTATION.md
│   └── class_docs/
│
├── assets/                    # Static assets
│   ├── icons/               # Weather icons
│   ├── themes/              # Theme assets
│   └── images/              # Application images
│
└── features/                  # Feature modules
    ├── __init__.py
    ├── weather_features.py   # Weather-specific features
    ├── theme_features.py     # Theme-related features
    └── data_features.py      # Data processing features
```

## Core Components

### 1. Configuration System (`config.py`)

The configuration system uses dataclasses for type safety and validation:

```python
@dataclass
class Config:
    api_key: str
    base_url: str = "https://api.openweathermap.org/data/2.5/weather"
    units: str = "imperial"
    database_path: str = "data/weather.db"
    request_timeout: int = 10
    max_retries: int = 3
    log_level: str = "INFO"
    
    @classmethod
    def from_environment(cls):
        """Load configuration from environment variables"""
        # Implementation details...
```

**Key Features:**
- Environment variable loading with fallbacks
- Validation of configuration values
- Type safety with dataclasses
- Default values for all settings

### 2. API Client (`core/api.py`)

The API client handles all external API communications:

```python
class WeatherAPI:
    def __init__(self, config: Config):
        self.config = config
        self.session = requests.Session()
    
    @rate_limit(min_interval=1.0)
    @retry_on_error(max_retries=3)
    @cache_response(ttl=3600)
    def get_current_weather(self, city: str) -> WeatherData:
        """Get current weather for a city"""
        # Implementation details...
```

**Key Features:**
- Decorator-based rate limiting and caching
- Automatic retry on failures
- Session reuse for performance
- Comprehensive error handling

### 3. Data Validation (`core/data_validator.py`)

Input validation ensures data integrity:

```python
class WeatherDataValidator:
    @staticmethod
    def validate_temperature(temp: float) -> bool:
        """Validate temperature is within reasonable range"""
        return -100 <= temp <= 150
    
    @staticmethod
    def validate_humidity(humidity: int) -> bool:
        """Validate humidity percentage"""
        return 0 <= humidity <= 100
```

**Key Features:**
- Comprehensive input validation
- Data cleaning and normalization
- Error reporting with context
- Extensible validation rules

### 4. Database Handler (`core/data_handler.py`)

SQLite database operations with connection pooling:

```python
class DatabaseHandler:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_database()
    
    def save_weather_data(self, data: WeatherData) -> bool:
        """Save weather data to database"""
        # Implementation details...
    
    def get_saved_locations(self) -> List[str]:
        """Retrieve saved locations"""
        # Implementation details...
```

**Key Features:**
- Connection pooling for performance
- Automatic database initialization
- Transaction support
- Data migration capabilities

## Development Setup

### Prerequisites

1. **Python 3.8+**: Required for type hints and dataclasses
2. **Git**: Version control
3. **Virtual Environment**: Isolated Python environment
4. **API Key**: OpenWeatherMap API key

### Installation Steps

```bash
# 1. Clone the repository
git clone <repository-url>
cd weather-dashboard

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment
cp .env.example .env
# Edit .env with your API key

# 5. Run the application
python main.py
```

### Development Environment

#### IDE Configuration
- **VS Code**: Install Python extension and configure linting
- **PyCharm**: Configure project interpreter and run configurations
- **Vim/Emacs**: Install Python language server

#### Recommended Extensions
- **Python**: Microsoft Python extension
- **Pylint**: Code linting and style checking
- **Black**: Code formatting
- **isort**: Import sorting

### Code Quality Tools

```bash
# Install development dependencies
pip install black isort pylint pytest

# Format code
black .
isort .

# Lint code
pylint core/ gui/ services/

# Run tests
pytest test/
```

## Coding Standards

### Python Style Guide

Follow **PEP 8** with these project-specific additions:

#### Naming Conventions
```python
# Classes: PascalCase
class WeatherData:
    pass

# Functions and variables: snake_case
def get_weather_data():
    pass

# Constants: UPPER_SNAKE_CASE
MAX_RETRIES = 3
DEFAULT_TIMEOUT = 10

# Private methods: _leading_underscore
def _internal_helper():
    pass
```

#### Documentation Standards

**Module Docstrings:**
```python
"""Weather Dashboard API Client.

This module provides a comprehensive API client for weather data retrieval.
It handles rate limiting, caching, and error retry logic automatically.

Classes:
    WeatherAPI: Main API client for weather data
    WeatherData: Data structure for weather information
"""
```

**Function Docstrings:**
```python
def get_current_weather(self, city: str) -> WeatherData:
    """Get current weather for a specified city.
    
    Args:
        city: City name or location identifier
        
    Returns:
        WeatherData: Current weather information
        
    Raises:
        APIError: If API request fails
        ValidationError: If city name is invalid
        
    Example:
        >>> api = WeatherAPI(config)
        >>> weather = api.get_current_weather("New York")
        >>> print(weather.temperature)
        72.5
    """
```

#### Type Hints

Use type hints consistently:

```python
from typing import List, Optional, Dict, Any
from dataclasses import dataclass

@dataclass
class WeatherData:
    city: str
    temperature: Optional[float]
    humidity: Optional[int]
    
def process_weather_data(data: List[WeatherData]) -> Dict[str, float]:
    """Process weather data and return statistics."""
    pass
```

### Error Handling

#### Exception Hierarchy
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
```

#### Error Handling Patterns

```python
def safe_api_call(self, func, *args, **kwargs):
    """Execute API call with comprehensive error handling."""
    try:
        return func(*args, **kwargs)
    except requests.RequestException as e:
        self.logger.error(f"Network error: {e}")
        raise APIError(f"Network request failed: {e}")
    except ValueError as e:
        self.logger.error(f"Validation error: {e}")
        raise ValidationError(f"Invalid data: {e}")
    except Exception as e:
        self.logger.error(f"Unexpected error: {e}")
        raise WeatherDashboardError(f"Unexpected error: {e}")
```

## Adding New Features

### Feature Development Workflow

1. **Plan the Feature**
   - Define requirements and acceptance criteria
   - Identify affected components
   - Plan testing strategy

2. **Create Feature Branch**
   ```bash
   git checkout -b feature/new-weather-chart
   ```

3. **Implement the Feature**
   - Follow coding standards
   - Add comprehensive tests
   - Update documentation

4. **Test Thoroughly**
   ```bash
   pytest test/test_new_feature.py
   python main.py  # Manual testing
   ```

5. **Submit Pull Request**
   - Include tests and documentation
   - Request code review

### Example: Adding a New Weather Chart

#### 1. Create the Component
```python
# gui/components/weather_chart.py
import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class WeatherChartComponent(ttk.Frame):
    """Weather chart component for data visualization."""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.setup_ui()
    
    def setup_ui(self):
        """Initialize the user interface."""
        # Create matplotlib figure
        self.figure, self.ax = plt.subplots(figsize=(8, 6))
        self.canvas = FigureCanvasTkAgg(self.figure, self)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def update_chart(self, data: List[WeatherData]):
        """Update chart with new weather data."""
        self.ax.clear()
        # Chart implementation...
        self.canvas.draw()
```

#### 2. Add to Main Window
```python
# gui/main_window.py
from .components.weather_chart import WeatherChartComponent

class MainWindow:
    def setup_tabs(self):
        # Add new tab
        self.chart_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.chart_tab, text="Weather Charts")
        
        # Add component
        self.weather_chart = WeatherChartComponent(self.chart_tab)
        self.weather_chart.pack(fill=tk.BOTH, expand=True)
```

#### 3. Add Tests
```python
# test/test_weather_chart.py
import pytest
from gui.components.weather_chart import WeatherChartComponent

class TestWeatherChartComponent:
    def test_chart_creation(self):
        """Test chart component initializes correctly."""
        root = tk.Tk()
        chart = WeatherChartComponent(root)
        assert chart is not None
        root.destroy()
    
    def test_chart_update(self):
        """Test chart updates with new data."""
        # Test implementation...
```

### Feature Categories

#### GUI Components
- **New Tabs**: Add new information displays
- **Widgets**: Create reusable UI components
- **Charts**: Data visualization components
- **Forms**: Input and configuration forms

#### API Integrations
- **New APIs**: Integrate additional weather services
- **Data Sources**: Add new data providers
- **Export Formats**: Support new data export formats

#### Data Processing
- **Analytics**: Weather pattern analysis
- **Forecasting**: Advanced prediction algorithms
- **Data Mining**: Historical data analysis

#### Theme System
- **New Themes**: Create additional visual themes
- **Customization**: User-configurable appearance
- **Animations**: Smooth transitions and effects

## Testing

### Test Structure

```
test/
├── __init__.py
├── test_api_data_samples.py      # API data validation
├── test_comprehensive_validation.py # Comprehensive tests
├── test_pop_validation.py        # Population validation
├── fixtures/                     # Test data
│   ├── sample_weather_data.json
│   └── mock_api_responses.json
└── integration/                  # Integration tests
    ├── test_full_workflow.py
    └── test_gui_integration.py
```

### Test Categories

#### Unit Tests
```python
def test_weather_data_validation():
    """Test weather data validation logic."""
    validator = WeatherDataValidator()
    
    # Valid data
    assert validator.validate_temperature(72.5) == True
    assert validator.validate_humidity(65) == True
    
    # Invalid data
    assert validator.validate_temperature(-200) == False
    assert validator.validate_humidity(150) == False
```

#### Integration Tests
```python
def test_weather_api_integration():
    """Test complete weather API workflow."""
    config = Config.from_environment()
    api = WeatherAPI(config)
    
    # Test API call
    weather = api.get_current_weather("New York")
    assert weather.city == "New York"
    assert weather.temperature is not None
```

#### GUI Tests
```python
def test_weather_display_component():
    """Test weather display component."""
    root = tk.Tk()
    component = WeatherDisplayComponent(root)
    
    # Test component initialization
    assert component is not None
    
    # Test data update
    test_data = WeatherData(city="Test", temperature=75.0)
    component.update_display(test_data)
    
    root.destroy()
```

### Test Best Practices

1. **Isolation**: Each test should be independent
2. **Mocking**: Use mocks for external dependencies
3. **Coverage**: Aim for 80%+ code coverage
4. **Performance**: Tests should run quickly
5. **Documentation**: Clear test names and docstrings

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest test/test_api_data_samples.py

# Run with coverage
pytest --cov=core --cov=gui

# Run with verbose output
pytest -v

# Run only unit tests
pytest test/ -k "not integration"
```

## Performance Optimization

### Caching Strategy

#### API Response Caching
```python
@cache_response(ttl=3600)  # 1 hour cache
def get_current_weather(self, city: str) -> WeatherData:
    """Get current weather with caching."""
    # Implementation...
```

#### Database Query Caching
```python
class DatabaseHandler:
    def __init__(self):
        self._cache = {}
    
    @lru_cache(maxsize=100)
    def get_saved_locations(self) -> List[str]:
        """Get saved locations with caching."""
        # Implementation...
```

### Memory Management

#### Resource Cleanup
```python
class WeatherAPI:
    def __init__(self):
        self.session = requests.Session()
    
    def __del__(self):
        """Clean up resources."""
        if hasattr(self, 'session'):
            self.session.close()
```

#### Connection Pooling
```python
import sqlite3
from contextlib import contextmanager

class DatabaseHandler:
    def __init__(self, db_path: str):
        self.db_path = db_path
    
    @contextmanager
    def get_connection(self):
        """Get database connection with automatic cleanup."""
        conn = sqlite3.connect(self.db_path)
        try:
            yield conn
        finally:
            conn.close()
```

### Performance Monitoring

#### Metrics Collection
```python
import time
from functools import wraps

def performance_monitor(func):
    """Decorator to monitor function performance."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        duration = time.time() - start_time
        
        if duration > 1.0:  # Log slow operations
            logging.warning(f"Slow operation: {func.__name__} took {duration:.2f}s")
        
        return result
    return wrapper
```

#### Performance Profiling
```python
import cProfile
import pstats

def profile_function(func, *args, **kwargs):
    """Profile a function's performance."""
    profiler = cProfile.Profile()
    profiler.enable()
    
    result = func(*args, **kwargs)
    
    profiler.disable()
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')
    stats.print_stats(10)  # Top 10 functions
    
    return result
```

## API Integration

### Adding New APIs

#### API Client Template
```python
class NewWeatherAPI:
    """Template for new weather API integration."""
    
    def __init__(self, config: Config):
        self.config = config
        self.base_url = "https://api.newwservice.com"
        self.session = requests.Session()
    
    @rate_limit(min_interval=1.0)
    @retry_on_error(max_retries=3)
    def get_weather_data(self, location: str) -> WeatherData:
        """Get weather data from new API."""
        url = f"{self.base_url}/weather"
        params = {
            'location': location,
            'units': self.config.units
        }
        
        response = self.session.get(url, params=params)
        response.raise_for_status()
        
        return self._parse_response(response.json())
    
    def _parse_response(self, data: dict) -> WeatherData:
        """Parse API response into WeatherData format."""
        return WeatherData(
            city=data['location'],
            temperature=data['temp'],
            humidity=data['humidity'],
            # ... other fields
        )
```

#### API Configuration
```python
# config.py
@dataclass
class Config:
    # Existing fields...
    new_api_key: str = ""
    new_api_url: str = "https://api.newwservice.com"
    new_api_timeout: int = 10
```

### API Best Practices

1. **Rate Limiting**: Respect API rate limits
2. **Error Handling**: Comprehensive error handling
3. **Caching**: Cache responses to reduce API calls
4. **Retry Logic**: Automatic retry on failures
5. **Logging**: Log API interactions for debugging

## Deployment

### Production Setup

#### Environment Configuration
```bash
# Production environment variables
API_KEY=your_production_api_key
LOG_LEVEL=WARNING
DATABASE_PATH=/var/weather/data/weather.db
REQUEST_TIMEOUT=15
MAX_RETRIES=5
```

#### System Requirements
- **Python 3.8+**: Runtime environment
- **SQLite**: Database (included with Python)
- **Internet**: API connectivity
- **Storage**: 100MB+ for data and logs

#### Deployment Options

**Desktop Application:**
```bash
# Create executable
pip install pyinstaller
pyinstaller --onefile main.py
```

**Docker Container:**
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["python", "main.py"]
```

**System Service:**
```ini
# /etc/systemd/system/weather-dashboard.service
[Unit]
Description=Weather Dashboard
After=network.target

[Service]
Type=simple
User=weather
WorkingDirectory=/opt/weather-dashboard
ExecStart=/usr/bin/python3 main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

### Monitoring and Logging

#### Application Logging
```python
import logging
from logging.handlers import RotatingFileHandler

def setup_logging():
    """Setup comprehensive logging."""
    logger = logging.getLogger('weather_dashboard')
    logger.setLevel(logging.INFO)
    
    # File handler with rotation
    file_handler = RotatingFileHandler(
        'data/weather_dashboard.log',
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setFormatter(
        logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    )
    logger.addHandler(file_handler)
    
    return logger
```

#### Health Checks
```python
def health_check():
    """Perform application health check."""
    try:
        # Check database connectivity
        db_handler = DatabaseHandler(config.database_path)
        db_handler.test_connection()
        
        # Check API connectivity
        api = WeatherAPI(config)
        api.test_connection()
        
        return True
    except Exception as e:
        logging.error(f"Health check failed: {e}")
        return False
```

### Security Considerations

1. **API Key Management**: Secure storage of API keys
2. **Input Validation**: Validate all user inputs
3. **Error Handling**: Don't expose sensitive information
4. **File Permissions**: Secure file and directory permissions
5. **Network Security**: Use HTTPS for API calls

---

*This developer guide provides comprehensive information for extending and maintaining the Weather Dashboard. For specific implementation details, refer to the API documentation and source code.*