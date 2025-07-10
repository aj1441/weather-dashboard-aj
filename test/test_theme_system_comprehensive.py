"""
Comprehensive script to test all theme-related functionality
"""
import tkinter as tk
import ttkbootstrap as tb
from ttkbootstrap.constants import *
import sys
import os
import logging
import importlib

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def load_module(module_path):
    """Load a module and return it"""
    try:
        module = importlib.import_module(module_path)
        logger.info(f"Successfully loaded module: {module_path}")
        return module
    except Exception as e:
        logger.error(f"Failed to load module {module_path}: {e}")
        return None

def test_theme_manager():
    """Test the theme manager functionality"""
    logger.info("Testing ThemeManager...")
    
    # Import theme manager
    from core.theme_manager import ThemeManager
    
    # Create instance
    theme_manager = ThemeManager()
    logger.info(f"Available themes: {theme_manager.style.theme_names()}")
    
    # Test custom theme registration
    from core.custom_themes import register_custom_themes
    result = register_custom_themes()
    logger.info(f"Custom themes registration result: {result}")
    
    # Check updated themes
    logger.info(f"Updated themes: {theme_manager.style.theme_names()}")
    
    return theme_manager

class ThemeTestUI(tk.Tk):
    """Test UI for theme components"""
    
    def __init__(self, theme_manager):
        super().__init__()
        self.theme_manager = theme_manager
        
        # Set up window
        self.title("Theme System Test")
        self.geometry("600x800")
        
        # Apply a theme
        self.style = tb.Style(theme="aj_darkly")
        
        # Set up UI
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the UI components"""
        # Main container
        main_frame = tb.Frame(self, padding=20)
        main_frame.pack(fill=BOTH, expand=YES)
        
        # Theme selection
        theme_frame = tb.LabelFrame(main_frame, text="Theme Selection", padding=10)
        theme_frame.pack(fill=X, pady=10)
        
        # Theme selector
        themes = ["aj_darkly", "aj_lightly", "darkly", "litera", "superhero", "cosmo"]
        self.current_theme = tk.StringVar(value="aj_darkly")
        
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
        
        # Create different toggle styles
        toggle_styles = [
            ("Standard Checkbutton", ""),
            ("Toolbutton Style", "toolbutton"),
            ("Outline Toolbutton", "outline-toolbutton"),
            ("Round Toggle", "round-toggle"),
            ("Square Toggle", "square-toggle")
        ]
        
        for label, style in toggle_styles:
            var = tk.BooleanVar(value=True)
            toggle = tb.Checkbutton(
                toggles_frame,
                text=label,
                variable=var,
                bootstyle=style
            )
            toggle.pack(anchor=W, padx=5, pady=5)
        
        # Colored toggles
        colors_frame = tb.LabelFrame(main_frame, text="Colored Toggles", padding=10)
        colors_frame.pack(fill=X, pady=10)
        
        # Create colored toggle variants
        colors = ["primary", "secondary", "success", "info", "warning", "danger"]
        
        for color in colors:
            var = tk.BooleanVar(value=True)
            toggle = tb.Checkbutton(
                colors_frame,
                text=f"{color.capitalize()} Round-Toggle",
                variable=var,
                bootstyle=f"{color}-round-toggle"
            )
            toggle.pack(anchor=W, padx=5, pady=2)
        
        # Theme Component Test
        try:
            component_frame = tb.LabelFrame(main_frame, text="Theme Component Test", padding=10)
            component_frame.pack(fill=X, pady=10)
            
            from gui.components.theme_component import ThemeComponent
            theme_comp = ThemeComponent(component_frame)
            logger.info("Successfully created ThemeComponent")
        except Exception as e:
            logger.error(f"Failed to create ThemeComponent: {e}")
    
    def apply_theme(self, theme_name):
        """Apply the selected theme"""
        # Get fallback theme if selected theme doesn't exist
        theme = self.theme_manager.get_fallback_theme(theme_name)
        self.style = tb.Style(theme=theme)
        logger.info(f"Applied theme: {theme}")

def main():
    """Main test function"""
    logger.info("Starting theme system tests...")
    
    # Test theme manager
    theme_manager = test_theme_manager()
    
    # Create and run test UI
    app = ThemeTestUI(theme_manager)
    app.mainloop()

if __name__ == "__main__":
    main()
