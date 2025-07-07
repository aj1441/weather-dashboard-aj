"""Custom themes for the weather dashboard"""

import ttkbootstrap as tb
import logging

logger = logging.getLogger(__name__)

def register_custom_themes():
    """Register custom themes using ttkbootstrap style system"""
    try:
        logger.info("Custom theme registration temporarily disabled")
        # Let's get the basic toggle working first, then add custom themes
        return True
        
    except Exception as e:
        logger.error(f"Custom theme registration failed: {e}")
        return False

def is_custom_theme(theme_name):
    """Check if a theme name is one of our custom themes"""
    return theme_name in ["aj_darkly", "aj_lightly"]

def get_fallback_theme(theme_name):
    """Get fallback theme for custom themes that might not be registered"""
    if theme_name == "aj_darkly":
        return "darkly"  # Use standard dark theme as fallback
    elif theme_name == "aj_lightly":
        return "pulse"   # Use standard light theme as fallback
    return theme_name

def get_available_themes():
    """Get all available themes including custom ones"""
    # Standard light and dark themes
    standard_themes = {
        "light": ["aj_lightly", "pulse", "flatly", "litera", "minty", "lumen"],
        "dark": ["aj_darkly", "darkly", "cyborg", "superhero", "solar"]
    }
    
    return standard_themes