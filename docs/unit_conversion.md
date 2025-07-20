# Unit Toggle (Fahrenheit/Celsius) Implementation

## Overview

This document explains how the Weather Dashboard application allows users to toggle between Fahrenheit (imperial) and Celsius (metric) units for both current weather and forecast displays using a clean, service-based architecture.

---

## Architecture Overview

The conversion system follows Python best practices with:
- **Pure Functions**: No side effects, immutable data
- **Separation of Concerns**: Dedicated service classes
- **Single Responsibility**: Each component has one clear purpose

---

## Components Involved

### Core Services

- **WeatherConversionService** (`utils/weather_conversion_service.py`):  
  Pure functions for converting weather data between units.
  - `convert_current_weather_data()`: Converts current weather without mutation
  - `convert_forecast_data()`: Converts forecast data without mutation
  - `_convert_temperature()`: Single temperature conversion
  - `get_unit_label()`: Returns °F or °C display label

- **ForecastCache** (`utils/weather_conversion_service.py`):  
  Immutable cache that stores original data and provides converted copies.
  - `store()`: Cache original forecast data with its unit
  - `get_converted()`: Return converted copy without mutating original
  - `has_data()`: Check if cache contains data

### UI Components

- **WeatherInputComponent**:  
  Contains the F/C toggle and "Get Weather" button.  
  - `unit_var` (StringVar): Tracks the current unit
  - `toggle_units()`: Handles toggle changes and triggers callbacks
  - `on_get_weather()`: Passes the selected unit to the weather fetch callback

- **TabbedWeatherDashboard**:  
  Coordinates unit changes and updates all displays.
  - `handle_unit_change(new_unit)`: Uses conversion service for data transformation
  - `forecast_cache` (ForecastCache): Immutable forecast storage

- **WeatherDisplayComponent** & **ForecastDisplayComponent**:  
  Display weather data with proper unit labels.

---

## Data Flow

1. **User toggles F/C switch**  
   → `toggle_units()` in `WeatherInputComponent`  
   → Calls `handle_unit_change(new_unit)` in `TabbedWeatherDashboard`

2. **Unit Change Handling**  
   - Uses `WeatherConversionService.convert_current_weather_data()` for current weather
   - Uses `forecast_cache.get_converted(target_unit)` for forecast data
   - Both operations return new converted copies without mutating originals
   - Updates display components with converted data

3. **User clicks "Get Weather"**  
   - Fetches weather data in selected unit
   - Stores forecast in cache with `forecast_cache.store(data, unit)`

---

## Key Implementation Benefits

- **Reliable Conversions**: Original data never mutated, conversions work every time
- **Predictable Behavior**: Pure functions with clear inputs/outputs
- **Testable Code**: Each service can be tested independently
- **No Side Effects**: Conversions don't affect cached data
- **Memory Efficient**: Deep copies only created when needed

---

## Example Code Usage

```python
from utils.weather_conversion_service import WeatherConversionService, ForecastCache

# Initialize cache
forecast_cache = ForecastCache()

# Store original forecast data
forecast_cache.store(forecast_data, 'imperial')

# Convert current weather (pure function)
converted_weather = WeatherConversionService.convert_current_weather_data(
    current_data, 'imperial', 'metric'
)

# Get converted forecast from cache (pure function)  
converted_forecast = forecast_cache.get_converted('metric')

# Original data remains unchanged for reliable future conversions
```

---

## Python Best Practices Implemented

1. **Immutable Data**: Original cached data never modified
2. **Pure Functions**: No side effects, predictable outputs
3. **Single Responsibility**: Each class has one clear purpose
4. **Composition over Inheritance**: Services composed together
5. **Type Hints**: Clear interfaces with proper typing
6. **Deep Copying**: Explicit data copying to prevent mutations

---

## Troubleshooting

- **Conversions not working**: Check that `WeatherConversionService` is being used instead of direct mutations
- **Cache issues**: Verify `forecast_cache.store()` is called when new data is fetched
- **Unit labels not updating**: Ensure `get_unit_label()` is used consistently
