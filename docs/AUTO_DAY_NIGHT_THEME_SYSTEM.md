# Auto Day/Night Theme System

## Overview

The Weather Dashboard features an intelligent **Auto Day/Night Theme System** that automatically switches between light and dark themes based on real-time sunrise and sunset data for any location worldwide. This system provides a seamless user experience by adapting the interface appearance to match the natural day/night cycle of the user's current location or any city they're viewing.

## Key Features

### 🌅 **Automatic Theme Switching**
- **Real-time Detection**: Uses actual sunrise/sunset times for precise day/night determination
- **Location-Aware**: Adapts theme based on the city you're currently viewing
- **Global Coverage**: Works for any location worldwide using coordinate-based calculations
- **Smooth Transitions**: Seamless switching between light and dark themes

### 🌍 **Location Intelligence**
- **IP Geolocation**: Automatically detects your approximate location on first launch
- **City-Based Updates**: Theme updates when you search for weather in different cities
- **Real-time Sync**: Continuously monitors and updates based on current time vs. sunrise/sunset
- **Manual Override**: Full control with manual light/dark toggle when auto mode is disabled

### ⚙️ **Advanced Configuration**
- **30-minute Refresh Cycle**: Automatically refreshes theme every 30 minutes to stay current
- **Persistent Settings**: All preferences are saved automatically between sessions
- **Fallback Logic**: Robust error handling with graceful fallbacks
- **Performance Optimized**: Efficient API calls with built-in caching

## Technical Architecture

### Core Components

#### 1. **Theme System Core** (`core/theme/theme_system.py`)
```python
class ThemeManager:
    """Main theme manager with dependency injection"""
    
    def __init__(self, config: ThemeConfig, settings: ThemeSettingsProtocol, 
                 auto_service: AutoThemeServiceProtocol, applicator: ThemeApplicatorProtocol)
```

**Key Responsibilities:**
- Coordinates between different theme services
- Manages theme application logic
- Handles fallback scenarios
- Provides clean API for theme operations

#### 2. **Auto Theme Service** (`services/theme_service.py`)
```python
class ThemeService:
    """Service for theme-related operations and management"""
    
    def apply_auto_theme(self) -> bool:
        """Apply automatic theme based on time and location"""
```

**Key Features:**
- Location detection and time zone handling
- Sunrise/sunset API integration  
- Theme selection logic
- Error handling and recovery

#### 3. **Theme Component** (`gui/components/theme_component.py`)
```python
class ThemeComponent:
    """GUI component for theme controls and user interaction"""
    
    def apply_auto_theme(self):
        """Apply auto theme and update UI state"""
```

**UI Features:**
- Auto mode toggle switch
- Manual theme selection buttons
- Visual feedback and status indicators
- Settings persistence

### Data Sources and APIs

#### **Sunrise-Sunset API Integration**
- **API**: `https://api.sunrise-sunset.org/json`
- **Input**: Latitude and longitude coordinates
- **Output**: Precise sunrise and sunset times in UTC
- **Caching**: Intelligent caching to minimize API calls
- **Error Handling**: Robust fallback mechanisms

**Example API Response:**
```json
{
  "results": {
    "sunrise": "2025-01-04T13:22:50+00:00",
    "sunset": "2025-01-04T23:45:12+00:00",
    "solar_noon": "2025-01-04T18:34:01+00:00",
    "day_length": "10:22:22"
  },
  "status": "OK"
}
```

#### **IP Geolocation Service**
- **Purpose**: Detect user's approximate location for initial theme setup
- **Fallback**: Manual location entry if geolocation fails
- **Privacy**: Only used for theme determination, not stored permanently

### Theme Configuration

#### **ThemeConfig Class**
```python
@dataclass(frozen=True)
class ThemeConfig:
    """Immutable theme system configuration"""
    default_light_theme: str = "aj_lightly"
    default_dark_theme: str = "aj_darkly"
    auto_enabled_by_default: bool = True
    fallback_theme: str = "flatly"
    settings_file: str = "data/user_settings.json"
```

