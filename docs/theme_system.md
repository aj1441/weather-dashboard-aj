# Theme System Architecture

This document provides an overview of how theming works inside the Weather Dashboard application. The user interface is built with **ttkbootstrap**, which supports dynamic themes similar to those found in modern desktop applications. The system has been structured so that new themes or theme logic can be added without touching unrelated parts of the codebase.

## Core Modules

1. **`core/custom_themes.py`**
   - Registers the custom themes `aj_darkly` and `aj_lightly`.
   - Uses `ttkbootstrap.Style.register_theme` to make these themes available to the rest of the application.
   - Provides helper functions to detect custom themes and list available light and dark options.

2. **`core/theme_manager.py`**
   - Provides the `ThemeManager` class which wraps all direct interactions with `ttkbootstrap.Style`.
   - Implements fallback logic so that if a preferred theme is missing, a sensible alternative is chosen automatically.
   - Offers helpers to query whether a theme is light or dark and to obtain the current active theme.

3. **`core/auto_theme.py`**
   - Contains the `AutoThemeManager` which determines whether a light or dark theme should be used based on sunrise and sunset times.
   - Retrieves the user's location via IP geolocation and fetches sunrise/sunset data from an external service.
   - Exposes utility functions `get_auto_theme()` and `is_daytime()` used throughout the project.

4. **`gui/components/theme_component.py`**
   - Provides the GUI controls for switching themes and toggling the automatic day/night mode.
   - Communicates with `ThemeManager` and `AutoThemeManager` to apply the correct theme and persist the user's preference.

5. **`data/user_settings.json`**
   - Stores the last selected theme and whether auto mode is enabled so the same settings are used on the next launch.

## Typical Flow

1. At startup, `register_custom_themes()` is called to ensure custom definitions are available.
2. The `ThemeManager` reads the user's saved preference and applies that theme using `Style.theme_use`.
3. If auto mode is enabled, `AutoThemeManager.get_recommended_theme()` determines the appropriate light or dark theme and `ThemeManager` applies it.
4. User interactions through the theme component update `user_settings.json` and immediately change the application style.

## Extending the System

- Add new custom themes to `USER_THEMES` in `user.py` and register them in `custom_themes.py`.
- Modify `ThemeManager` if additional fallback or categorization logic is required.
- Update `AutoThemeManager` when introducing new triggers (for example weather-based themes) while keeping the API stable for the GUI components.

For a detailed breakdown of the automatic day/night logic see `docs/AUTO_THEME_IMPLEMENTATION.md`.
