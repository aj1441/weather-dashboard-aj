"""
Test script for ttkbootstrap toggle styles with custom themes
This script creates a window with all available toggle types for visual inspection
"""

import tkinter as tk
import ttkbootstrap as tb
from ttkbootstrap.constants import *
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.theme_manager import ThemeManager
from core.custom_themes import register_custom_themes

class ThemeToggleTest(tk.Tk):
    def __init__(self):
        super().__init__()
        
        # Initialize theme manager and register custom themes
        self.theme_manager = ThemeManager()
        register_custom_themes(self.theme_manager)
        
        # Setup window
        self.title("Toggle Style Test")
        self.geometry("500x700")
        
        # Theme selection
        self.current_theme = tk.StringVar(value="aj_darkly")
        self.setup_ui()
        self.apply_theme(self.current_theme.get())
        
    def setup_ui(self):
        """Create the UI elements"""
        main_frame = tb.Frame(self, padding=20)
        main_frame.pack(fill=BOTH, expand=YES)
        
        # Theme selector
        theme_frame = tb.LabelFrame(main_frame, text="Theme Selection", padding=10)
        theme_frame.pack(fill=X, pady=10)
        
        themes = ["aj_darkly", "aj_lightly", "darkly", "litera", "superhero", "cosmo"]
        for theme in themes:
            rb = tb.Radiobutton(
                theme_frame, 
                text=theme,
                variable=self.current_theme,
                value=theme,
                command=lambda t=theme: self.apply_theme(t)
            )
            rb.pack(anchor=W, padx=5, pady=2)
        
        # Toggle styles
        toggles_frame = tb.LabelFrame(main_frame, text="Toggle Styles", padding=10)
        toggles_frame.pack(fill=X, pady=10)
        
        # Standard TCheckbutton
        self.std_var = tk.BooleanVar(value=True)
        std_check = tb.Checkbutton(
            toggles_frame,
            text="Standard Checkbutton",
            variable=self.std_var
        )
        std_check.pack(anchor=W, padx=5, pady=5)
        
        # Toolbutton style
        self.tool_var = tk.BooleanVar(value=True)
        tool_check = tb.Checkbutton(
            toggles_frame,
            text="Toolbutton",
            variable=self.tool_var,
            bootstyle="toolbutton"
        )
        tool_check.pack(anchor=W, padx=5, pady=5)
        
        # Outline Toolbutton style
        self.outline_var = tk.BooleanVar(value=True)
        outline_check = tb.Checkbutton(
            toggles_frame,
            text="Outline Toolbutton",
            variable=self.outline_var,
            bootstyle="outline-toolbutton"
        )
        outline_check.pack(anchor=W, padx=5, pady=5)
        
        # Round Toggle style
        self.round_var = tk.BooleanVar(value=True)
        round_toggle = tb.Checkbutton(
            toggles_frame,
            text="Round Toggle",
            variable=self.round_var,
            bootstyle="round-toggle"
        )
        round_toggle.pack(anchor=W, padx=5, pady=5)
        
        # Square Toggle style
        self.square_var = tk.BooleanVar(value=True)
        square_toggle = tb.Checkbutton(
            toggles_frame,
            text="Square Toggle",
            variable=self.square_var,
            bootstyle="square-toggle"
        )
        square_toggle.pack(anchor=W, padx=5, pady=5)
        
        # Colors with toggles section
        colors_frame = tb.LabelFrame(main_frame, text="Color Variants", padding=10)
        colors_frame.pack(fill=X, pady=10)
        
        # Colored toolbuttons
        for color in ["primary", "secondary", "success", "info", "warning", "danger"]:
            var = tk.BooleanVar(value=True)
            toggle = tb.Checkbutton(
                colors_frame,
                text=f"{color.capitalize()} Toolbutton",
                variable=var,
                bootstyle=f"{color}-toolbutton"
            )
            toggle.pack(anchor=W, padx=5, pady=2)
            
        # Colored round toggles
        colors_toggle_frame = tb.LabelFrame(main_frame, text="Color Toggle Variants", padding=10)
        colors_toggle_frame.pack(fill=X, pady=10)
        
        for color in ["primary", "secondary", "success", "info", "warning", "danger"]:
            var = tk.BooleanVar(value=True)
            toggle = tb.Checkbutton(
                colors_toggle_frame,
                text=f"{color.capitalize()} Round-Toggle",
                variable=var,
                bootstyle=f"{color}-round-toggle"
            )
            toggle.pack(anchor=W, padx=5, pady=2)
    
    def apply_theme(self, theme_name):
        """Apply the selected theme"""
        # Get fallback theme if selected theme doesn't exist
        theme = self.theme_manager.get_fallback_theme(theme_name)
        self.style = tb.Style(theme=theme)
        print(f"Applied theme: {theme}")
        
if __name__ == "__main__":
    app = ThemeToggleTest()
    app.mainloop()