#### **Theme Registry**
```python
class ThemeRegistry:
    """Central registry for all theme definitions"""
    
    LIGHT_THEMES = [
        "aj_lightly", "pulse", "flatly", "litera", "minty", 
        "lumen", "sandstone", "yeti", "united", "morph"
    ]
    
    DARK_THEMES = [
        "aj_darkly", "darkly", "superhero", "solar", "cyborg", "vapor"
    ]
```

## User Experience Flow

### 1. **First Launch**
```
App Startup → Location Detection → Get Sunrise/Sunset → Apply Initial Theme
```

### 2. **Location Change**
```
User Searches City → Get Coordinates → Check Day/Night → Update Theme
```

### 3. **Time-Based Updates**
```
30-Minute Timer → Check Current Time → Compare to Sunrise/Sunset → Apply Theme
```

### 4. **Manual Override**
```
User Toggles Auto Mode → Disable Auto Updates → Apply Manual Theme
```

## Implementation Details

### **Auto Theme Logic**
```python
def _get_auto_theme(self) -> str:
    """Determine appropriate theme for auto mode"""
    is_day = self._auto_service.is_daytime()
    
    if is_day is None:
        # Can't determine time, use manual theme or default
        manual = self._settings.get_current_theme()
        return manual if manual else self._config.fallback_theme
    
    if is_day:
        theme = self._settings.get_light_theme()
    else:
        theme = self._settings.get_dark_theme()
        
    # Validate theme and use fallback if needed
    return self._get_fallback_theme(theme)
```

### **Fallback Chain System**
```python
FALLBACK_CHAINS = {
    "aj_lightly": ["pulse", "flatly", "litera"],
    "aj_darkly": ["darkly", "superhero", "cyborg"],
    "pulse": ["flatly", "litera", "minty"],
    "darkly": ["superhero", "cyborg", "vapor"]
}
```

### **Time Zone Handling**
- All calculations performed in UTC to avoid time zone issues
- Local time conversion handled by the system
- Daylight Saving Time automatically accounted for
- Cross-timezone accuracy when viewing different cities

## Performance Optimizations

### **Caching Strategy**
- **Sunrise/Sunset Data**: Cached for 24 hours per location
- **Theme Preferences**: Immediately persisted to disk
- **API Responses**: Intelligent caching with TTL (Time To Live)
- **Location Data**: Cached to minimize geolocation API calls

### **Resource Management**
- **Minimal API Calls**: Only fetch data when necessary
- **Background Updates**: Non-blocking theme updates
- **Memory Efficient**: Clean up unused theme resources
- **Session Reuse**: Persistent HTTP sessions for API calls

### **Error Handling**
```python
def apply_auto_theme(self) -> bool:
    """Apply automatic theme with comprehensive error handling"""
    try:
        # Primary theme application logic
        self.theme_manager.apply_auto_theme()
        return True
    except APIError as e:
        # API-specific error handling
        self.logger.warning(f"API error, using cached data: {e}")
        return self._apply_cached_theme()
    except Exception as e:
        # Fallback to manual theme
        self.logger.error(f"Auto theme failed, falling back: {e}")
        return self._apply_fallback_theme()
```

## Configuration Options

### **User Settings** (`data/user_settings.json`)
```json
{
  "theme": {
    "auto_enabled": true,
    "current_theme": "aj_lightly",
    "light_theme": "aj_lightly",
    "dark_theme": "aj_darkly",
    "last_location": {
      "latitude": 40.7128,
      "longitude": -74.0060,
      "city": "New York",
      "state": "NY"
    },
    "last_sunrise": "2025-01-04T12:20:00Z",
    "last_sunset": "2025-01-04T22:15:00Z",
    "cache_timestamp": "2025-01-04T10:00:00Z"
  }
}
```

### **Environment Variables**
```bash
# Optional theme system configuration
THEME_AUTO_ENABLED=true
THEME_DEFAULT_LIGHT=aj_lightly
THEME_DEFAULT_DARK=aj_darkly
THEME_REFRESH_INTERVAL=1800  # 30 minutes in seconds
THEME_CACHE_DURATION=86400   # 24 hours in seconds
```

## Troubleshooting

