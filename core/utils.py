from datetime import datetime
import json
import os


# Constants for user settings and theme management
# This file handles loading and saving user preferences, such as theme settings.
# It allows the application to remember user choices across sessions.
USER_SETTINGS_FILE = "data/user_settings.json"

def load_user_theme(default="superhero"):
    """Load saved theme from file, or use default."""
    if os.path.exists(USER_SETTINGS_FILE):
        try:
            with open(USER_SETTINGS_FILE, "r") as f:
                settings = json.load(f)
                return settings.get("theme", default)
        except Exception:
            return default
    return default

def save_user_theme(theme_name):
    """Save selected theme to user settings file."""
    settings = {"theme": theme_name}
    try:
        os.makedirs("data", exist_ok=True)
        with open(USER_SETTINGS_FILE, "w") as f:
            json.dump(settings, f, indent=2)
    except Exception as e:
        print(f"Failed to save theme: {e}")

# Utility functions for the weather dashboard application
def format_timestamp(timestamp):
    """Convert ISO timestamp to readable format."""
    try:
        return datetime.fromisoformat(timestamp).strftime("%b %d, %Y %I:%M %p")
    except:
        return "N/A"
    
# Function to map weather descriptions to emojis
# This function takes a weather description string and returns an appropriate emoji.
# It helps to visually represent the weather conditions in the GUI.
# It can be used in labels or buttons to enhance user experience.
def map_weather_to_emoji(description):
    d = description.lower()
    if "sun" in d or "clear" in d:
        return "☀️"
    elif "partly" in d:
        return "🌤️"
    elif "cloud" in d:
        return "☁️"
    elif "wind" in d:
        return "🌬️"
    elif "rain" in d:
        return "🌧️"
    elif "thunder" in d:
        return "⛈️"
    elif "snow" in d:
        return "❄️"
    else:
        return "🌡️"
