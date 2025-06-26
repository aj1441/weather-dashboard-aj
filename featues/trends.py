def analyze_trends(weather_data_list):
    """Analyze weather trends for a city."""
    # Example: return average change or trend direction
    if len(weather_data_list) < 2:
        return "Insufficient data"
    delta = weather_data_list[-1]['temperature'] - weather_data_list[0]['temperature']
    return "Warming trend" if delta > 0 else "Cooling trend" if delta < 0 else "Stable"
