# Weather Dashboard User Guide

## Table of Contents
1. [Getting Started](#getting-started)
2. [Main Interface](#main-interface)
3. [Weather Features](#weather-features)
4. [Theme System](#theme-system)
5. [Saved Locations](#saved-locations)
6. [Historical Data](#historical-data)
7. [Troubleshooting](#troubleshooting)
8. [Tips and Tricks](#tips-and-tricks)

## Getting Started

### First Launch
1. **Installation**: Follow the setup guide in `SETUP_GUIDE.md`
2. **API Key**: Ensure you have a valid OpenWeatherMap API key in your `.env` file
3. **Launch**: Run `python main.py` from the project directory

### Initial Setup
- The app will automatically detect your location on first launch
- Your theme preference will be saved for future sessions
- The database will be created automatically in the `data/` folder

## Main Interface

### Navigation Tabs
The Weather Dashboard features a tabbed interface for organized access to different features:

#### Current Weather Tab
- **Location Search**: Enter any city name to get current weather
- **Current Conditions**: Temperature, humidity, wind speed, and weather description
- **Weather Icon**: Visual representation of current conditions
- **Last Updated**: Timestamp showing when data was last refreshed

#### Forecast Tab
- **7-Day Forecast**: Extended weather predictions
- **Daily Highs/Lows**: Temperature ranges for each day
- **Weather Patterns**: Visual indicators of upcoming conditions
- **Precipitation Chance**: Rain/snow probability for each day

#### Historical Data Tab
- **Date Range Selection**: Choose start and end dates for historical data
- **Weather Metrics**: Temperature, precipitation, wind, and cloud cover history
- **Data Visualization**: Charts and graphs of historical patterns
- **Export Options**: Save historical data for analysis

#### Settings Tab
- **Theme Controls**: Auto day/night mode and manual theme selection
- **Units**: Switch between Fahrenheit and Celsius
- **Saved Locations**: Manage your favorite cities
- **API Settings**: Configure API endpoints and timeouts

## Weather Features

### Current Weather Information
The dashboard displays comprehensive current weather data:

- **Temperature**: Current temperature in your preferred units
- **Feels Like**: Apparent temperature considering wind and humidity
- **Humidity**: Relative humidity percentage
- **Wind Speed**: Current wind speed and direction
- **Pressure**: Atmospheric pressure in millibars
- **Visibility**: Visibility range in miles/kilometers
- **UV Index**: Current UV radiation level
- **Sunrise/Sunset**: Daily sun position times

### Weather Descriptions
The app provides detailed weather descriptions:
- **Clear**: No cloud cover
- **Cloudy**: Overcast conditions
- **Rain**: Precipitation of various intensities
- **Snow**: Snowfall conditions
- **Storm**: Thunderstorm or severe weather
- **Fog**: Reduced visibility conditions

### Forecast Details
7-day forecasts include:
- **Daily High/Low**: Temperature extremes for each day
- **Weather Type**: Expected conditions (sunny, cloudy, rain, etc.)
- **Precipitation**: Chance of rain or snow
- **Wind**: Expected wind speed and direction
- **Humidity**: Forecasted humidity levels

## Theme System

### Auto Day/Night Mode
The intelligent theme system automatically switches between light and dark themes:

#### How It Works
1. **Location Detection**: Uses your current location or searched city
2. **Sunrise/Sunset Calculation**: Determines actual day/night times for your location
3. **Automatic Switching**: Changes theme based on current time vs. sunrise/sunset
4. **Periodic Updates**: Refreshes theme every 30 minutes

#### Theme Controls
- **🌅 Auto Day/Night**: Toggle automatic theme switching
- **☀ Light Theme**: Manual light theme selection
- **🌙 Dark Theme**: Manual dark theme selection
- **Settings Persistence**: Your preferences are saved between sessions

#### Theme Features
- **Custom Themes**: Beautiful `aj_lightly` (light) and `aj_darkly` (dark) themes
- **Smooth Transitions**: Seamless theme switching
- **Location-Aware**: Theme updates when you search new locations
- **Manual Override**: Disable auto mode for manual control

### Manual Theme Control
When auto mode is disabled:
1. Click the theme toggle button in the settings tab
2. Choose between light and dark themes
3. Changes apply immediately across the entire interface
4. Your selection is remembered for future sessions

## Saved Locations

### Managing Favorite Cities
The dashboard allows you to save and quickly access your favorite locations:

#### Adding Locations
1. Search for a city in the location field
2. Click the "Save Location" button (star icon)
3. The city is added to your saved locations list
4. Access saved locations from the dropdown menu

#### Saved Locations Features
- **Quick Access**: Click any saved city to load its weather
- **Location Management**: Add, remove, and reorder saved cities
- **Persistent Storage**: Saved locations are stored in the database
- **Cross-Session**: Locations persist between app restarts

#### Location Management
- **Add New**: Save current search location
- **Remove**: Delete unwanted saved locations
- **Reorder**: Drag and drop to change display order
- **Edit**: Modify saved location names

## Historical Data

### Accessing Historical Weather
The historical data feature provides access to weather records from 2010 to present:

#### Date Selection
1. Navigate to the Historical Data tab
2. Select start and end dates using the date pickers
3. Choose your desired location
4. Click "Load Historical Data"

#### Available Data
- **Temperature**: Daily high, low, and average temperatures
- **Precipitation**: Daily rainfall and snowfall amounts
- **Wind**: Wind speed and direction data
- **Cloud Cover**: Percentage of sky covered by clouds
- **Humidity**: Daily humidity levels
- **Pressure**: Atmospheric pressure readings

#### Data Visualization
- **Line Charts**: Temperature trends over time
- **Bar Charts**: Precipitation amounts
- **Heat Maps**: Weather pattern visualization
- **Export Options**: Save data as CSV or JSON

### Historical Data Features
- **No API Key Required**: Uses free Open-Meteo API
- **Global Coverage**: Data available for most world locations
- **High Resolution**: Daily aggregated weather metrics
- **Fast Loading**: Optimized data retrieval with caching

## Troubleshooting

### Common Issues

#### "API Key Required" Error
**Problem**: Application shows API key error on startup
**Solution**:
1. Check that your `.env` file exists in the project root
2. Ensure your API key is correctly set: `API_KEY=your_key_here`
3. Get a free API key from [OpenWeatherMap](https://openweathermap.org/api)
4. Restart the application

#### "Location Not Found" Error
**Problem**: City search returns no results
**Solution**:
1. Check spelling and try alternative city names
2. Use official city names (e.g., "New York" instead of "NYC")
3. Try adding country codes for ambiguous names
4. Ensure you have an internet connection

#### Theme Not Updating
**Problem**: Auto day/night theme doesn't change
**Solution**:
1. Check that auto mode is enabled in settings
2. Verify your location is correctly detected
3. Wait for the 30-minute refresh cycle
4. Try manually toggling themes to test functionality

#### Slow Performance
**Problem**: Application feels sluggish or unresponsive
**Solution**:
1. Check your internet connection speed
2. Close other applications to free up system resources
3. Restart the application
4. Check the log file for error messages

### Error Messages

#### Configuration Errors
- **"Weather API key is required"**: Set your API key in `.env` file
- **"Invalid API key format"**: Check your API key is correct
- **"Database path not writable"**: Check file permissions

#### Network Errors
- **"Connection timeout"**: Check internet connection
- **"API rate limit exceeded"**: Wait a few minutes before retrying
- **"Service unavailable"**: Weather API may be temporarily down

#### Data Errors
- **"Invalid weather data"**: API response format issue
- **"Location not found"**: Try different city name
- **"Historical data unavailable"**: Data may not exist for selected dates

## Tips and Tricks

### Optimizing Your Experience

#### Performance Tips
1. **Use Saved Locations**: Save frequently accessed cities for faster loading
2. **Enable Caching**: The app caches weather data to reduce API calls
3. **Close Unused Tabs**: Close historical data tab when not needed
4. **Regular Restarts**: Restart the app weekly for optimal performance

#### Weather Data Tips
1. **Check Multiple Sources**: Compare current weather with forecast
2. **Use Historical Data**: Analyze weather patterns for planning
3. **Save Important Locations**: Keep frequently checked cities saved
4. **Monitor Trends**: Use historical data to spot weather patterns

#### Theme Tips
1. **Auto Mode Benefits**: Let the app handle theme switching automatically
2. **Manual Override**: Use manual mode for specific preferences
3. **Location-Based Themes**: Theme changes when you search new locations
4. **Persistent Settings**: Your theme choice is remembered

### Keyboard Shortcuts
- **Ctrl+Q**: Quit application
- **Ctrl+S**: Save current location
- **Ctrl+R**: Refresh weather data
- **Ctrl+T**: Switch between tabs
- **F11**: Toggle fullscreen mode

### Data Management
- **Backup Settings**: Your preferences are stored in `data/weather.db`
- **Log Files**: Check `data/weather_dashboard.log` for troubleshooting
- **Cache Management**: Weather data is cached for 1 hour by default
- **Database Location**: All data is stored in the `data/` directory

### Advanced Features
- **Multiple Units**: Switch between Fahrenheit and Celsius
- **Detailed Logs**: Enable DEBUG logging for troubleshooting
- **API Configuration**: Customize API endpoints and timeouts
- **Performance Monitoring**: Built-in performance tracking

## Support

### Getting Help
1. **Check Logs**: Review `data/weather_dashboard.log` for error details
2. **Documentation**: Refer to `README.md` for technical details
3. **Configuration**: Review `config.py` for available settings
4. **API Status**: Check OpenWeatherMap API status if issues persist

### Reporting Issues
When reporting problems, include:
- **Error Message**: Exact error text
- **Steps to Reproduce**: How to trigger the issue
- **System Information**: OS version and Python version
- **Log File**: Relevant entries from the log file
- **Configuration**: Your current settings

### Feature Requests
The Weather Dashboard is designed for extensibility. New features can be added by:
1. **GUI Components**: Adding new tabs or widgets
2. **API Integration**: Connecting to additional weather services
3. **Data Processing**: Implementing new data analysis features
4. **Theme Customization**: Creating new visual themes

---

*This user guide covers all major features of the Weather Dashboard. For technical details, refer to the API documentation and developer guides.*