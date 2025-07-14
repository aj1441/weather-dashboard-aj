# Icon Configuration File
# This file documents all available icons and their usage

## Emoji Icons (Built-in)
# Weather
sunny = "☀️"
cloudy = "☁️"
rainy = "🌧️"
snowy = "❄️"
partly_cloudy = "🌤️"
thunderstorm = "⛈️"
windy = "🌬️"
temperature = "🌡️"

# UI Actions
save = "💾"
star = "⭐"
heart = "❤️"
location = "📍"
search = "🔍"
refresh = "🔄"
settings = "⚙️"
chart = "📊"
history = "📋"
info = "ℹ️"
warning = "⚠️"
error = "❌"
success = "✅"

# Navigation
home = "🏠"
back = "⬅️"
forward = "➡️"
up = "⬆️"
down = "⬇️"

# Theme
light = "☀️"
dark = "🌙"

# Weather Details
humidity = "💧"
pressure = "🌡️"
wind = "🌬️"
visibility = "👁️"

## File Icons (Place files in assets/icons/)
# Expected formats: .png, .svg, .ico, .jpg, .jpeg
# Naming convention: [icon_name].[extension]
# Examples:
# - save_icon.png
# - weather_sunny.svg
# - app_logo.ico

## Usage Examples
# 1. Get emoji icon:
#    icon = get_icon("save")  # Returns "💾"
#
# 2. Create button with icon:
#    btn = create_icon_button(parent, "Save City", "save", command=save_func, bootstyle="success-outline")
#
# 3. Get weather icon:
#    weather_emoji = get_weather_icon("sunny")  # Returns "☀️"
#
# 4. Load custom image:
#    img = icon_manager.load_image("logo", size=(100, 100))
