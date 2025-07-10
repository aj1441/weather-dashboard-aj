#!/usr/bin/env python3
"""Simple test to verify aj_lightly theme is working"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import ttkbootstrap as tb
    from core.custom_themes import register_custom_themes
    
    print("Testing aj_lightly theme...")
    
    # Register custom themes
    register_custom_themes()
    
    # Check available themes
    style = tb.Style()
    themes = style.theme_names()
    print(f"Available themes: {themes}")
    
    if "aj_lightly" in themes:
        print("aj_lightly theme is registered!")
        
        # Try to create a test window
        window = tb.Window(themename="aj_lightly")
        window.title("aj_lightly Theme Test")
        window.geometry("400x300")
        
        # Add some test widgets
        frame = tb.Frame(window, padding=20)
        frame.pack(fill="both", expand=True)
        
        title = tb.Label(frame, text="aj_lightly Theme Test", font=("Arial", 16, "bold"))
        title.pack(pady=10)
        
        button = tb.Button(frame, text="Test Button", bootstyle="primary")
        button.pack(pady=5)
        
        entry = tb.Entry(frame, width=30)
        entry.pack(pady=5)
        entry.insert(0, "Test entry field")
        
        # Close button
        close_btn = tb.Button(frame, text="Close", command=window.quit, bootstyle="danger")
        close_btn.pack(pady=10)
        
        print("✅ aj_lightly theme test window created successfully!")
        print("Theme colors should be light with custom styling.")
        print("Close the window to end the test.")
        
        window.mainloop()
        
    else:
        print("❌ aj_lightly theme is NOT registered!")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
