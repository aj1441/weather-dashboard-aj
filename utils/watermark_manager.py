"""
Watermark manager for displaying logos as background watermarks.

This module provides a flexible system for adding watermarks to GUI components
with configurable transparency, positioning, and styling options.
"""

import tkinter as tk
from tkinter import PhotoImage
import os
from typing import Optional, Tuple, Dict, Any
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class WatermarkManager:
    """Manages watermark display across the application."""
    
    def __init__(self, assets_path: str = "assets/images"):
        """
        Initialize the watermark manager.
        
        Args:
            assets_path: Path to the assets directory containing logo files
        """
        self.assets_path = Path(assets_path)
        self.logo_cache: Dict[str, PhotoImage] = {}
        self.watermark_widgets: Dict[str, tk.Widget] = {}
        
        # Default watermark settings
        self.default_settings = {
            'opacity': 0.1,  # 10% opacity
            'position': 'center',  # center, top-left, top-right, bottom-left, bottom-right
            'size': (200, 200),  # (width, height) in pixels
            'enabled': True
        }
        
        logger.info(f"WatermarkManager initialized with assets path: {self.assets_path}")
    
    def load_logo(self, logo_name: str) -> Optional[PhotoImage]:
        """
        Load a logo image from the assets directory.
        
        Args:
            logo_name: Name of the logo file (e.g., 'art_logo.png')
            
        Returns:
            PhotoImage object or None if loading fails
        """
        if logo_name in self.logo_cache:
            return self.logo_cache[logo_name]
        
        logo_path = self.assets_path / logo_name
        if not logo_path.exists():
            logger.warning(f"Logo file not found: {logo_path}")
            return None
        
        try:
            # Load the image
            image = PhotoImage(file=str(logo_path))
            self.logo_cache[logo_name] = image
            logger.debug(f"Loaded logo: {logo_name} ({image.width()}x{image.height()})")
            return image
        except Exception as e:
            logger.error(f"Failed to load logo {logo_name}: {e}")
            return None
    
    def create_watermark_label(self, parent: tk.Widget, logo_name: str = "art_logo.png", 
                              settings: Optional[Dict[str, Any]] = None) -> Optional[tk.Label]:
        """
        Create a watermark label with the specified logo.
        
        Args:
            parent: Parent widget to place the watermark
            logo_name: Name of the logo file
            settings: Watermark settings (opacity, position, size, enabled)
            
        Returns:
            Label widget with watermark or None if creation fails
        """
        try:
            if settings is None:
                settings = self.default_settings.copy()
            
            if not settings.get('enabled', True):
                return None
            
            # Load the logo
            logo_image = self.load_logo(logo_name)
            if logo_image is None:
                logger.warning(f"Failed to load logo: {logo_name}")
                return None
            
            # Create a transparent label with error handling
            watermark_label = tk.Label(parent, image=logo_image)
            watermark_label.image = logo_image  # Keep a reference
            
            # Configure transparency and positioning
            self._configure_watermark_appearance(watermark_label, settings)
            
            # Position the watermark
            self._position_watermark(watermark_label, parent, settings.get('position', 'center'))
            
            logger.debug(f"Created watermark with logo: {logo_name}")
            return watermark_label
            
        except Exception as e:
            logger.error(f"Error creating watermark: {e}")
            return None
    
    def _configure_watermark_appearance(self, label: tk.Label, settings: Dict[str, Any]):
        """Configure the appearance of the watermark label."""
        opacity = settings.get('opacity', 0.1)
        
        # Set transparency by configuring the label
        label.configure(
            bg='systemTransparent',  # Transparent background
            fg='systemTransparent'   # Transparent foreground
        )
        
        # Note: Tkinter doesn't support true alpha transparency directly
        # The opacity effect is achieved through the image itself
        # For better transparency, you'd need to modify the image
    
    def _position_watermark(self, watermark: tk.Label, parent: tk.Widget, position: str):
        """Position the watermark within the parent widget."""
        watermark.place(relx=0.5, rely=0.5, anchor='center')  # Default center
        
        if position == 'top-left':
            watermark.place(relx=0.05, rely=0.05, anchor='nw')
        elif position == 'top-right':
            watermark.place(relx=0.95, rely=0.05, anchor='ne')
        elif position == 'bottom-left':
            watermark.place(relx=0.05, rely=0.95, anchor='sw')
        elif position == 'bottom-right':
            watermark.place(relx=0.95, rely=0.95, anchor='se')
        elif position == 'center':
            watermark.place(relx=0.5, rely=0.5, anchor='center')
        else:
            # Custom positioning
            watermark.place(relx=0.5, rely=0.5, anchor='center')
    
    def add_watermark_to_frame(self, frame: tk.Frame, logo_name: str = "art_logo.png",
                               settings: Optional[Dict[str, Any]] = None) -> Optional[tk.Label]:
        """
        Add a watermark to a frame widget.
        
        Args:
            frame: The frame to add the watermark to
            logo_name: Name of the logo file
            settings: Watermark settings
            
        Returns:
            The watermark label widget
        """
        watermark = self.create_watermark_label(frame, logo_name, settings)
        if watermark:
            # Lower the watermark so it appears behind other widgets
            watermark.lower()
            self.watermark_widgets[id(frame)] = watermark
        
        return watermark
    
    def remove_watermark(self, frame: tk.Widget):
        """Remove watermark from a frame."""
        frame_id = id(frame)
        if frame_id in self.watermark_widgets:
            watermark = self.watermark_widgets[frame_id]
            watermark.destroy()
            del self.watermark_widgets[frame_id]
            logger.debug(f"Removed watermark from frame {frame_id}")
    
    def update_watermark_settings(self, frame: tk.Widget, new_settings: Dict[str, Any]):
        """Update watermark settings for a specific frame."""
        frame_id = id(frame)
        if frame_id in self.watermark_widgets:
            watermark = self.watermark_widgets[frame_id]
            self._configure_watermark_appearance(watermark, new_settings)
            self._position_watermark(watermark, frame, new_settings.get('position', 'center'))
            logger.debug(f"Updated watermark settings for frame {frame_id}")
    
    def get_available_logos(self) -> list:
        """Get list of available logo files."""
        logos = []
        if self.assets_path.exists():
            for file in self.assets_path.glob("*.png"):
                logos.append(file.name)
        return logos

