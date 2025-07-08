"""Utility functions for updating the weather details row using ttkbootstrap."""

def update_weather_details_row(humidity_label, pressure_label, wind_label, parsed):
    """
    Update the details row labels for humidity, pressure, and wind.
    Args:
        humidity_label: Label widget for humidity
        pressure_label: Label widget for pressure
        wind_label: Label widget for wind
        parsed: dict from parse_weather_data (should include 'wind_unit_label')
    """
    humidity_display = f"{parsed['humidity']}%" if parsed['humidity'] != "N/A" and parsed['humidity'] is not None else "N/A%"
    humidity_label.config(text=f"💧 Humidity: {humidity_display}")

    pressure_display = f"{parsed['pressure']} hPa" if parsed['pressure'] != "N/A" and parsed['pressure'] is not None else "N/A hPa"
    pressure_label.config(text=f"🌡️ Pressure: {pressure_display}")

    if parsed['wind_speed'] != "N/A" and parsed['wind_speed'] is not None:
        wind_display = f"{parsed['wind_speed']} {parsed.get('wind_unit_label', 'mph')}"
    else:
        wind_display = f"N/A {parsed.get('wind_unit_label', 'mph')}"
    wind_label.config(text=f"🌬️ Wind: {wind_display}")
