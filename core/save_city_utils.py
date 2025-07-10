"""Utility for creating a save city button using ttkbootstrap."""

import logging

logger = logging.getLogger(__name__)

def create_save_city_button(parent, city_data, on_save_callback, style='primary'):
    """
    Create a save city button.
    Args:
        parent: parent frame
        city_data: dict with city info (can be None initially)
        on_save_callback: function to call when button is pressed
        style: ttkbootstrap bootstyle string
    Returns:
        button: the created Button
    """
    import ttkbootstrap as tb
    def handle_save():
        current_city_data = getattr(btn, 'city_data', None)
        logger.debug("Save button clicked - city_data: %s", current_city_data)
        
        # Make sure to use the proper city name from the API response
        if current_city_data:
            # Ensure we're using the properly capitalized city name from the API
            logger.debug("Using API-provided city name: %s", current_city_data.get('city', ''))
            
        on_save_callback(current_city_data)
    btn = tb.Button(parent, text="Save City", command=handle_save)
    if hasattr(btn, 'configure'):
        try:
            btn.configure(bootstyle=style)
        except Exception:
            pass
    
    # Set the initial city_data
    btn.city_data = city_data
    return btn
