# Unit Toggle (Fahrenheit/Celsius) Implementation

## Overview

This document explains how the Weather Dashboard application allows users to toggle between Fahrenheit (imperial) and Celsius (metric) units for both current weather and forecast displays.

---

## Components Involved

- **WeatherInputComponent**:  
  Contains the F/C toggle and "Get Weather" button.  
  - `unit_var` (StringVar): Tracks the current unit.
  - `toggle_units()`: Handles toggle changes and triggers callbacks.
  - `on_get_weather()`: Passes the selected unit to the weather fetch callback.

- **TabbedWeatherDashboard**:  
  Coordinates unit changes and updates all displays.
  - `handle_unit_change(new_unit)`: Converts displayed data and updates components.
  - `last_forecast_data`: Caches the latest forecast for robust toggling.

- **WeatherDisplayComponent**:  
  Displays current weather, temperature, and unit label.
  - `update_display(weather_data)`: Updates temperature and unit label.

- **ForecastDisplayComponent**:  
  Displays the 7-day forecast, updating all temperatures and unit labels.
  - `update_forecast_display(forecast_data)`: Updates forecast cards with correct units.

---

## Data Flow

1. **User toggles F/C switch**  
   → `toggle_units()` in `WeatherInputComponent`  
   → Calls `handle_unit_change(new_unit)` in `TabbedWeatherDashboard`

2. **Unit Change Handling**  
   - Converts current weather and cached forecast data to the new unit.
   - Updates both `WeatherDisplayComponent` and `ForecastDisplayComponent` with new values and unit labels.

3. **User clicks "Get Weather"**  
   - `on_get_weather()` passes the current unit to the fetch callback.
   - Weather data is fetched and displayed in the selected unit.

---

## Key Implementation Details

- **Unit Conversion**:  
  - Conversion functions (`convert_to_celsius`, `convert_to_fahrenheit`) are used for both current and forecast data.
  - The `unit` field is set in all data dicts for display components to show the correct °F/°C label.

- **Forecast Caching**:  
  - The latest forecast is cached in `TabbedWeatherDashboard` to ensure the forecast display persists and updates correctly when toggling units.

- **Display Update**:  
  - Both display components read the `unit` field and update their labels accordingly.

---

## Example Code Snippet

```python
# In WeatherInputComponent
def toggle_units(self):
    if hasattr(self, 'on_unit_change'):
        self.on_unit_change(self.unit_var.get())

# In TabbedWeatherDashboard
def handle_unit_change(self, new_unit):
    ...
    converted_data = self._convert_temperature_data(current_data, old_unit, new_unit)
    converted_data['unit'] = '°C' if new_unit == 'metric' else '°F'
    self.weather_display.update_display(converted_data)
    # Use cached forecast if needed
    forecast = converted_data.get('forecast', []) or self.last_forecast_data
    for day in forecast:
        day['unit'] = converted_data['unit']
    self.forecast_display.update_forecast_display(forecast)
```

---

## Troubleshooting

- If the forecast disappears on toggle, ensure `last_forecast_data` is always updated and used as a fallback.
- If the F/C label does not update, check that the `unit` field is set and used in all display updates.
