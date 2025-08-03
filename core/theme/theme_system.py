"""
Best-practice theme management system for the Weather Dashboard.

This module provides a clean, testable, and maintainable theme management
architecture following Python best practices including:
- Single Responsibility Principle
- Dependency Injection
- Protocol-based interfaces
- Immutable configuration
- Composition over inheritance
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Protocol, Optional, Dict, List, Any
from abc import ABC, abstractmethod
import logging

logger = logging.getLogger(__name__)


# ============================================================================
# Configuration
# ============================================================================

@dataclass(frozen=True)
class ThemeConfig:
    """Immutable theme system configuration."""
    default_light_theme: str = "aj_lightly"
    default_dark_theme: str = "aj_darkly"
    auto_enabled_by_default: bool = True
    fallback_theme: str = "flatly"
    settings_file: str = "data/user_settings.json"


@dataclass(frozen=True)
class ThemeDefinition:
    """Immutable theme definition."""
    name: str
    category: str  # 'light' or 'dark'
    is_custom: bool = False
    fallbacks: List[str] = field(default_factory=list)


# ============================================================================
# Protocols (Interfaces)
# ============================================================================

class ThemeSettingsProtocol(Protocol):
    """Interface for theme settings persistence."""
    
    def get_current_theme(self) -> str:
        """Get the currently selected theme."""
        ...
    
    def set_current_theme(self, theme: str) -> None:
        """Set the current theme."""
        ...
    
    def is_auto_enabled(self) -> bool:
        """Check if auto theme mode is enabled."""
        ...
    
    def set_auto_enabled(self, enabled: bool) -> None:
        """Enable or disable auto theme mode."""
        ...
    
    def get_light_theme(self) -> str:
        """Get the light theme for auto mode."""
        ...
    
    def set_light_theme(self, theme: str) -> None:
        """Set the light theme for auto mode."""
        ...
    
    def get_dark_theme(self) -> str:
        """Get the dark theme for auto mode."""
        ...
    
    def set_dark_theme(self, theme: str) -> None:
        """Set the dark theme for auto mode."""
        ...


class AutoThemeServiceProtocol(Protocol):
    """Interface for automatic theme determination."""
    
    def is_daytime(self) -> Optional[bool]:
        """Determine if it's currently daytime. Returns None if unknown."""
        ...


class ThemeApplicatorProtocol(Protocol):
    """Interface for applying themes to UI components."""
    
    def apply_theme(self, theme_name: str) -> bool:
        """Apply the specified theme. Returns True if successful."""
        ...
    
    def get_available_themes(self) -> List[str]:
        """Get list of all available themes."""
        ...


# ============================================================================
# Core Classes
# ============================================================================

class ThemeRegistry:
    """Central registry for all theme definitions."""
    
    # Built-in themes by category
    LIGHT_THEMES = [
        "aj_lightly", "pulse", "flatly", "litera", "minty", "lumen", 
        "sandstone", "yeti", "united", "morph", "journal", "cosmo",
        "simplex", "cerculean"
    ]
    
    DARK_THEMES = [
        "aj_darkly", "darkly", "superhero", "solar", "cyborg", "vapor"
    ]
    
    # Custom theme definitions - loaded from user.py if available
    CUSTOM_THEMES = {}
    
    @classmethod
    def _load_user_themes(cls):
        """Load custom themes from user.py"""
        if cls.CUSTOM_THEMES:  # Already loaded
            return
            
        try:
            from core.theme.user_themes import USER_THEMES
            cls.CUSTOM_THEMES.update(USER_THEMES)
            logger.info(f"Loaded custom themes from user.py: {list(USER_THEMES.keys())}")
        except ImportError:
            logger.warning("Could not import USER_THEMES from user.py - using fallback themes")
            # Fallback theme definitions
            cls.CUSTOM_THEMES = {
                "aj_darkly": {
                    "type": "dark",
                    "colors": {
                        "primary": "#007bff",
                        "secondary": "#6c757d", 
                        "success": "#28a745",
                        "info": "#17a2b8",
                        "warning": "#ffc107",
                        "danger": "#dc3545",
                        "light": "#f8f9fa",
                        "dark": "#343a40",
                        "bg": "#212529",
                        "fg": "#fff",
                        "selectbg": "#007bff",
                        "selectfg": "#fff",
                        "border": "#495057",
                        "inputfg": "#fff",
                        "inputbg": "#495057",
                        "active": "#007bff"
                    }
                },
                "aj_lightly": {
                    "type": "light",
                    "colors": {
                        "primary": "#007bff",
                        "secondary": "#6c757d",
                        "success": "#28a745", 
                        "info": "#17a2b8",
                        "warning": "#ffc107",
                        "danger": "#dc3545",
                        "light": "#f8f9fa",
                        "dark": "#343a40",
                        "bg": "#fff",
                        "fg": "#212529",
                        "selectbg": "#007bff",
                        "selectfg": "#fff",
                        "border": "#dee2e6",
                        "inputfg": "#495057",
                        "inputbg": "#fff",
                        "active": "#007bff"
                    }
                }
            }
    
    # Fallback chains for themes
    FALLBACK_CHAINS = {
        "aj_lightly": ["pulse", "flatly", "litera"],
        "aj_darkly": ["darkly", "superhero", "cyborg"],
        "pulse": ["flatly", "litera", "minty"],
        "darkly": ["superhero", "cyborg", "vapor"]
    }
    
    @classmethod
    def get_theme_definition(cls, theme_name: str) -> Optional[ThemeDefinition]:
        """Get theme definition by name."""
        # Ensure user themes are loaded
        cls._load_user_themes()
        
        if theme_name in cls.LIGHT_THEMES:
            category = "light"
        elif theme_name in cls.DARK_THEMES:
            category = "dark"
        else:
            return None
            
        is_custom = theme_name in cls.CUSTOM_THEMES
        fallbacks = cls.FALLBACK_CHAINS.get(theme_name, [])
        
        return ThemeDefinition(
            name=theme_name,
            category=category,
            is_custom=is_custom,
            fallbacks=fallbacks
        )
    
    @classmethod
    def get_all_themes(cls) -> List[str]:
        """Get all available theme names."""
        cls._load_user_themes()
        return cls.LIGHT_THEMES + cls.DARK_THEMES
    
    @classmethod
    def get_fallback_chain(cls, theme_name: str) -> List[str]:
        """Get fallback chain for a theme."""
        cls._load_user_themes()
        return cls.FALLBACK_CHAINS.get(theme_name, [])
    
    @classmethod
    def is_valid_theme(cls, theme_name: str) -> bool:
        """Check if theme name is valid."""
        cls._load_user_themes()
        return theme_name in cls.get_all_themes()