### **Common Issues**

#### **Theme Not Updating**
**Problem**: Auto day/night theme doesn't change  
**Solutions**:
1. Check that auto mode is enabled in settings
2. Verify internet connection for sunrise/sunset API
3. Wait for the 30-minute refresh cycle
4. Try manually toggling themes to test functionality
5. Check log file for API errors

#### **Wrong Theme for Location**
**Problem**: Theme doesn't match local time  
**Solutions**:
1. Search for your current city to update location
2. Check that system time zone is correct
3. Verify location permissions if using geolocation
4. Clear theme cache and restart application

#### **API Connection Issues**
**Problem**: Cannot fetch sunrise/sunset data  
**Solutions**:
1. Check internet connectivity
2. Verify firewall allows outbound connections
3. Check proxy settings if behind corporate firewall
4. Application will use cached data or fallback themes

### **Debug Mode**
Enable detailed logging for theme system debugging:

```python
import logging
logging.getLogger('core.theme').setLevel(logging.DEBUG)
logging.getLogger('services.theme_service').setLevel(logging.DEBUG)
```

**Debug Output Example**:
```
[DEBUG] ThemeManager: Auto mode enabled, checking day/night status
[DEBUG] AutoThemeService: Location: (40.7128, -74.0060) New York, NY
[DEBUG] AutoThemeService: Current time: 2025-01-04 15:30:00 UTC
[DEBUG] AutoThemeService: Sunrise: 2025-01-04 12:20:00 UTC
[DEBUG] AutoThemeService: Sunset: 2025-01-04 22:15:00 UTC
[DEBUG] AutoThemeService: Result: daytime=True
[DEBUG] ThemeManager: Applying light theme: aj_lightly
[INFO] ThemeManager: Applied theme: aj_lightly
```

## API Reference

### **Main Classes**

#### **ThemeManager**
```python
def apply_current_theme() -> bool:
    """Apply the current theme based on settings"""

def set_manual_theme(theme_name: str) -> bool:
    """Set a manual theme and disable auto mode"""

def enable_auto_mode(light_theme: str = None, dark_theme: str = None) -> bool:
    """Enable auto theme mode with optional custom themes"""

def disable_auto_mode() -> bool:
    """Disable auto mode and use current manual theme"""
```

#### **ThemeService**
```python
def apply_auto_theme() -> bool:
    """Apply automatic theme based on time and location"""

def toggle_auto_mode() -> bool:
    """Toggle automatic theme mode on/off"""

def get_current_theme() -> str:
    """Get the currently applied theme name"""
```

## Integration Examples

### **Basic Auto Theme Setup**
```python
from services.theme_service import ThemeService
from core.theme.theme_system import ThemeConfig

# Initialize theme service
config = ThemeConfig()
theme_service = ThemeService(config, app_instance)

# Enable auto mode
theme_service.apply_auto_theme()
```

### **Custom Theme Configuration**
```python
# Set custom themes for auto mode
theme_service.enable_auto_mode(
    light_theme="aj_lightly",
    dark_theme="aj_darkly"
)
```

### **Manual Override**
```python
# Temporarily override auto mode
theme_service.set_manual_theme("superhero")

# Re-enable auto mode later
theme_service.enable_auto_mode()
```

## Future Enhancements

### **Planned Features**
1. **Weather-Aware Themes**: Adjust theme based on weather conditions
2. **Multiple Location Support**: Track themes for multiple saved cities
3. **Advanced Scheduling**: Custom time-based theme rules
4. **Theme Animation**: Smooth transitions between theme changes
5. **Accessibility Mode**: High contrast themes for better accessibility

### **Performance Improvements**
1. **Local Sunrise Calculation**: Reduce API dependency with local calculations
2. **Predictive Caching**: Pre-cache sunrise/sunset data for frequent locations
3. **Background Sync**: Update theme data in background threads
4. **Battery Optimization**: Reduce update frequency on battery-powered devices

---

*This auto day/night theme system provides a sophisticated, user-friendly way to automatically adapt the application's appearance to match natural lighting conditions, enhancing user comfort and providing a premium experience.*