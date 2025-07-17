"""Utility functions for weather data extraction and formatting"""

def parse_weather_data(data, unit_label="°F"):
    """
    Parse weather data dict (raw or cleaned) into a display-ready dict.
    Returns:
        dict with keys: city, temp, description, humidity, pressure, wind_speed, icon, country
    """
    # Try cleaned format first
    if 'city' in data and 'temperature' in data:
        return {
            'city': data.get('city', 'Unknown'),
            'temp': data.get('temperature', 'N/A'),
            'description': data.get('weather_description', 'N/A'),
            'humidity': data.get('humidity', 'N/A'),
            'pressure': data.get('pressure', 'N/A'),
            'wind_speed': data.get('wind_speed', 'N/A'),
            'icon': data.get('weather_icon', ''),
            'country': data.get('country', ''),
            'unit_label': unit_label
        }
    # Fallback to raw OpenWeatherMap format
    return {
        'city': data.get('name', 'Unknown'),
        'temp': data.get('main', {}).get('temp', 'N/A'),
        'description': data.get('weather', [{}])[0].get('description', 'N/A'),
        'humidity': data.get('main', {}).get('humidity', 'N/A'),
        'pressure': data.get('main', {}).get('pressure', 'N/A'),
        'wind_speed': data.get('wind', {}).get('speed', 'N/A'),
        'icon': data.get('weather', [{}])[0].get('icon', ''),
        'country': data.get('sys', {}).get('country', ''),
        'unit_label': unit_label
    }