class ThemeManager:
    """
    Main theme manager with dependency injection.
    
    This class coordinates between different theme services without
    being tightly coupled to their implementations.
    """
    
    def __init__(self,
                 config: ThemeConfig,
                 settings: ThemeSettingsProtocol,
                 auto_service: AutoThemeServiceProtocol,
                 applicator: ThemeApplicatorProtocol):
        self._config = config
        self._settings = settings
        self._auto_service = auto_service
        self._applicator = applicator
        self._logger = logging.getLogger(__name__)
    
    @property
    def current_theme(self) -> str:
        """Get the currently active theme."""
        if self._settings.is_auto_enabled():
            return self._get_auto_theme()
        return self._settings.get_current_theme()
    
    def apply_current_theme(self) -> bool:
        """Apply the current theme based on settings."""
        theme = self.current_theme
        success = self._applicator.apply_theme(theme)
        
        if success:
            self._logger.info(f"Applied theme: {theme}")
        else:
            # Try fallback
            fallback = self._get_fallback_theme(theme)
            if fallback != theme:
                success = self._applicator.apply_theme(fallback)
                if success:
                    self._logger.info(f"Applied fallback theme: {fallback}")
                    
        return success
    
    def set_manual_theme(self, theme_name: str) -> bool:
        """Set a manual theme and disable auto mode."""
        if not ThemeRegistry.is_valid_theme(theme_name):
            self._logger.warning(f"Invalid theme: {theme_name}")
            return False
            
        self._settings.set_auto_enabled(False)
        self._settings.set_current_theme(theme_name)
        return self.apply_current_theme()
    
    def enable_auto_mode(self, light_theme: Optional[str] = None, 
                        dark_theme: Optional[str] = None) -> bool:
        """Enable auto theme mode with optional custom light/dark themes."""
        if light_theme and not ThemeRegistry.is_valid_theme(light_theme):
            self._logger.warning(f"Invalid light theme: {light_theme}")
            return False
            
        if dark_theme and not ThemeRegistry.is_valid_theme(dark_theme):
            self._logger.warning(f"Invalid dark theme: {dark_theme}")
            return False
        
        # Set themes if provided
        if light_theme:
            self._settings.set_light_theme(light_theme)
        if dark_theme:
            self._settings.set_dark_theme(dark_theme)
            
        self._settings.set_auto_enabled(True)
        return self.apply_current_theme()
    
    def disable_auto_mode(self) -> bool:
        """Disable auto mode and use current manual theme."""
        self._settings.set_auto_enabled(False)
        return self.apply_current_theme()
    
    def is_auto_enabled(self) -> bool:
        """Check if auto theme mode is enabled."""
        return self._settings.is_auto_enabled()
    
    def get_available_themes(self) -> List[str]:
        """Get all available themes."""
        return self._applicator.get_available_themes()
    
    def _get_auto_theme(self) -> str:
        """Determine appropriate theme for auto mode."""
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
    
    def _get_fallback_theme(self, theme_name: str) -> str:
        """Get a fallback theme if the requested one isn't available."""
        available = self._applicator.get_available_themes()
        
        if theme_name in available:
            return theme_name
            
        # Try fallback chain
        for fallback in ThemeRegistry.get_fallback_chain(theme_name):
            if fallback in available:
                self._logger.info(f"Using fallback theme {fallback} for {theme_name}")
                return fallback
                
        # Last resort
        if self._config.fallback_theme in available:
            self._logger.warning(f"Using last resort fallback: {self._config.fallback_theme}")
            return self._config.fallback_theme
            
        # Return first available theme
        if available:
            self._logger.warning(f"Using first available theme: {available[0]}")
            return available[0]
            
        # This should never happen
        self._logger.error("No themes available!")
        return "flatly"