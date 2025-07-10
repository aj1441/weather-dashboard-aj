"""
Test script to verify theme_manager.py updates
"""

import tkinter as tk
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def run_test():
    """Run a simple test to verify theme_manager.py and custom_themes.py"""
    print("Testing ThemeManager functionality...")
    
    # Import after path is set up
    from core.theme_manager import ThemeManager
    
    # Create a theme manager instance
    theme_manager = ThemeManager()
    print(f"ThemeManager created successfully")
    
    # Get available themes
    available_themes = theme_manager.style.theme_names()
    print(f"Available themes: {available_themes}")
    
    # Try to register all custom themes
    from core.custom_themes import register_custom_themes
    result = register_custom_themes()
    print(f"Custom themes registration result: {result}")
    
    # Get updated available themes
    updated_themes = theme_manager.style.theme_names()
    print(f"Updated available themes: {updated_themes}")
    
    # Print success message
    print("\nTheme manager test completed successfully!")
    print("You can now run the full application to verify toggle styling.")

if __name__ == "__main__":
    run_test()
