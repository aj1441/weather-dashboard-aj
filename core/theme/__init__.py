"""Theme system initialization and convenience functions."""

from .theme_system import ThemeManager, ThemeConfig, ThemeDefinition
from .theme_factory import create_theme_manager
from .theme_implementations import TtkBootstrapThemeApplicator

import logging

logger = logging.getLogger(__name__)


def register_custom_themes(theme_manager=None):
    """
    Register custom themes with ttkbootstrap.
    
    This is a convenience function that ensures custom themes are registered.
    Can be called with or without a theme manager instance.
    
    Args:
        theme_manager: Optional ThemeManager instance (for compatibility)
        
    Returns:
        bool: True if registration was successful
    """
    try:
        # Create a temporary theme applicator to handle registration
        applicator = TtkBootstrapThemeApplicator()
        # Registration happens automatically in __init__
        return True
    except Exception as e:
        logger.error(f"Failed to register custom themes: {e}")
        return False


__all__ = ['ThemeManager', 'ThemeConfig', 'ThemeDefinition', 'create_theme_manager', 'register_custom_themes']