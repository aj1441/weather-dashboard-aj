"""
Watermark control component for adjusting watermark settings.

This component provides a user interface for controlling watermark
appearance, position, and visibility across the application.
"""

import tkinter as tk
import ttkbootstrap as tb
from typing import Dict, Any, Callable, Optional
import logging

logger = logging.getLogger(__name__)

class WatermarkControlComponent:
    """Component for controlling watermark settings."""
    
    def __init__(self, parent: tk.Widget, watermark_manager=None):
        """
        Initialize the watermark control component.
        
        Args:
            parent: Parent widget
            watermark_manager: Watermark manager instance
        """
        self.parent = parent
        self.watermark_manager = watermark_manager
        self.settings_callback: Optional[Callable] = None
        
        # Default settings
        self.current_settings = {
            'opacity': 0.1,
            'position': 'center',
            'enabled': True
        }
        
        self.setup_component()
    
    def setup_component(self) -> tb.Frame:
        """Setup the watermark control interface."""
        control_frame = tb.LabelFrame(self.parent, text="🎨 Watermark Settings", padding=10)
        
        # Enable/Disable checkbox
        self.enabled_var = tk.BooleanVar(value=self.current_settings['enabled'])
        enabled_check = tb.Checkbutton(
            control_frame,
            text="Show Watermark",
            variable=self.enabled_var,
            command=self._on_enabled_changed,
            bootstyle="round-toggle"
        )
        enabled_check.pack(fill=tk.X, pady=(0, 10))
        
        # Opacity slider
        opacity_frame = tb.Frame(control_frame)
        opacity_frame.pack(fill=tk.X, pady=(0, 10))
        
        tb.Label(opacity_frame, text="Opacity:").pack(side=tk.LEFT)
        
        self.opacity_var = tk.DoubleVar(value=self.current_settings['opacity'])
        opacity_slider = tb.Scale(
            opacity_frame,
            from_=0.0,
            to=1.0,
            variable=self.opacity_var,
            command=self._on_opacity_changed,
            bootstyle="info"
        )
        opacity_slider.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(10, 0))
        
        # Position selector
        position_frame = tb.Frame(control_frame)
        position_frame.pack(fill=tk.X, pady=(0, 10))
        
        tb.Label(position_frame, text="Position:").pack(side=tk.LEFT)
        
        self.position_var = tk.StringVar(value=self.current_settings['position'])
        position_combo = tb.Combobox(
            position_frame,
            textvariable=self.position_var,
            values=['center', 'top-left', 'top-right', 'bottom-left', 'bottom-right'],
            state='readonly',
            bootstyle="info"
        )
        position_combo.pack(side=tk.RIGHT, padx=(10, 0))
        position_combo.bind('<<ComboboxSelected>>', self._on_position_changed)
        
        # Logo selector
        logo_frame = tb.Frame(control_frame)
        logo_frame.pack(fill=tk.X, pady=(0, 10))
        
        tb.Label(logo_frame, text="Logo:").pack(side=tk.LEFT)
        
        self.logo_var = tk.StringVar(value="art_logo.png")
        logo_combo = tb.Combobox(
            logo_frame,
            textvariable=self.logo_var,
            values=self._get_available_logos(),
            state='readonly',
            bootstyle="info"
        )
        logo_combo.pack(side=tk.RIGHT, padx=(10, 0))
        logo_combo.bind('<<ComboboxSelected>>', self._on_logo_changed)
        
        # Apply button
        apply_button = tb.Button(
            control_frame,
            text="Apply Settings",
            command=self._apply_settings,
            bootstyle="success"
        )
        apply_button.pack(fill=tk.X, pady=(10, 0))
        
        return control_frame
    
    def _get_available_logos(self) -> list:
        """Get list of available logo files."""
        try:
            if self.watermark_manager:
                return self.watermark_manager.get_available_logos()
            else:
                # Fallback to common logo names
                return ["art_logo.png", "enhanced_logo_clean.png"]
        except Exception as e:
            logger.error(f"Error getting available logos: {e}")
            return ["art_logo.png"]
    
    def _on_enabled_changed(self):
        """Handle enable/disable checkbox change."""
        self.current_settings['enabled'] = self.enabled_var.get()
        logger.debug(f"Watermark enabled: {self.current_settings['enabled']}")
    
    def _on_opacity_changed(self, value):
        """Handle opacity slider change."""
        self.current_settings['opacity'] = float(value)
        logger.debug(f"Watermark opacity: {self.current_settings['opacity']}")
    
    def _on_position_changed(self, event=None):
        """Handle position combobox change."""
        self.current_settings['position'] = self.position_var.get()
        logger.debug(f"Watermark position: {self.current_settings['position']}")
    
    def _on_logo_changed(self, event=None):
        """Handle logo combobox change."""
        self.current_settings['logo'] = self.logo_var.get()
        logger.debug(f"Watermark logo: {self.current_settings['logo']}")
    
    def _apply_settings(self):
        """Apply current settings."""
        if self.settings_callback:
            self.settings_callback(self.current_settings)
            logger.info("Watermark settings applied")
        else:
            logger.warning("No settings callback configured")
    
    def set_settings_callback(self, callback: Callable[[Dict[str, Any]], None]):
        """Set callback for when settings are applied."""
        self.settings_callback = callback
    
    def get_current_settings(self) -> Dict[str, Any]:
        """Get current watermark settings."""
        return self.current_settings.copy()
    
    def update_settings(self, new_settings: Dict[str, Any]):
        """Update the component with new settings."""
        self.current_settings.update(new_settings)
        
        # Update UI elements
        self.enabled_var.set(self.current_settings.get('enabled', True))
        self.opacity_var.set(self.current_settings.get('opacity', 0.1))
        self.position_var.set(self.current_settings.get('position', 'center'))
        self.logo_var.set(self.current_settings.get('logo', 'art_logo.png'))
        
        logger.debug("Watermark control settings updated")

def create_watermark_control(parent: tk.Widget, watermark_manager=None) -> WatermarkControlComponent:
    """
    Convenience function to create a watermark control component.
    
    Args:
        parent: Parent widget
        watermark_manager: Watermark manager instance
        
    Returns:
        WatermarkControlComponent instance
    """
    return WatermarkControlComponent(parent, watermark_manager) 