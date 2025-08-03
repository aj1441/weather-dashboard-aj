# Theme System Overview

## Introduction

The Weather Dashboard features a comprehensive **Theme System** that provides multiple ways to customize the application's appearance. The system includes automatic theme switching, custom-designed themes, manual theme selection, and custom widgets that maintain consistency across the entire application.

## Theme System Components

### 🌅 **Auto Day/Night Theme System**
The flagship feature that automatically switches themes based on real-time sunrise/sunset data.

**Key Features:**
- Location-aware automatic switching
- Real-time sunrise/sunset detection
- 30-minute refresh cycles
- Global location support
- Manual override capabilities

**📖 Full Documentation**: See [AUTO_DAY_NIGHT_THEME_SYSTEM.md](AUTO_DAY_NIGHT_THEME_SYSTEM.md) for complete details.

### 🎨 **Custom Theme Collection**
Two beautiful custom themes designed specifically for the Weather Dashboard using the ttkbootstrap theme creator.

#### **aj_lightly** (Light Theme)
- **Design Philosophy**: Clean, modern, and eye-friendly for daytime use
- **Primary Colors**: Professional blue and white palette
- **Use Case**: Default light theme for auto day/night mode
- **Features**: Custom widget styling, optimized contrast, modern appearance

#### **aj_darkly** (Dark Theme)  
- **Design Philosophy**: Eye-friendly dark scheme for nighttime use
- **Color Palette**:
  - Primary: `#00bce9` (cyan blue)
  - Background: `#121212` (dark charcoal)
  - Text: `#f5f5f5` (light gray)
  - Accent: `#ccb9ec` (soft purple)
- **Use Case**: Default dark theme for auto day/night mode
- **Features**: Low-light optimized, reduced eye strain, modern dark aesthetic

### 🔧 **Manual Theme Selection**
Complete user control over theme selection when auto mode is disabled.

**Available Themes:**
- **Light Themes**: `aj_lightly`, `pulse`, `flatly`, `litera`, `minty`, `lumen`, `sandstone`, `yeti`, `united`, `morph`, `journal`, `cosmo`, `simplex`, `cerulean`
- **Dark Themes**: `aj_darkly`, `darkly`, `superhero`, `solar`, `cyborg`, `vapor`

**User Controls:**
- Toggle between Auto and Manual modes
- Light/Dark theme selection buttons
- Instant theme application
- Settings persistence

### 🧩 **Custom Widget System**
App-wide custom widgets that maintain consistency across all themes.

**Custom Components:**
- **Theme-Aware Buttons**: Automatically adapt to current theme colors
- **Custom Input Fields**: Consistent styling across light and dark modes
- **Branded Components**: Weather-specific UI elements
- **Icon Integration**: Custom weather icons that match theme aesthetics

## Architecture Overview

### **Core Theme Stack**
```
┌─────────────────────────────────────┐
│        User Interface Layer        │
│  (Theme Controls & Visual Feedback) │
├─────────────────────────────────────┤
│       Theme Management Layer       │
│   (ThemeManager & ThemeService)     │
├─────────────────────────────────────┤
│        Theme Registry Layer        │
│  (Theme Definitions & Fallbacks)    │
├─────────────────────────────────────┤
│       Auto Theme Service Layer     │
│  (Location & Time-based Logic)      │
├─────────────────────────────────────┤
│        ttkbootstrap Foundation      │
│    (Base Theme System & Widgets)    │
└─────────────────────────────────────┘
```

### **Key Files and Components**

| Component | File Path | Purpose |
|-----------|-----------|---------|
| **Theme System Core** | `core/theme/theme_system.py` | Main theme management architecture |
| **Theme Service** | `services/theme_service.py` | Business logic and API interface |
| **Theme Component** | `gui/components/theme_component.py` | User interface controls |
| **Custom Themes** | `core/theme/theme_implementations.py` | Custom theme definitions |
| **Theme Factory** | `core/theme/theme_factory.py` | Theme creation and registration |
| **User Themes** | `core/theme/user_themes.py` | User-customizable theme definitions |

