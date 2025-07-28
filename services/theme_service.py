"""
Theme service for handling theme-related operations and management.

This service encapsulates theme operations and provides a clean
interface for theme management functionality.
"""

import logging
from typing import Optional, Dict, Any

from config import Config
from core.theme_factory import create_theme_manager
from core.theme_system import ThemeManager, ThemeConfig


class ThemeService:
    """Service for theme-related operations and management."""
    
    def __init__(self, config: Config, app_instance=None):
        """Initialize the theme service with configuration."""
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.app_instance = app_instance
        self.theme_manager = create_theme_manager(app_instance)
    
    def apply_theme(self, theme_name: str) -> bool:
        """
        Apply a specific theme.
        
        Args:
            theme_name: Name of the theme to apply
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.theme_manager.apply_theme(theme_name)
            self.logger.info(f"Successfully applied theme: {theme_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error applying theme {theme_name}: {e}")
            return False
    
    def apply_auto_theme(self) -> bool:
        """
        Apply automatic theme based on time and location.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            self.theme_manager.apply_auto_theme()
            self.logger.info("Successfully applied auto theme")
            return True
            
        except Exception as e:
            self.logger.error(f"Error applying auto theme: {e}")
            return False
    
    def toggle_auto_mode(self) -> bool:
        """
        Toggle automatic theme mode on/off.
        
        Returns:
            True if auto mode is now enabled, False if disabled
        """
        try:
            current_state = self.theme_manager.is_auto_enabled()
            self.theme_manager.toggle_auto_mode()
            new_state = self.theme_manager.is_auto_enabled()
            
            self.logger.info(f"Auto mode toggled: {current_state} -> {new_state}")
            return new_state
            
        except Exception as e:
            self.logger.error(f"Error toggling auto mode: {e}")
            return False
    
    def is_auto_enabled(self) -> bool:
        """
        Check if auto theme mode is enabled.
        
        Returns:
            True if auto mode is enabled, False otherwise
        """
        return self.theme_manager.is_auto_enabled()
    
    def get_current_theme(self) -> str:
        """
        Get the currently applied theme name.
        
        Returns:
            Name of the current theme
        """
        return self.theme_manager.get_current_theme()
    
    def get_available_themes(self) -> Dict[str, Any]:
        """
        Get list of available themes.
        
        Returns:
            Dictionary of available themes
        """
        return self.theme_manager.get_available_themes()
    
    def refresh_theme(self) -> bool:
        """
        Refresh the current theme.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            self.theme_manager.refresh_theme()
            self.logger.info("Successfully refreshed theme")
            return True
            
        except Exception as e:
            self.logger.error(f"Error refreshing theme: {e}")
            return False
    
    def get_theme_settings(self) -> Dict[str, Any]:
        """
        Get current theme settings.
        
        Returns:
            Dictionary with theme settings
        """
        return self.theme_manager.get_settings()
    
    def update_theme_settings(self, settings: Dict[str, Any]) -> bool:
        """
        Update theme settings.
        
        Args:
            settings: Dictionary with new theme settings
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.theme_manager.update_settings(settings)
            self.logger.info("Successfully updated theme settings")
            return True
            
        except Exception as e:
            self.logger.error(f"Error updating theme settings: {e}")
            return False
    
    def get_theme_manager(self) -> ThemeManager:
        """
        Get the underlying theme manager instance.
        
        Returns:
            ThemeManager instance
        """
        return self.theme_manager 