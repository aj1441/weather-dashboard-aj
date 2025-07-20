"""
Concrete implementations of theme system protocols.

This module provides the actual implementations for theme settings storage,
auto theme determination, and theme application.
"""

import json
import os
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime

try:
    import ttkbootstrap as tb
    from ttkbootstrap.style import ThemeDefinition
except ImportError:
    tb = None
    ThemeDefinition = None

from .theme_system import (
    ThemeConfig, 
    ThemeSettingsProtocol, 
    AutoThemeServiceProtocol, 
    ThemeApplicatorProtocol,
    ThemeRegistry
)

logger = logging.getLogger(__name__)


# ============================================================================
# Settings Implementation
# ============================================================================

class JsonThemeSettings:
    """JSON-based theme settings storage implementation."""
    
    def __init__(self, config: ThemeConfig):
        self._config = config
        self._settings_file = config.settings_file
        self._ensure_data_directory()
        self._logger = logging.getLogger(__name__)
        # Runtime state - auto mode always starts enabled but can be toggled during runtime
        self._auto_enabled = config.auto_enabled_by_default
    
    def _ensure_data_directory(self) -> None:
        """Create data directory if it doesn't exist."""
        data_dir = os.path.dirname(self._settings_file)
        if data_dir:
            os.makedirs(data_dir, exist_ok=True)
    
    def _load_settings(self) -> Dict[str, Any]:
        """Load settings from JSON file."""
        if os.path.exists(self._settings_file):
            try:
                with open(self._settings_file, "r") as f:
                    return json.load(f)
            except Exception as e:
                self._logger.warning(f"Error loading settings: {e}")
        
        # Return defaults - note: auto_theme_mode is not saved, only manual theme preferences
        return {
            "theme": self._config.fallback_theme,
            "light_theme": self._config.default_light_theme,
            "dark_theme": self._config.default_dark_theme
        }
    
    def _save_settings(self, settings: Dict[str, Any]) -> bool:
        """Save settings to JSON file."""
        try:
            with open(self._settings_file, "w") as f:
                json.dump(settings, f, indent=2)
            return True
        except Exception as e:
            self._logger.error(f"Failed to save settings: {e}")
            return False
    
    def get_current_theme(self) -> str:
        """Get the currently selected theme."""
        settings = self._load_settings()
        return settings.get("theme", self._config.fallback_theme)
    
    def set_current_theme(self, theme: str) -> None:
        """Set the current theme."""
        settings = self._load_settings()
        settings["theme"] = theme
        self._save_settings(settings)
    
    def is_auto_enabled(self) -> bool:
        """Check if auto theme mode is enabled."""
        return self._auto_enabled
    
    def set_auto_enabled(self, enabled: bool) -> None:
        """Enable or disable auto theme mode - runtime only, not saved."""
        self._auto_enabled = enabled
        # Note: We intentionally don't save this to settings - app always starts with auto enabled
    
    def get_light_theme(self) -> str:
        """Get the light theme for auto mode."""
        settings = self._load_settings()
        return settings.get("light_theme", self._config.default_light_theme)
    
    def set_light_theme(self, theme: str) -> None:
        """Set the light theme for auto mode."""
        settings = self._load_settings()
        settings["light_theme"] = theme
        self._save_settings(settings)
    
    def get_dark_theme(self) -> str:
        """Get the dark theme for auto mode."""
        settings = self._load_settings()
        return settings.get("dark_theme", self._config.default_dark_theme)
    
    def set_dark_theme(self, theme: str) -> None:
        """Set the dark theme for auto mode."""
        settings = self._load_settings()
        settings["dark_theme"] = theme
        self._save_settings(settings)


# ============================================================================
# Auto Theme Service Implementation
# ============================================================================

