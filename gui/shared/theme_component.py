"""
Refactored theme component using the new theme management system.

This component provides a clean UI for theme controls while delegating
all theme logic to the unified ThemeManager.
"""

import logging
import ttkbootstrap as tb
from ttkbootstrap.constants import PRIMARY, SUCCESS, WARNING, DANGER, INFO
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.theme.theme_system import ThemeManager

logger = logging.getLogger(__name__)


class ThemeComponent:
    """Simplified theme component using unified ThemeManager."""

    def __init__(self, parent, theme_manager: 'ThemeManager'):
        self.parent = parent
        self.theme_manager = theme_manager
        self.logger = logging.getLogger(__name__)
        
        # UI variables
        self.auto_mode_var = tb.BooleanVar(value=self.theme_manager.is_auto_enabled())
        self.theme_var = tb.BooleanVar(value=self._is_light_theme())
        
        self.setup_component()
        self.update_ui_state()
    
    def _is_light_theme(self) -> bool:
        """Check if current theme is a light theme."""
        current = self.theme_manager.current_theme
        # Use the theme registry to determine if theme is light
        from core.theme.theme_system import ThemeRegistry
        light_themes = ThemeRegistry.LIGHT_THEMES
        return current in light_themes
    
    def setup_component(self):
        """Create the theme controls."""
        self.theme_frame = tb.Frame(self.parent)

        # Auto mode toggle
        self.auto_toggle = tb.Checkbutton(
            self.theme_frame,
            text="🌅 Auto Day/Night",
            variable=self.auto_mode_var,
            command=self.toggle_auto_mode,
            bootstyle="warning-round-toggle",
        )
        self.auto_toggle.pack(side="left", padx=(0, 10))

        # Manual theme toggle (enabled only when auto mode is off)
        self.manual_toggle = tb.Checkbutton(
            self.theme_frame,
            text="☀ Light / 🌙 Dark",
            variable=self.theme_var,
            command=self.toggle_manual_theme,
            bootstyle="success-round-toggle",
        )
        self.manual_toggle.pack(side="left")

    def toggle_auto_mode(self):
        """Toggle between auto and manual theme mode."""
        auto_enabled = self.auto_mode_var.get()
        
        try:
            if auto_enabled:
                # Enable auto mode with current light/dark theme preferences
                success = self.theme_manager.enable_auto_mode()
                if success:
                    self.logger.info("Auto day/night mode enabled")
                else:
                    self.logger.error("Failed to enable auto mode")
                    self.auto_mode_var.set(False)
            else:
                # Disable auto mode
                success = self.theme_manager.disable_auto_mode()
                if success:
                    self.logger.info("Auto day/night mode disabled - using manual theme")
                else:
                    self.logger.error("Failed to disable auto mode")
                    self.auto_mode_var.set(True)
                    
        except (ValueError, AttributeError) as e:
            self.logger.error(f"Invalid theme configuration: {e}")
            # Revert the UI state
            self.auto_mode_var.set(not auto_enabled)
        except Exception as e:
            self.logger.error(f"Unexpected error toggling auto mode: {e}")
            # Revert the UI state
            self.auto_mode_var.set(not auto_enabled)
        
        # Update UI state and theme variable
        self.update_ui_state()
        self.theme_var.set(self._is_light_theme())

    def toggle_manual_theme(self):
        """Toggle between light and dark themes in manual mode."""
        if self.theme_manager.is_auto_enabled():
            self.logger.info("Auto mode is enabled - manual toggle ignored")
            return
        
        is_light = self.theme_var.get()
        
        try:
            # Determine target theme based on toggle
            if is_light:
                # User wants light theme - use the saved light theme preference
                target_theme = self.theme_manager._settings.get_light_theme()
            else:
                # User wants dark theme - use the saved dark theme preference  
                target_theme = self.theme_manager._settings.get_dark_theme()
            
            success = self.theme_manager.set_manual_theme(target_theme)
            if success:
                self.logger.info(f"Manual theme changed to: {target_theme}")
            else:
                self.logger.error(f"Failed to apply manual theme: {target_theme}")
                # Revert the UI state
                self.theme_var.set(not is_light)
                
        except (ValueError, AttributeError) as e:
            self.logger.error(f"Invalid theme configuration: {e}")
            # Revert the UI state
            self.theme_var.set(not is_light)
        except Exception as e:
            self.logger.error(f"Unexpected error changing manual theme: {e}")
            # Revert the UI state
            self.theme_var.set(not is_light)

    def update_ui_state(self):
        """Update the UI state based on current theme manager settings."""
        auto_enabled = self.theme_manager.is_auto_enabled()
        
        # Update auto mode checkbox
        self.auto_mode_var.set(auto_enabled)
        
        # Enable/disable manual toggle based on auto mode
        if auto_enabled:
            self.manual_toggle.configure(state="disabled")
        else:
            self.manual_toggle.configure(state="normal")
    
    def refresh_theme(self):
        """Refresh the current theme (useful for external updates)."""
        try:
            success = self.theme_manager.apply_current_theme()
            if success:
                # Update UI to reflect current theme
                self.theme_var.set(self._is_light_theme())
                self.update_ui_state()
                self.logger.debug("Theme refreshed successfully")
            else:
                self.logger.warning("Failed to refresh theme")
        except Exception as e:
            self.logger.error(f"Error refreshing theme: {e}")
    
    def get_current_theme(self) -> str:
        """Get the current theme name."""
        return self.theme_manager.current_theme
    
    def get_available_themes(self) -> list:
        """Get list of available themes."""
        return self.theme_manager.get_available_themes()


# Backward compatibility - if old code tries to import the old way
def apply_auto_theme():
    """Deprecated - kept for backward compatibility."""
    logger.warning("apply_auto_theme() is deprecated - use ThemeManager.apply_current_theme()")