# Global watermark manager instance
watermark_manager = WatermarkManager()

def add_watermark_to_component(component: tk.Widget, logo_name: str = "art_logo.png",
                              settings: Optional[Dict[str, Any]] = None) -> Optional[tk.Label]:
    """
    Convenience function to add watermark to any component.
    
    Args:
        component: The widget to add watermark to
        logo_name: Name of the logo file
        settings: Watermark settings
        
    Returns:
        The watermark label widget or None if failed
    """
    try:
        return watermark_manager.add_watermark_to_frame(component, logo_name, settings)
    except Exception as e:
        logger.error(f"Failed to add watermark to component: {e}")
        return None

def create_watermark_settings(opacity: float = 0.1, position: str = 'center',
                            size: Tuple[int, int] = (200, 200), enabled: bool = True) -> Dict[str, Any]:
    """
    Create watermark settings dictionary.
    
    Args:
        opacity: Transparency level (0.0 to 1.0)
        position: Position ('center', 'top-left', 'top-right', 'bottom-left', 'bottom-right')
        size: Size as (width, height) tuple
        enabled: Whether watermark is enabled
        
    Returns:
        Settings dictionary
    """
    return {
        'opacity': opacity,
        'position': position,
        'size': size,
        'enabled': enabled
    }

# Simple fallback class for when watermark system fails
class WatermarkFallback:
    """Fallback class when watermark system is not available."""
    
    def __init__(self, parent=None, logo_name=None, settings=None):
        self.parent = parent
        self.logo_name = logo_name
        self.settings = settings or {}
    
    def update_settings(self, new_settings):
        """Update settings (no-op for fallback)."""
        pass
    
    def enable(self):
        """Enable watermark (no-op for fallback)."""
        pass
    
    def disable(self):
        """Disable watermark (no-op for fallback)."""
        pass

def safe_add_watermark(component: tk.Widget, logo_name: str = "art_logo.png",
                      settings: Optional[Dict[str, Any]] = None):
    """
    Safely add watermark with fallback.
    
    Args:
        component: The widget to add watermark to
        logo_name: Name of the logo file
        settings: Watermark settings
        
    Returns:
        Watermark component or fallback
    """
    try:
        return add_watermark_to_component(component, logo_name, settings)
    except Exception as e:
        logger.warning(f"Watermark system failed, using fallback: {e}")
        return WatermarkFallback(component, logo_name, settings) 