class LocationBasedAutoThemeService:
    """Auto theme service using location and sunrise/sunset times."""
    
    def __init__(self):
        self._logger = logging.getLogger(__name__)
        self._location_service = None
        self._cached_result = None
        self._cache_time = None
        self._cache_duration = 300  # 5 minutes
    
    def _get_location_service(self):
        """Lazy load location service to avoid circular imports."""
        if self._location_service is None:
            try:
                from .location_service import LocationService
                self._location_service = LocationService()
            except ImportError as e:
                self._logger.warning(f"Location service not available: {e}")
                return None
        return self._location_service
    
    def is_daytime(self) -> Optional[bool]:
        """Determine if it's currently daytime. Returns None if unknown."""
        # Check cache first
        now = datetime.now()
        if (self._cached_result is not None and 
            self._cache_time is not None and
            (now - self._cache_time).total_seconds() < self._cache_duration):
            return self._cached_result
        
        location_service = self._get_location_service()
        if location_service is None:
            return None
        
        try:
            result = location_service.is_daytime_now()
            self._cached_result = result
            self._cache_time = now
            return result
        except Exception as e:
            self._logger.warning(f"Error determining daytime status: {e}")
            return None


class SimpleTimeBasedAutoThemeService:
    """Simple auto theme service based on local time only."""
    
    def __init__(self, day_start_hour: int = 6, night_start_hour: int = 18):
        self.day_start_hour = day_start_hour
        self.night_start_hour = night_start_hour
    
    def is_daytime(self) -> Optional[bool]:
        """Determine if it's daytime based on local time."""
        current_hour = datetime.now().hour
        return self.day_start_hour <= current_hour < self.night_start_hour


# ============================================================================
# Theme Applicator Implementation
# ============================================================================

class TtkBootstrapThemeApplicator:
    """Theme applicator for ttkbootstrap applications."""
    
    # Class-level flag to track if themes have been registered
    _themes_registered = False
    
    def __init__(self, app_instance=None):
        self._app = app_instance
        self._logger = logging.getLogger(__name__)
        self._ensure_custom_themes_registered()
    
    def _ensure_custom_themes_registered(self) -> None:
        """Register custom themes if they haven't been registered yet."""
        if tb is None or ThemeDefinition is None:
            self._logger.warning("ttkbootstrap not available")
            return
            
        # Check if already registered (class-level)
        if TtkBootstrapThemeApplicator._themes_registered:
            return
        
        try:
            # Import USER_THEMES from user.py
            try:
                from user import USER_THEMES
                self._logger.debug(f"Loaded user themes: {list(USER_THEMES.keys())}")
            except ImportError:
                self._logger.warning("Could not import USER_THEMES from user.py")
                USER_THEMES = {}
            
            # Get existing theme names to avoid re-registering
            existing_themes = set(tb.Style().theme_names())
            
            # Register themes from USER_THEMES (user.py)
            for theme_name, theme_data in USER_THEMES.items():
                if theme_name not in existing_themes:
                    try:
                        colors = theme_data["colors"]
                        theme_def = ThemeDefinition(
                            themename=theme_name,
                            themetype=theme_data["type"],
                            **colors
                        )
                        tb.Style.register_theme(theme_def)
                        self._logger.info(f"Registered custom theme from user.py: {theme_name}")
                    except Exception as e:
                        self._logger.error(f"Failed to register theme {theme_name}: {e}")
            
            # Also register themes from ThemeRegistry (fallback)
            for theme_name, theme_data in ThemeRegistry.CUSTOM_THEMES.items():
                if theme_name not in existing_themes and theme_name not in USER_THEMES:
                    try:
                        colors = theme_data["colors"]
                        theme_def = ThemeDefinition(
                            themename=theme_name,
                            themetype=theme_data["type"],
                            **colors
                        )
                        tb.Style.register_theme(theme_def)
                        self._logger.info(f"Registered fallback theme: {theme_name}")
                    except Exception as e:
                        self._logger.error(f"Failed to register fallback theme {theme_name}: {e}")
            
            # Mark themes as registered to avoid re-registration
            TtkBootstrapThemeApplicator._themes_registered = True
            self._logger.info("Theme registration completed")
                        
        except Exception as e:
            self._logger.error(f"Error in theme registration: {e}")
    
    def apply_theme(self, theme_name: str) -> bool:
        """Apply the specified theme. Returns True if successful."""
        if tb is None:
            self._logger.warning("ttkbootstrap not available")
            return False
        
        try:
            # Apply the theme - use safer approach (themes already registered in __init__)
            try:
                if self._app and hasattr(self._app, 'style'):
                    self._app.style.theme_use(theme_name)
                else:
                    style = tb.Style()
                    style.theme_use(theme_name)
                    
                self._logger.info(f"Successfully applied theme: {theme_name}")
                return True
                
            except Exception as widget_error:
                # Widget errors are common during theme switching - log but consider success
                error_msg = str(widget_error)
                if "invalid command name" in error_msg:
                    # This is a known ttkbootstrap issue with widget lifecycle during theme changes
                    # The theme is actually applied successfully, just some widgets complain
                    self._logger.debug(f"Widget lifecycle warning during theme application: {widget_error}")
                    self._logger.info(f"Theme applied successfully despite widget warnings: {theme_name}")
                    return True
                else:
                    # Other errors might be more serious
                    self._logger.warning(f"Theme application error: {widget_error}")
                    return False
            
        except Exception as e:
            self._logger.error(f"Failed to apply theme {theme_name}: {e}")
            return False
    
    def get_available_themes(self) -> List[str]:
        """Get list of all available themes."""
        if tb is None:
            return ThemeRegistry.get_all_themes()
        
        try:
            # Themes already registered in __init__
            return list(tb.Style().theme_names())
        except Exception as e:
            self._logger.warning(f"Error getting available themes: {e}")
            return ThemeRegistry.get_all_themes()


