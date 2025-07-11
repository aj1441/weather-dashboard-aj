# Weather Dashboard

A modern, extensible weather dashboard built with Python and ttkbootstrap. Features real-time and historical weather data, intelligent theme switching, and a modular architecture designed for easy expansion.

## Features

- **Real-time Weather**: Current conditions and 7-day forecasts via OpenWeatherMap API
- **Historical Weather**: Historical data from 2010-present via Open-Meteo API (no key required)
- **🌅 Auto Day/Night Mode**: Intelligent theme switching using sunrise-sunset.org API
- **Custom Themes**: Beautiful light (`aj_lightly`) and dark (`aj_darkly`) themes
- **Location-Aware**: Automatic location detection with manual override options
- **Data Validation**: Robust data validation and cleaning with decorator-based validation
- **Rate Limiting**: API rate limiting and retry mechanisms using Python decorators
- **Error Handling**: Comprehensive error handling with decorator-based retries and fallbacks
- **Persistent Storage**: SQLite database with JSON backup for user settings and saved cities
- **Theme Support**: Light and dark themes with user preferences and auto/manual modes
- **Saved Locations**: Save and manage favorite cities with quick access
- **API Caching**: Built-in API response caching with session reuse
- **Modular Architecture**: Extensible component-based design with decorator patterns

## Auto Day/Night Theme Feature

The weather dashboard automatically switches between light and dark themes based on:

- **Your Location**: Uses IP geolocation to determine your approximate location
- **Sunrise/Sunset Times**: Calculates actual sunrise and sunset times for your location
- **Location Updates**: When you search for weather in a new city, the theme updates based on day/night at that location
- **Automatic Refresh**: Theme refreshes every 30 minutes to stay current

### Theme Controls

- **🌅 Auto Day/Night**: Toggle automatic theme switching on/off
- **☀ Light / 🌙 Dark**: Manual theme control (only available when auto mode is disabled)
- **Persistent Settings**: Your theme preferences are saved between sessions

### How It Works

1. **Startup**: App detects your location and applies appropriate theme
2. **Weather Search**: Theme updates based on day/night at the searched location
3. **Periodic Updates**: Theme refreshes automatically every 30 minutes
4. **Manual Override**: You can disable auto mode and manually control themes

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configuration
Copy the example environment file and add your API key:
```bash
cp .env.example .env
```

Edit `.env` and add your OpenWeatherMap API key:
```
API_KEY=your_32_character_api_key_here
```

Get a free API key from [OpenWeatherMap](https://openweathermap.org/api).

### 3. Run the Application
```bash
python main.py
```

### 4. Test Auto Theme Feature (Optional)
```bash
# Demonstrate auto day/night theme functionality
python demo_auto_theme.py

# Run comprehensive auto theme tests
python test_day_night_theme.py
```

## Configuration Options

The application supports the following environment variables in your `.env` file:

| Variable | Description | Default |
|----------|-------------|---------|
| `API_KEY` | OpenWeatherMap API key (required) | - |
| `BASE_URL` | Weather API base URL | `https://api.openweathermap.org/data/2.5/weather` |
| `UNITS` | Temperature units (metric/imperial) | `imperial` |
| `DATABASE_PATH` | SQLite database location | `data/weather.db` |
| `REQUEST_TIMEOUT` | API request timeout in seconds | `10` |
| `MAX_RETRIES` | Maximum API retry attempts | `3` |
| `CACHE_DURATION` | Weather data cache duration in hours | `1` |
| `LOG_LEVEL` | Logging level (DEBUG/INFO/WARNING/ERROR) | `INFO` |

## Architecture

The application follows a modular architecture with clear separation of concerns:

- **`config.py`**: Dataclass-based configuration management
- **`core/api.py`**: Enhanced API client with caching and retries
- **`core/open_meteo_historical.py`**: Historical weather data client
- **`core/data_validator.py`**: Data validation and cleaning
- **`core/data_handler.py`**: Database and storage management
- **`core/auto_theme.py`**: Intelligent theme management system
- **`core/theme_manager.py`**: Theme registration and switching
- **`core/custom_themes.py`**: Custom theme definitions
- **`gui/`**: Modular GUI components with theme support

## Development

### Running Tests
```bash
pytest test/
```

### Code Structure
```
weather-dashboard-aj/
├── config.py                    # Application configuration
├── main.py                     # Application entry point
├── core/                       # Core business logic
│   ├── api.py                 # Weather API client
│   ├── open_meteo_historical.py # Historical data client
│   ├── data_validator.py      # Data validation and cleaning
│   ├── data_handler.py        # Database and storage
│   ├── auto_theme.py          # Auto theme system
│   ├── theme_manager.py       # Theme management
│   ├── custom_themes.py       # Theme definitions
│   └── utils.py              # Utility functions
├── gui/                       # User interface
│   ├── tabbed_main_window.py # Main application window
│   └── components/           # Reusable GUI components
│       ├── theme_component.py
│       ├── weather_display.py
│       └── saved_cities.py
├── data/                      # Application data
│   ├── weather.db           # SQLite database
│   ├── weather_history.json # Historical data
│   └── user_settings.json   # User preferences
└── docs/                     # Documentation
    └── AUTO_THEME_IMPLEMENTATION.md
```

### Adding New Features

The modular architecture makes it easy to add new features:

1. **New API Endpoints**: Extend the `WeatherAPI` class
2. **Additional Validation**: Add rules to `WeatherDataValidator`
3. **New GUI Components**: Create components in `gui/components/`
4. **Data Processing**: Add new decorators or data handlers

## Logging

The application logs to both console and file:
- Console: Real-time feedback during development
- File: `data/weather_dashboard.log` for debugging and monitoring

Set `LOG_LEVEL=DEBUG` in your `.env` file for detailed debugging information.

## Troubleshooting

### Missing API Key
```
Configuration Error: Weather API key is required
```
**Solution**: Add `API_KEY=your_key_here` to your `.env` file.

### Import Errors
```
Import Error: No module named 'ttkbootstrap'
```
**Solution**: Install dependencies with `pip install -r requirements.txt`

### Database Issues
The application automatically creates the SQLite database. If you encounter issues:
1. Check that the `data/` directory is writable
2. Delete `data/weather.db` to recreate the database
3. Check the log file for detailed error messages

## API Integration

The weather dashboard integrates with multiple weather APIs for comprehensive functionality:

### OpenWeatherMap API (Requires API Key)
- Current weather conditions (`/data/2.5/weather`)
- 7-day weather forecast (`/data/2.5/forecast/climate`, `/data/2.5/forecast`)
- Geocoding for location search (`/geo/1.0/direct`)
- Key management and rate limiting

### Open-Meteo Archive API (No Key Required)
- Historical weather data from 2010 to present
- Temperature, precipitation, wind, and cloud cover history
- Daily aggregated weather metrics
- Built-in caching and retry mechanisms

### Sunrise-Sunset API (No Key Required)
- Precise sunrise/sunset times for any location
- Powers the auto day/night theme system
- Automatic time zone handling
- Response caching for performance

### Core Decorators
The application uses Python decorators extensively for:
- **@rate_limit**: Control API request frequency
- **@validate_response**: Ensure API response integrity
- **@retry_on_error**: Automatic retry for transient failures
- **@cache_response**: Cache API responses to reduce calls
- **@handle_api_error**: Standardized error handling
- **@validate_input**: Input parameter validation

Each API client is wrapped with appropriate decorators to ensure robust operation and optimal performance. The decorator pattern allows for easy addition of cross-cutting concerns like logging, monitoring, and error handling.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is for educational purposes as part of a capstone project.