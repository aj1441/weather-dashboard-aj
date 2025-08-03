# Quick Setup Guide

## ✅ Features Ready to Use:

1. **Weather Data**: Real-time weather information using Open-Meteo API (no API key required)
2. **Custom Themes**: Both `aj_darkly` and `aj_lightly` themes integrated
3. **Auto Day/Night**: Location-aware automatic theme switching
4. **Historical Data**: Weather history from 2010 to present
5. **Saved Cities**: Quick access to favorite locations

## 🔧 Setup Steps:

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Test the Application
```bash
python3 main.py
```

### 3. First Launch Tips
- The app will automatically detect your location for weather and theme settings
- You can toggle between auto and manual theme modes
- Save your favorite cities for quick access

## 🎨 Advanced Theme System:

### Auto Day/Night Mode
- **🌅 Auto Mode**: Automatically switches between light and dark themes based on local sunrise/sunset
- **Location Aware**: Updates theme based on the city you're viewing
- **Manual Override**: Full control with light/dark toggle when auto mode is disabled

### Theme Options
- **Light Mode**: Uses custom `aj_lightly` theme (clean, modern design)
- **Dark Mode**: Uses custom `aj_darkly` theme (eye-friendly dark scheme)
- **Persistence**: All theme preferences are saved automatically

### Custom Theme Integration
- **aj_darkly Colors**:
  - Primary: `#00bce9` (blue)
  - Background: `#121212` (dark)
  - Text: `#f5f5f5` (light)
  - Accent: `#ccb9ec` (purple)
- **aj_lightly Colors**:
  - [Your light theme colors here]

## 🔄 Auto-updating Features
- **30-minute Theme Refresh**: Keeps theme in sync with day/night cycle
- **Real-time Weather**: Current conditions and forecasts
- **Historical Data**: Automatically updates and maintains historical weather records

For detailed documentation on the theme system, see `docs/AUTO_THEME_IMPLEMENTATION.md`.