## Usage Modes

### **1. Auto Mode (Default)**
```python
# Theme automatically switches based on location and time
theme_service.enable_auto_mode()
```
- **Morning/Day**: Switches to `aj_lightly` (or custom light theme)
- **Evening/Night**: Switches to `aj_darkly` (or custom dark theme)
- **Updates**: Every 30 minutes automatically
- **Location**: Updates when searching different cities

### **2. Manual Mode**
```python
# User has full control over theme selection
theme_service.set_manual_theme("superhero")  # Dark theme
theme_service.set_manual_theme("pulse")      # Light theme
```
- **User Choice**: Select any available theme
- **Persistence**: Selection saved between sessions
- **Override**: Disables automatic switching
- **Instant**: Theme applies immediately

### **3. Hybrid Mode**
```python
# Custom auto mode with user-selected themes
theme_service.enable_auto_mode(
    light_theme="minty",    # Custom light choice
    dark_theme="cyborg"     # Custom dark choice
)
```
- **Best of Both**: Automatic switching with user preferences
- **Customization**: Choose preferred light and dark themes
- **Flexibility**: Can change auto themes without disabling auto mode

## Theme Creation Process

### **Custom Theme Development**
Our custom themes (`aj_lightly` and `aj_darkly`) were created using the **ttkbootstrap theme creator**:

1. **Design Phase**:
   - Color palette selection based on weather app aesthetics
   - Accessibility considerations (contrast ratios, readability)
   - User experience optimization (eye strain reduction)

2. **Implementation Phase**:
   ```python
   # Theme definition structure
   USER_THEMES = {
       "aj_darkly": {
           "type": "dark",
           "colors": {
               "primary": "#00bce9",
               "bg": "#121212",
               "fg": "#f5f5f5",
               # ... complete color specification
           }
       }
   }
   ```

3. **Testing Phase**:
   - Cross-platform compatibility testing
   - Widget appearance verification
   - Performance impact assessment

### **Custom Widget Integration**
Custom widgets are designed to work seamlessly across all themes:

```python
# Example: Theme-aware button creation
def create_weather_button(parent, text, command, style_type="primary"):
    """Create a weather-themed button that adapts to current theme"""
    button = tb.Button(
        parent, 
        text=text, 
        command=command,
        bootstyle=f"{style_type}-outline"  # Adapts to theme colors
    )
    return button
```

## Configuration and Settings

### **User Settings Storage**
Theme preferences are stored in `data/user_settings.json`:

```json
{
  "theme": {
    "auto_enabled": true,
    "current_theme": "aj_lightly",
    "light_theme": "aj_lightly",
    "dark_theme": "aj_darkly",
    "custom_themes_enabled": true
  }
}
```

### **Theme Registry Configuration**
```python
# Theme categorization and fallback chains
LIGHT_THEMES = ["aj_lightly", "pulse", "flatly", "litera", ...]
DARK_THEMES = ["aj_darkly", "darkly", "superhero", "solar", ...]

FALLBACK_CHAINS = {
    "aj_lightly": ["pulse", "flatly", "litera"],
    "aj_darkly": ["darkly", "superhero", "cyborg"]
}
```

## User Interface Controls

### **Theme Control Panel**
Located in the main interface, the theme controls provide:

- **🌅 Auto Toggle**: Enable/disable automatic theme switching
- **☀️ Light Button**: Manual light theme selection (when auto disabled)
- **🌙 Dark Button**: Manual dark theme selection (when auto disabled)
- **Status Indicator**: Shows current theme and mode
- **Settings Persistence**: All choices automatically saved

### **Visual Feedback**
- **Immediate Application**: Themes apply instantly when changed
- **Status Display**: Current theme name and mode shown
- **Loading States**: Smooth transitions during theme changes
- **Error Handling**: User-friendly messages for theme issues

## Performance Considerations

