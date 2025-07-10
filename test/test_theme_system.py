#!/usr/bin/env python3
"""Test script for theme system components"""

import ttkbootstrap as tb
from ttkbootstrap.constants import *
import logging
import sys

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

# Import our modules
from core.theme_manager import ThemeManager
from core.custom_themes import register_custom_themes
from core.utils import load_user_theme, save_user_theme

def test_theme_system():
    """Test various theme system components"""
    logger = logging.getLogger("theme_test")
    
    logger.info("=== Theme System Test ===")
    
    # Step 1: Register custom themes
    logger.info("1. Registering custom themes...")
    result = register_custom_themes()
    logger.info(f"   Result: {'Success' if result else 'Failed'}")
    
    # Step 2: Create ThemeManager and check available themes
    logger.info("\n2. Creating ThemeManager...")
    theme_manager = ThemeManager()
    available_themes = theme_manager.style.theme_names()
    logger.info(f"   Available themes: {', '.join(available_themes)}")
    
    # Step 3: Check user settings
    logger.info("\n3. Checking user theme settings...")
    user_theme = load_user_theme()
    logger.info(f"   Current user theme: {user_theme}")
    
    # Step 4: Test window with theme
    logger.info("\n4. Creating test windows with themes...")
    
    # Test custom dark theme
    logger.info("   Testing aj_darkly theme...")
    try:
        window1 = tb.Window(title="Test Dark Theme", themename="aj_darkly")
        
        # Add some test widgets
        frame1 = tb.Frame(window1, padding=20)
        frame1.pack(fill=BOTH, expand=YES)
        
        tb.Label(frame1, text="Test Dark Theme (aj_darkly)", font=("Helvetica", 16)).pack(pady=10)
        
        # Add a toggle switch
        toggle1 = tb.Checkbutton(frame1, text="Dark Theme Toggle", bootstyle="success-round-toggle")
        toggle1.pack(pady=10)
        toggle1.invoke()  # Make it on by default
        
        # Add standard button
        btn1 = tb.Button(frame1, text="Standard Button", bootstyle="primary")
        btn1.pack(pady=10)
        
        # Add outline button
        btn2 = tb.Button(frame1, text="Outline Button", bootstyle=("info", "outline"))
        btn2.pack(pady=10)
        
        # Show the window
        window1.update()
        logger.info("   ✓ aj_darkly theme window created successfully")
    except Exception as e:
        logger.error(f"   ✗ Failed to create aj_darkly theme window: {e}")
    
    # Test custom light theme
    logger.info("   Testing aj_lightly theme...")
    try:
        window2 = tb.Window(title="Test Light Theme", themename="aj_lightly")
        
        # Add some test widgets
        frame2 = tb.Frame(window2, padding=20)
        frame2.pack(fill=BOTH, expand=YES)
        
        tb.Label(frame2, text="Test Light Theme (aj_lightly)", font=("Helvetica", 16)).pack(pady=10)
        
        # Add a toggle switch
        toggle2 = tb.Checkbutton(frame2, text="Light Theme Toggle", bootstyle="warning-round-toggle")
        toggle2.pack(pady=10)
        toggle2.invoke()  # Make it on by default
        
        # Add standard button
        btn3 = tb.Button(frame2, text="Standard Button", bootstyle="primary")
        btn3.pack(pady=10)
        
        # Add outline button
        btn4 = tb.Button(frame2, text="Outline Button", bootstyle=("info", "outline"))
        btn4.pack(pady=10)
        
        # Show the window
        window2.update()
        logger.info("   ✓ aj_lightly theme window created successfully")
    except Exception as e:
        logger.error(f"   ✗ Failed to create aj_lightly theme window: {e}")
    
    logger.info("\n5. Test theme switching...")
    
    # Create a main window for testing theme switching
    main_window = tb.Window(title="Theme Switcher Test", themename=user_theme)
    main_window.geometry("500x400")
    
    main_frame = tb.Frame(main_window, padding=20)
    main_frame.pack(fill=BOTH, expand=YES)
    
    tb.Label(
        main_frame, 
        text="Theme System Test", 
        font=("Helvetica", 16, "bold")
    ).pack(pady=10)
    
    # Theme selector
    themes_frame = tb.Frame(main_frame)
    themes_frame.pack(fill=X, pady=20)
    
    tb.Label(themes_frame, text="Select Theme:").pack(side=LEFT, padx=(0, 10))
    
    theme_var = tb.StringVar(value=user_theme)
    theme_combo = tb.Combobox(
        themes_frame, 
        textvariable=theme_var,
        values=available_themes,
        bootstyle="primary"
    )
    theme_combo.pack(side=LEFT, fill=X, expand=YES)
    
    def change_theme():
        new_theme = theme_var.get()
        logger.info(f"Changing theme to: {new_theme}")
        try:
            theme_manager.set_theme(new_theme)
            save_user_theme(new_theme)
            result_var.set(f"Theme changed to {new_theme}")
        except Exception as e:
            logger.error(f"Failed to change theme: {e}")
            result_var.set(f"Error: {str(e)}")
    
    tb.Button(
        themes_frame,
        text="Apply Theme",
        command=change_theme,
        bootstyle="success"
    ).pack(side=LEFT, padx=(10, 0))
    
    # Result label
    result_var = tb.StringVar(value="Select a theme and click Apply")
    result_label = tb.Label(
        main_frame,
        textvariable=result_var,
        bootstyle="info"
    )
    result_label.pack(pady=10)
    
    # Test widgets frame
    test_frame = tb.Frame(main_frame, bootstyle="default")
    test_frame.pack(fill=BOTH, expand=YES, pady=10)
    
    # Add test toggle
    test_toggle_var = tb.BooleanVar(value=True)
    test_toggle = tb.Checkbutton(
        test_frame,
        text="Test Toggle Switch",
        variable=test_toggle_var,
        bootstyle="warning-round-toggle"
    )
    test_toggle.pack(pady=10)
    
    # Add test buttons
    buttons_frame = tb.Frame(test_frame)
    buttons_frame.pack(fill=X, pady=10)
    
    tb.Button(
        buttons_frame,
        text="Primary Button",
        bootstyle="primary"
    ).pack(side=LEFT, padx=5, fill=X, expand=YES)
    
    tb.Button(
        buttons_frame,
        text="Secondary Button",
        bootstyle="secondary"
    ).pack(side=LEFT, padx=5, fill=X, expand=YES)
    
    tb.Button(
        buttons_frame,
        text="Info Outline",
        bootstyle=("info", "outline")
    ).pack(side=LEFT, padx=5, fill=X, expand=YES)
    
    logger.info("Starting main test window...")
    main_window.mainloop()

if __name__ == "__main__":
    test_theme_system()
