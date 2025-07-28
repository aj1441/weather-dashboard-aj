"""
Watermark component for displaying logos as background watermarks.

This component provides easy integration of watermarks into GUI components
with configurable settings and automatic positioning.
"""

import tkinter as tk
import ttkbootstrap as tb
from typing import Optional, Dict, Any
import logging

from utils.watermark_manager import add_watermark_to_component, create_watermark_settings, safe_add_watermark

logger = logging.getLogger(__name__)

class WatermarkComponent:
    """Component for managing watermarks in GUI elements."""
    
    def __init__(self, parent: tk.Widget, logo_name: str = "art_logo.png", 
                 settings: Optional[Dict[str, Any]] = None):
        """
        Initialize the watermark component.
        
        Args:
            parent: Parent widget to add watermark to
            logo_name: Name of the logo file
            settings: Watermark settings
        """
        self.parent = parent
        self.logo_name = logo_name
        self.settings = settings or create_watermark_settings()
        self.watermark_label = None
        
        # Add watermark to parent
        self._add_watermark()
    
    def _add_watermark(self):
        """Add watermark to the parent widget."""
        try:
            self.watermark_label = safe_add_watermark(
                self.parent, 
                self.logo_name, 
                self.settings
            )
            if self.watermark_label:
                logger.debug(f"Added watermark to {self.parent}")
            else:
                logger.warning(f"Failed to add watermark to {self.parent}")
        except Exception as e:
            logger.error(f"Error adding watermark: {e}")
            self.watermark_label = None
    
    def update_settings(self, new_settings: Dict[str, Any]):
        """Update watermark settings."""
        self.settings.update(new_settings)
        if self.watermark_label:
            # Recreate watermark with new settings
            self.watermark_label.destroy()
            self._add_watermark()
    
    def set_opacity(self, opacity: float):
        """Set watermark opacity (0.0 to 1.0)."""
        self.settings['opacity'] = max(0.0, min(1.0, opacity))
        self.update_settings(self.settings)
    
    def set_position(self, position: str):
        """Set watermark position."""
        valid_positions = ['center', 'top-left', 'top-right', 'bottom-left', 'bottom-right']
        if position in valid_positions:
            self.settings['position'] = position
            self.update_settings(self.settings)
        else:
            logger.warning(f"Invalid position: {position}. Using 'center'")
            self.settings['position'] = 'center'
            self.update_settings(self.settings)
    
    def enable(self):
        """Enable the watermark."""
        self.settings['enabled'] = True
        if not self.watermark_label:
            self._add_watermark()
    
    def disable(self):
        """Disable the watermark."""
        self.settings['enabled'] = False
        if self.watermark_label:
            self.watermark_label.destroy()
            self.watermark_label = None
    
    def is_enabled(self) -> bool:
        """Check if watermark is enabled."""
        return self.settings.get('enabled', True)

def add_watermark_to_tab(tab: tk.Widget, logo_name: str = "art_logo.png", 
                        position: str = 'center', opacity: float = 0.1) -> WatermarkComponent:
    """
    Convenience function to add watermark to a tab.
    
    Args:
        tab: The tab widget to add watermark to
        logo_name: Name of the logo file
        position: Watermark position
        opacity: Watermark opacity
        
    Returns:
        WatermarkComponent instance
    """
    settings = create_watermark_settings(
        opacity=opacity,
        position=position,
        enabled=True
    )
    
    return WatermarkComponent(tab, logo_name, settings)

def add_watermark_to_main_window(window: tk.Widget, logo_name: str = "art_logo.png") -> WatermarkComponent:
    """
    Add watermark to the main application window.
    
    Args:
        window: The main window widget
        logo_name: Name of the logo file
        
    Returns:
        WatermarkComponent instance
    """
    settings = create_watermark_settings(
        opacity=0.05,  # Very subtle for main window
        position='center',
        enabled=True
    )
    
    return WatermarkComponent(window, logo_name, settings) 