### **Optimization Features**
- **Lazy Loading**: Themes loaded only when needed
- **Caching**: Theme data cached in memory
- **Resource Management**: Unused theme resources cleaned up
- **Efficient Updates**: Only affected components updated during theme changes

### **Memory Usage**
- **Lightweight**: Minimal memory footprint per theme
- **Cleanup**: Automatic cleanup of unused theme resources
- **Caching Strategy**: Intelligent caching with memory limits

## Troubleshooting

### **Common Issues**

#### **Theme Not Loading**
**Symptoms**: Default theme used instead of selected theme  
**Solutions**:
1. Check if custom themes are properly registered
2. Verify theme name spelling in settings
3. Check theme file integrity
4. Review fallback chain in logs

#### **Auto Mode Not Working**
**Symptoms**: Theme doesn't change automatically  
**Solutions**:
1. Verify auto mode is enabled in settings
2. Check internet connection for sunrise/sunset data
3. Review location detection settings
4. See [AUTO_DAY_NIGHT_THEME_SYSTEM.md](AUTO_DAY_NIGHT_THEME_SYSTEM.md) for detailed troubleshooting

#### **Custom Widget Styling Issues**
**Symptoms**: Widgets don't match theme colors  
**Solutions**:
1. Ensure widgets use theme-aware styling
2. Check bootstyle parameters
3. Verify widget inheritance from theme base classes
4. Review custom widget implementation

## Development Guidelines

### **Adding New Themes**
1. **Define Theme**: Add theme definition to `core/theme/user_themes.py`
2. **Register Theme**: Add to appropriate theme category list
3. **Test Compatibility**: Verify all widgets work correctly
4. **Add Fallbacks**: Define fallback chain for reliability

### **Creating Theme-Aware Widgets**
```python
class WeatherWidget(tb.Frame):
    """Example theme-aware widget"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.setup_ui()
        
    def setup_ui(self):
        # Use bootstyle for theme compatibility
        self.button = tb.Button(
            self,
            text="Weather Action",
            bootstyle="primary-outline"  # Adapts to theme
        )
```

### **Best Practices**
1. **Use bootstyle**: Always use ttkbootstrap's bootstyle for theme compatibility
2. **Avoid hardcoded colors**: Let themes handle color management
3. **Test all themes**: Verify appearance across light and dark themes
4. **Handle fallbacks**: Provide graceful degradation for missing themes

## API Reference

### **Main Classes**

#### **ThemeService**
```python
def apply_theme(theme_name: str) -> bool
def apply_auto_theme() -> bool
def toggle_auto_mode() -> bool
def get_current_theme() -> str
```

#### **ThemeManager**
```python
def set_manual_theme(theme_name: str) -> bool
def enable_auto_mode(light_theme: str = None, dark_theme: str = None) -> bool
def disable_auto_mode() -> bool
def get_available_themes() -> List[str]
```

## Integration Examples

### **Basic Theme Usage**
```python
from services.theme_service import ThemeService

# Initialize theme service
theme_service = ThemeService(config, app_instance)

# Apply a specific theme
theme_service.apply_theme("aj_darkly")

# Enable auto mode with defaults
theme_service.apply_auto_theme()
```

### **Custom Theme Setup**
```python
# Enable auto mode with custom theme preferences
theme_service.enable_auto_mode(
    light_theme="aj_lightly",
    dark_theme="aj_darkly"
)

# Or set manual theme
theme_service.set_manual_theme("superhero")
```

---

## Related Documentation

- **[AUTO_DAY_NIGHT_THEME_SYSTEM.md](AUTO_DAY_NIGHT_THEME_SYSTEM.md)**: Complete auto theme documentation
- **[USER_GUIDE.md](USER_GUIDE.md#theme-system)**: User-facing theme instructions
- **[DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md)**: Technical implementation details

---

*The Theme System provides a comprehensive, user-friendly way to customize the Weather Dashboard's appearance while maintaining consistency and accessibility across all components.*
