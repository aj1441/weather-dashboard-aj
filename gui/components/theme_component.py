"""Theme toggle component for the weather dashboard"""

import ttkbootstrap as tb
from core.utils import save_user_theme

class ThemeComponent:
    """Handles theme switching functionality"""
    
    def __init__(self, parent, current_theme="vapor"):
        self.parent = parent
        self.current_theme = current_theme
        self.theme_var = tb.BooleanVar(value=(current_theme == "pulse"))
        self.setup_component()
    
    def setup_component(self):
        """Create the theme toggle widget"""
        self.toggle = tb.Checkbutton(
            self.parent,
            text="☀ Light / 🌙 Dark",
            variable=self.theme_var,
            command=self.toggle_theme,
            bootstyle="info-round-toggle"
        )
        return self.toggle
    
    def toggle_theme(self):
        """Toggle between light and dark themes and save"""
        if self.theme_var.get():
            self.parent.style.theme_use("pulse")
            self.current_theme = "pulse"
        else:
            self.parent.style.theme_use("vapor")
            self.current_theme = "vapor"
        
        save_user_theme(self.current_theme)
        
        # Callback for parent to know theme changed
        if hasattr(self, 'on_theme_change'):
            self.on_theme_change(self.current_theme)
    
    def get_current_theme(self):
        """Get the current theme name"""
        return self.current_theme
