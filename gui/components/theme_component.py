"""Theme toggle component for the weat        # Auto mode toggle
        self.auto_toggle = tb.Checkbutton(
            self.theme_frame,
            text="🌅 Auto Day/Night",
            variable=self.auto_mode_var,
            command=self.toggle_auto_mode,
            bootstyle="warning-round-toggle"
        )
        self.auto_toggle.pack(side="left", padx=(0, 10))
        
        # Manual theme toggle (enabled only when auto mode is off)
        self.manual_toggle = tb.Checkbutton(
            self.theme_frame,
            text="☀ Light / 🌙 Dark",
            variable=self.theme_var,
            command=self.toggle_theme,
            bootstyle="info-round-toggle"
        ) auto day/night mode"""

import ttkbootstrap as tb
import logging
from core.utils import save_user_theme, save_auto_theme_settings, load_auto_theme_settings, get_auto_theme, UserSettingsManager
from core.custom_themes import register_custom_themes
from core.location_service import LocationService

logger = logging.getLogger(__name__)

class ThemeComponent:
    """Handles theme switching functionality with auto day/night mode"""
    
    def __init__(self, parent, current_theme="aj_darkly"):
        self.parent = parent
        self.current_theme = current_theme
        self.location_service = LocationService()
        
        # Register custom themes first
        register_custom_themes()
        
        # Load auto theme settings
        self.auto_mode, self.light_theme, self.dark_theme = load_auto_theme_settings()
        
        # Set up variables for UI controls
        self.auto_mode_var = tb.BooleanVar(value=self.auto_mode)
        
        # Set the toggle state: True for light themes, False for dark themes
        self.is_light_theme = current_theme in ["aj_lightly", "pulse", "flatly", "litera", "minty", "lumen"]
        self.theme_var = tb.BooleanVar(value=self.is_light_theme)
        
        self.setup_component()
    
    def setup_component(self):
        """Create the theme controls"""
        # Create a frame to hold all theme controls
        self.theme_frame = tb.Frame(self.parent)
        
        # Auto mode toggle
        self.auto_toggle = tb.Checkbutton(
            self.theme_frame,
            text="🌅 Auto Day/Night",
            variable=self.auto_mode_var,
            command=self.toggle_auto_mode,
            bootstyle="warning-round-toggle"
        )
        self.auto_toggle.pack(side="left", padx=(0, 10))
        
        # Manual theme toggle (enabled only when auto mode is off)
        self.manual_toggle = tb.Checkbutton(
            self.theme_frame,
            text="☀ Light / 🌙 Dark",
            variable=self.theme_var,
            command=self.toggle_theme,
            bootstyle="info-round-toggle"
        )
        self.manual_toggle.pack(side="left")
        
        # Update UI state
        self.update_ui_state()
        
        # If auto mode is enabled, apply the appropriate theme immediately
        if self.auto_mode:
            self.apply_auto_theme()
        
        return self.theme_frame
    
    def toggle_auto_mode(self):
        """Toggle auto day/night mode on/off"""
        self.auto_mode = self.auto_mode_var.get()
        
        # Save the setting
        save_auto_theme_settings(self.auto_mode, self.light_theme, self.dark_theme)
        
        # Update UI state
        self.update_ui_state()
        
        if self.auto_mode:
            # Apply auto theme immediately
            self.apply_auto_theme()
            # Notify parent to start auto refresh
            if hasattr(self.parent, 'start_auto_theme_refresh'):
                self.parent.start_auto_theme_refresh()
            logger.info("Auto day/night mode enabled")
        else:
            # Notify parent to stop auto refresh
            if hasattr(self.parent, 'stop_auto_theme_refresh'):
                self.parent.stop_auto_theme_refresh()
            logger.info("Auto day/night mode disabled - using manual theme selection")
    
    def update_ui_state(self):
        """Update UI controls based on auto mode state"""
        if self.auto_mode:
            # Disable manual toggle when auto mode is on
            self.manual_toggle.configure(state="disabled")
        else:
            # Enable manual toggle when auto mode is off
            self.manual_toggle.configure(state="normal")
    
    def apply_auto_theme(self, latitude=None, longitude=None):
        """Apply theme based on current time and location"""
        try:
            # Use specific coordinates if provided, otherwise use user's IP location
            if latitude is not None and longitude is not None:
                from core.auto_theme import get_auto_theme as get_auto_theme_coords
                auto_theme = get_auto_theme_coords(latitude, longitude)
                logger.info(f"Using specific location for auto theme: {latitude}, {longitude}")
            else:
                auto_theme = get_auto_theme()
                logger.info("Using IP location for auto theme")
            
            if auto_theme != self.current_theme:
                self.current_theme = auto_theme
                self.apply_theme(auto_theme)
                
                # Update the manual toggle to reflect the auto-selected theme
                self.is_light_theme = auto_theme in ["aj_lightly", "pulse", "flatly", "litera", "minty", "lumen"]
                self.theme_var.set(self.is_light_theme)
                
                logger.info(f"Auto theme applied: {auto_theme}")
        except Exception as e:
            logger.error(f"Failed to apply auto theme: {e}")
    
    def toggle_theme(self):
        """Toggle between light and dark themes (manual mode only)"""
        if self.auto_mode:
            # Don't allow manual changes in auto mode
            return
        
        if self.theme_var.get():
            # Switch to light theme
            new_theme = self.light_theme
        else:
            # Switch to dark theme
            new_theme = self.dark_theme
        
        self.current_theme = new_theme
        self.apply_theme(new_theme)
        save_user_theme(new_theme)
        
        logger.info(f"Manual theme changed to: {new_theme}")
    
    def apply_theme(self, theme_name: str):
        """Apply a specific theme"""
        try:
            # Get the application's style instance
            import ttkbootstrap as tb
            style = tb.Style()
            style.theme_use(theme_name)
            logger.debug(f"Applied theme: {theme_name}")
        except Exception as e:
            logger.error(f"Failed to apply theme {theme_name}: {e}")
            # Fallback to standard themes
            fallback_theme = "pulse" if theme_name in ["pulse", "flatly", "litera", "minty", "lumen"] else "darkly"
            try:
                import ttkbootstrap as tb
                style = tb.Style()
                style.theme_use(fallback_theme)
                self.current_theme = fallback_theme
                logger.info(f"Fell back to theme: {fallback_theme}")
            except Exception as e2:
                logger.error(f"Even fallback theme failed: {e2}")
        
        # Callback for parent to know theme changed
        if hasattr(self, 'on_theme_change'):
            self.on_theme_change(self.current_theme)
    
    def refresh_auto_theme(self, latitude=None, longitude=None):
        """Refresh auto theme (useful for periodic updates and location changes)"""
        if self.auto_mode:
            self.apply_auto_theme(latitude, longitude)
    
    def get_current_theme(self):
        """Get the current theme name"""
        return self.current_theme
    
    def set_manual_theme(self, theme_name: str):
        """Manually set a theme (disables auto mode)"""
        self.auto_mode = False
        self.auto_mode_var.set(False)
        save_auto_theme_settings(self.auto_mode, self.light_theme, self.dark_theme)
        
        self.current_theme = theme_name
        self.apply_theme(theme_name)
        save_user_theme(theme_name)
        
        # Update UI state
        self.update_ui_state()
        self.is_light_theme = theme_name in ["pulse", "flatly", "litera", "minty", "lumen"]
        self.theme_var.set(self.is_light_theme)
        
        logger.info(f"Manual theme set to: {theme_name} (auto mode disabled)")
    
    def get_available_themes(self):
        """Get list of available themes"""
        return {
            "light": ["pulse", "flatly", "litera", "minty", "lumen"],
            "dark": ["aj_darkly", "darkly", "cyborg", "vapor", "solar"]
        }
    
    def is_auto_mode_enabled(self):
        """Check if auto mode is currently enabled"""
        return self.auto_mode
    
    def _switch_theme(self, theme_name):
        """Switch to the specified theme"""
        self.logger.info(f"Switching to theme: {theme_name}")
        self.app.style.theme_use(theme_name)
        if hasattr(self.parent, "sync_customtkinter_theme"):
            self.parent.sync_customtkinter_theme(theme_name)
        self.current_theme = theme_name
        UserSettingsManager.save_user_theme(theme_name)
