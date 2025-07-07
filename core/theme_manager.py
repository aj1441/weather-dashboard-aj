"""Theme management for the weather dashboard"""

import ttkbootstrap as tb
import logging
from typing import Dict, Optional

class ThemeManager:
    """Manages theme operations and provides theme utilities"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.style = tb.Style()
    
    def theme_exists(self, theme_name: str) -> bool:
        """Check if a theme exists"""
        return theme_name in self.style.theme_names()
    
    def get_fallback_theme(self, preferred_theme: str) -> str:
        """Get a fallback theme if preferred theme doesn't exist"""
        if self.theme_exists(preferred_theme):
            return preferred_theme
            
        # Fallback chain for custom themes
        if preferred_theme == "aj_lightly":
            fallbacks = ["pulse", "flatly", "litera", "cosmo"]
        elif preferred_theme == "aj_darkly":
            fallbacks = ["darkly", "superhero", "cyborg", "vapor"]
        else:
            fallbacks = ["darkly", "superhero", "pulse", "cosmo"]
        
        for theme in fallbacks:
            if self.theme_exists(theme):
                self.logger.warning(f"Using fallback theme: {theme} for {preferred_theme}")
                return theme
        
        # Ultimate fallback
        return self.style.theme_names()[0]
    
    def get_available_themes(self) -> Dict[str, list]:
        """Get all available themes categorized by type"""
        return {
            "light": ["aj_lightly", "pulse", "flatly", "litera", "minty", "lumen"],
            "dark": ["aj_darkly", "darkly", "cyborg", "superhero", "solar"]
        }
    
    def is_light_theme(self, theme_name: str) -> bool:
        """Check if a theme is a light theme"""
        light_themes = self.get_available_themes()["light"]
        return theme_name in light_themes
    
    def is_dark_theme(self, theme_name: str) -> bool:
        """Check if a theme is a dark theme"""
        dark_themes = self.get_available_themes()["dark"]
        return theme_name in dark_themes
    
    def get_current_theme(self) -> str:
        """Get the currently active theme"""
        return self.style.theme_use()
    
    def set_theme(self, theme_name: str) -> bool:
        """Set the application theme"""
        try:
            # Use fallback if theme doesn't exist
            theme_to_use = self.get_fallback_theme(theme_name)
            self.style.theme_use(theme_to_use)
            self.logger.info(f"Theme set to: {theme_to_use}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to set theme {theme_name}: {e}")
            return False
