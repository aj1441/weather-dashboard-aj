"""
Utility for handling unit label logic for temperature, wind, etc.
"""

def get_unit_label(temp_unit):
    """
    Return the unit label for temperature.
    Args:
        temp_unit: str, 'imperial', 'metric', or 'kelvin'
    Returns:
        str: unit label (e.g., '°F', '°C', 'K')
    """
    if temp_unit == 'imperial':
        return '°F'
    elif temp_unit == 'metric':
        return '°C'
    elif temp_unit == 'kelvin':
        return 'K'
    else:
        return '°F'  # Default

def get_wind_unit_label(temp_unit):
    """
    Return the wind speed unit label based on temperature unit system.
    Args:
        temp_unit: str, 'imperial', 'metric', or 'kelvin'
    Returns:
        str: wind unit label (e.g., 'mph', 'm/s')
    """
    if temp_unit == 'imperial':
        return 'mph'
    else:
        return 'm/s'
