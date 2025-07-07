# Weather Dashboard

A modern, extensible weather dashboard built with Python and ttkbootstrap. Features real-time weather data, persistent storage, theme switching, and a modular architecture designed for easy expansion.

## Features

- **Real-time Weather Data**: Current conditions using OpenWeatherMap API
- **🌅 Auto Day/Night Mode**: Automatic theme switching based on your location and local sunrise/sunset times
- **Location-Aware Theming**: Theme updates based on the location you're viewing weather for
- **Data Validation**: Robust validation and cleaning of weather data with unit conversion
- **Persistent Storage**: SQLite database with JSON backup for user settings and saved cities
- **Theme Support**: Light and dark themes with user preferences, auto mode, and manual override
- **Saved Locations**: Save and manage favorite cities with quick access
- **Rate Limiting**: Built-in API rate limiting and retry mechanisms with session reuse
- **Location Services**: IP-based location detection for automatic theme switching
- **Modular Architecture**: Extensible component-based design for future enhancements

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
| `MIN_REQUEST_INTERVAL` | Rate limiting interval in seconds | `1.0` |
| `LOG_LEVEL` | Logging level (DEBUG/INFO/WARNING/ERROR) | `INFO` |

## Architecture

The application follows a modular architecture with clear separation of concerns:

- **`config.py`**: Dataclass-based configuration with environment variable loading
- **`core/api.py`**: Enhanced API client with rate limiting, retries, and validation
- **`core/data_validator.py`**: Modular data validation and cleaning
- **`core/data_handler.py`**: Database and file storage management
- **`core/decorators.py`**: Reusable decorators for common patterns
- **`gui/`**: Modular GUI components and main window

## Development

### Running Tests
```bash
pytest test/
```

### Code Structure
```
weather-dashboard-aj/
├── config.py              # Application configuration
├── main.py                # Application entry point
├── core/                  # Core business logic
│   ├── api.py            # Weather API client
│   ├── data_validator.py # Data validation and cleaning
│   ├── data_handler.py   # Database and storage
│   └── decorators.py     # Utility decorators
├── gui/                  # User interface
│   ├── tabbed_main_window.py
│   └── components/       # Reusable GUI components
├── data/                 # Application data
└── docs/                 # Documentation
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

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is for educational purposes as part of a capstone project.