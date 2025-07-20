# Weather Dashboard Theme System Architecture

## Overview

The Weather Dashboard features a modern, maintainable theme management system built using Python best practices including dependency injection, protocol-based interfaces, and the Single Responsibility Principle. The system provides automatic day/night theme switching based on geographical location and sunrise/sunset calculations, while also supporting manual theme selection.

## Core Architecture

### Design Principles

1. **Single Responsibility Principle**: Each component has one clear purpose
2. **Dependency Injection**: Components receive their dependencies, making them testable
3. **Protocol-based Interfaces**: Use of typing.Protocol for loose coupling
4. **Immutable Configuration**: @dataclass(frozen=True) for thread-safe config
5. **Composition over Inheritance**: Favor object composition for flexibility

### Key Components

```
core/
├── theme_system.py          # Core protocols, ThemeManager, ThemeRegistry
├── theme_implementations.py # Concrete implementations
└── theme_factory.py        # Factory for easy instantiation
```

## File Structure and Responsibilities

### 1. `core/theme_system.py`

**Core theme management architecture with protocols and registry.**

#### Key Classes:

- **`ThemeConfig`**: Immutable configuration dataclass
- **`ThemeRegistry`**: Central registry for all theme definitions
- **`ThemeManager`**: Main coordinator using dependency injection
- **Protocols**: `ThemeSettingsProtocol`, `AutoThemeServiceProtocol`, `ThemeApplicatorProtocol`

#### ThemeRegistry Features:
```python
LIGHT_THEMES = ["aj_lightly", "pulse", "flatly", "litera", ...]
DARK_THEMES = ["aj_darkly", "darkly", "superhero", "cyborg", ...]
CUSTOM_THEMES = {}  # Loaded from user.py
FALLBACK_CHAINS = {...}  # Theme fallback logic
```

### 2. `core/theme_implementations.py`

**Concrete implementations of theme system protocols.**

#### Key Classes:

- **`JsonThemeSettings`**: Persists theme preferences to JSON
- **`LocationBasedAutoThemeService`**: Determines day/night using location
- **`SimpleTimeBasedAutoThemeService`**: Simple time-based fallback
- **`TtkBootstrapThemeApplicator`**: Applies themes to ttkbootstrap
- **Mock classes**: For testing purposes

#### Special Features:
- Runtime-only auto mode state (never persisted)
- Graceful error handling for widget lifecycle issues
- Class-level theme registration prevention

### 3. `core/theme_factory.py`

**Factory pattern for easy theme manager creation.**

```python
def create_theme_manager(app_instance=None, **config_kwargs) -> ThemeManager:
    """One-line theme manager creation with sensible defaults"""
```

### 4. `gui/components/theme_component.py`

**UI component for theme controls using the new system.**

#### Features:
- Auto day/night mode toggle
- Manual light/dark theme toggle
- Real-time UI state updates
- Backward compatibility functions

## Theme Configuration

### User Settings Storage (`data/user_settings.json`)

```json
{
  "theme": "aj_darkly",           // Current manual theme
  "light_theme": "aj_lightly",    // Preferred light theme for auto mode
  "dark_theme": "aj_darkly"       // Preferred dark theme for auto mode
}
```

**Important**: Auto mode state is runtime-only and never saved. The app always starts with auto mode enabled.

### Custom Themes (`user.py`)

Custom themes are defined in `user.py` and automatically registered:

```python
USER_THEMES = {
    "aj_darkly": {
        "type": "dark",
        "colors": {
            "primary": "#007bff",
            "bg": "#212529",
            "fg": "#fff",
            # ... more colors
        }
    },
    "aj_lightly": {
        "type": "light", 
        "colors": {
            "primary": "#007bff",
            "bg": "#fff",
            "fg": "#212529",
            # ... more colors
        }
    }
}
```

## System Flow

### Application Startup

```mermaid
graph TD
    A[App.run()] --> B[create_theme_manager()]
    B --> C[ThemeFactory.create_default()]
    C --> D[Register custom themes from user.py]
    D --> E[Initialize with auto_enabled=True]
    E --> F[Apply current theme]
    F --> G[LocationService determines day/night]
    G --> H[Apply appropriate light/dark theme]
```

### Auto Mode Logic

1. **Always Enabled at Startup**: App starts with `auto_enabled=True`
2. **Location Detection**: Uses IP geolocation to get coordinates
3. **Sunrise/Sunset Calculation**: Calls sunrise-sunset.org API
4. **Theme Selection**: 
   - Daytime → `light_theme` setting (default: "aj_lightly")
   - Nighttime → `dark_theme` setting (default: "aj_darkly")
5. **Fallback Chain**: If theme unavailable, uses fallback themes

### Manual Mode Logic

1. **User Toggles Off Auto Mode**: Sets `auto_enabled=False` (runtime only)
2. **Manual Theme Selection**: Uses saved `theme` preference
3. **Toggle Behavior**: Light/Dark toggle uses saved light/dark preferences
4. **Persistence**: Only manual theme choice is saved, not auto mode state

### Theme Application Process

