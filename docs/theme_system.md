
# Theme System Architecture (Current Implementation)

This document describes how theming works in the Weather Dashboard application as currently implemented. The UI is built with **ttkbootstrap**, supporting dynamic themes and runtime theme switching. The system is designed for flexibility, with theme registration, application, and auto-refresh logic handled in the main window and utility functions.

## Core Modules and Responsibilities

1. **`core/custom_themes.py`**
   - Registers custom themes (e.g., `aj_darkly`, `aj_lightly`) using `ttkbootstrap.Style.register_theme`.
   - Provides helpers for theme fallback and available theme lists.

2. **`gui/tabbed_main_window.py`**
   - Central place for theme registration, application, and auto-refresh logic.
   - After creating the root window (`tb.Window()`), calls `register_custom_themes()` and applies the user's theme (with fallback if needed).
   - Manages a background thread for auto day/night mode, periodically checking location/time and switching themes as needed.
   - Handles all theme switching at runtime, including manual and automatic changes.

3. **`core/utils.py`**
   - Manages user settings (theme, auto mode, light/dark theme choices) in `data/user_settings.json`.
   - Provides helpers to load/save theme preferences and auto mode settings.

4. **`core/auto_theme.py`**
   - Contains logic to determine if it is day or night based on location and sunrise/sunset times.
   - Used by the main window's auto theme thread to select the appropriate theme.

5. **`gui/components/theme_component.py`**
   - Provides the UI controls for switching themes and toggling auto day/night mode.
   - Delegates actual theme switching to the main window, which manages the theme and triggers restyling.

6. **`data/user_settings.json`**
   - Stores the last selected theme, auto mode status, and user preferences for next launch.

## Typical Flow

1. On startup, the main window (`TabbedWeatherDashboard`) creates the root window, registers custom themes, and applies the user's last selected theme (with fallback if needed).
2. If auto mode is enabled, a background thread is started to periodically check the user's location and time, switching between light and dark themes as appropriate.
3. User interactions with the theme component update `user_settings.json` and trigger immediate theme changes.
4. All widgets are restyled as needed after a theme change.

## Extending the System

- Add new custom themes to `USER_THEMES` in `user.py` and register them in `custom_themes.py`.
- Update the auto theme logic in `core/auto_theme.py` if you want to use new triggers (e.g., weather-based themes).
- UI changes for theme switching should be handled in the main window and theme component, with all actual theme application and registration logic kept in the main window.

For details on the automatic day/night logic, see `docs/AUTO_THEME_IMPLEMENTATION.md`.