# ============================================================================
# Mock Implementations (for testing)
# ============================================================================

class MockThemeSettings:
    """Mock theme settings for testing."""
    
    def __init__(self, config: ThemeConfig):
        self._config = config
        self._current_theme = config.fallback_theme
        self._auto_enabled = config.auto_enabled_by_default
        self._light_theme = config.default_light_theme
        self._dark_theme = config.default_dark_theme
    
    def get_current_theme(self) -> str:
        return self._current_theme
    
    def set_current_theme(self, theme: str) -> None:
        self._current_theme = theme
    
    def is_auto_enabled(self) -> bool:
        return self._auto_enabled
    
    def set_auto_enabled(self, enabled: bool) -> None:
        self._auto_enabled = enabled
    
    def get_light_theme(self) -> str:
        return self._light_theme
    
    def set_light_theme(self, theme: str) -> None:
        self._light_theme = theme
    
    def get_dark_theme(self) -> str:
        return self._dark_theme
    
    def set_dark_theme(self, theme: str) -> None:
        self._dark_theme = theme


class MockAutoThemeService:
    """Mock auto theme service for testing."""
    
    def __init__(self, is_day: Optional[bool] = True):
        self._is_day = is_day
    
    def is_daytime(self) -> Optional[bool]:
        return self._is_day
    
    def set_daytime(self, is_day: Optional[bool]) -> None:
        """Set the daytime status for testing."""
        self._is_day = is_day


class MockThemeApplicator:
    """Mock theme applicator for testing."""
    
    def __init__(self):
        self._current_theme = "flatly"
        self._available_themes = ThemeRegistry.get_all_themes()
        self._applied_themes = []  # Track applied themes for testing
    
    def apply_theme(self, theme_name: str) -> bool:
        if theme_name in self._available_themes:
            self._current_theme = theme_name
            self._applied_themes.append(theme_name)
            return True
        return False
    
    def get_available_themes(self) -> List[str]:
        return self._available_themes
    
    def get_applied_themes(self) -> List[str]:
        """Get list of applied themes for testing."""
        return self._applied_themes.copy()