```mermaid
graph TD
    A[apply_current_theme()] --> B{Auto mode enabled?}
    B -->|Yes| C[Get auto theme]
    B -->|No| D[Get manual theme]
    C --> E[Check daytime status]
    E --> F[Select light/dark theme]
    F --> G[Apply theme with fallback]
    D --> G
    G --> H{Success?}
    H -->|No| I[Try fallback chain]
    H -->|Yes| J[Theme applied]
    I --> J
```

## Key Features

### 1. Automatic Day/Night Detection

- **Location-based**: Uses IP geolocation + sunrise/sunset calculations
- **Caching**: 5-minute cache for location/sun data
- **Fallback**: Simple time-based detection (6 AM - 6 PM)
- **Error Handling**: Graceful degradation when services unavailable

### 2. Settings Behavior

- **Auto Mode**: Always defaults to enabled, never saved to settings
- **Manual Preferences**: Only light/dark theme choices are saved
- **Runtime State**: Auto mode can be toggled during runtime but resets on restart
- **Persistence**: Manual theme selection persists across sessions

### 3. Theme Registration

- **Custom Themes**: Loaded from `user.py` with error handling
- **Fallback Themes**: Built-in theme definitions if user.py unavailable
- **Registration Once**: Class-level flag prevents duplicate registration
- **Validation**: Theme availability checked before application

### 4. Error Handling

- **Widget Lifecycle**: Handles ttkbootstrap "invalid command name" errors
- **Network Failures**: Graceful fallback when location services fail
- **Missing Themes**: Automatic fallback chain with ultimate fallback
- **Import Errors**: Continues with reduced functionality

## Usage Examples

### Basic Usage

```python
from core.theme_factory import create_theme_manager

# Create theme manager with defaults
theme_manager = create_theme_manager(app_instance)

# Apply current theme (auto-determined or manual)
theme_manager.apply_current_theme()

# Check current state
print(f"Auto enabled: {theme_manager.is_auto_enabled()}")
print(f"Current theme: {theme_manager.current_theme}")
```

### Manual Theme Control

```python
# Set manual theme (disables auto mode)
theme_manager.set_manual_theme("aj_darkly")

# Enable auto mode with custom preferences
theme_manager.enable_auto_mode(
    light_theme="pulse",
    dark_theme="superhero"
)

# Disable auto mode (uses manual theme)
theme_manager.disable_auto_mode()
```

### UI Component Integration

```python
from gui.components.theme_component import ThemeComponent

# Create theme component
theme_component = ThemeComponent(parent_frame, theme_manager)

# Component handles:
# - Auto mode toggle
# - Manual light/dark toggle
# - UI state updates
# - Error handling
```

## Testing Architecture

### Mock Implementations

The system includes comprehensive mock implementations for testing:

- **`MockThemeSettings`**: In-memory settings simulation
- **`MockAutoThemeService`**: Controllable day/night simulation
- **`MockThemeApplicator`**: Theme application tracking

### Test Coverage

```python
# Example test setup
def test_auto_mode():
    config = ThemeConfig()
    settings = MockThemeSettings(config)
    auto_service = MockAutoThemeService(is_day=True)
    applicator = MockThemeApplicator()
    
    manager = ThemeManager(config, settings, auto_service, applicator)
    assert manager.current_theme == "aj_lightly"
```

## Migration from Legacy System

### What Was Removed

- **Scattered Files**: Consolidated 7+ theme files into 3 focused modules
- **Code Duplication**: Reduced theme-related code by ~40%
- **Tight Coupling**: Replaced with dependency injection
- **Hardcoded Logic**: Replaced with configurable, testable components

### Backward Compatibility

- **Legacy Functions**: Maintained in theme_component.py for compatibility
- **Settings Format**: Existing user_settings.json continues to work
- **Theme Names**: All existing theme names preserved

## Troubleshooting

### Common Issues

1. **"Invalid command name" errors**: 
   - Expected during theme switching
   - Handled gracefully, not actual failures

2. **Location service failures**:
   - Falls back to time-based detection
   - Check internet connectivity
   - Verify firewall settings

3. **Custom themes not loading**:
   - Check user.py format
   - Verify USER_THEMES dictionary structure
   - Check application logs for import errors

4. **Auto mode not working**:
   - Auto mode resets to enabled on app restart
   - Check if location services are blocked
   - Verify sunrise/sunset API accessibility

### Debug Information

Enable debug logging to see theme system operations:

```python
import logging
logging.getLogger('core.theme_implementations').setLevel(logging.DEBUG)
```

## Performance Considerations

- **Lazy Loading**: Location service loaded only when needed
- **Caching**: 5-minute cache for location/sunrise data
- **Single Registration**: Themes registered once per application lifecycle
- **Minimal I/O**: Settings loaded/saved only when changed

## Security Considerations

- **Network Requests**: Uses HTTPS for location/sunrise APIs
- **Error Handling**: No sensitive data exposed in error messages
- **Input Validation**: Theme names validated before application
- **Timeout Handling**: 10-second timeouts for API calls

This architecture provides a robust, maintainable, and extensible theme management system that follows Python best practices while delivering a smooth user experience with intelligent automatic theme switching.