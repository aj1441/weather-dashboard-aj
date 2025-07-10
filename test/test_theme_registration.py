#!/usr/bin/env python3
"""Test custom theme registration"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import ttkbootstrap as tb
from core.custom_themes import register_custom_themes
from user import USER_THEMES

def test_theme_registration():
    """Test that custom themes are properly registered"""
    print("Testing theme registration...")
    
    # Register custom themes
    print("Registering custom themes...")
    success = register_custom_themes()
    print(f"Registration result: {success}")
    
    # Check if themes are available
    style = tb.Style()
    available_themes = style.theme_names()
    print(f"Available themes: {available_themes}")
    
    # Check for our custom themes
    for theme_name in USER_THEMES.keys():
        if theme_name in available_themes:
            print(f"✅ {theme_name} is available")
        else:
            print(f"❌ {theme_name} is NOT available")
    
    # Try to create a test window with aj_lightly theme
    print("\nTesting aj_lightly theme...")
    try:
        test_window = tb.Window(themename="aj_lightly")
        test_window.title("Test aj_lightly Theme")
        test_window.geometry("300x200")
        
        # Add some test widgets
        frame = tb.Frame(test_window)
        frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        label = tb.Label(frame, text="Testing aj_lightly theme")
        label.pack(pady=5)
        
        button = tb.Button(frame, text="Test Button")
        button.pack(pady=5)
        
        entry = tb.Entry(frame)
        entry.pack(pady=5)
        entry.insert(0, "Test entry")
        
        print("✅ aj_lightly theme test window created successfully!")
        print("Theme is working properly!")
        
        # Show the window briefly
        test_window.after(2000, test_window.destroy)  # Close after 2 seconds
        test_window.mainloop()
        
    except Exception as e:
        print(f"❌ Error creating test window with aj_lightly theme: {e}")

if __name__ == "__main__":
    test_theme_registration()
