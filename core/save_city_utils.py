"""
Utility for save city button logic, to be reused across components.
Compatible with ttkbootstrap or customtkinter.
"""

def create_save_city_button(parent, city_data, on_save_callback, style='primary'):
    """
    Create a save city button.
    Args:
        parent: parent frame
        city_data: dict with city info (can be None initially)
        on_save_callback: function to call when button is pressed
        style: style string (for ttkbootstrap or customtkinter)
    Returns:
        button: the created Button
    """
    # Try customtkinter first for rounded styling, then fallback to ttkbootstrap, then tkinter
    btn = None
    ctk_loaded = False
    try:
        import customtkinter as ctk
        ctk_loaded = True
        def handle_save():
            # Get city_data from the button's attribute (updated dynamically)
            current_city_data = getattr(btn, 'city_data', None)
            print(f"[DEBUG] Save button clicked - city_data: {current_city_data}")
            on_save_callback(current_city_data)
        # Map style to customtkinter options (rounded corners, color)
        ctk_kwargs = {
            'text': "Save City",
            'command': handle_save,
            'corner_radius': 20,  # rounded edges
        }
        # Optionally map style to fg_color if desired
        style_map = {
            'primary': '#007bff',
            'success': '#28a745',
            'danger': '#dc3545',
            'warning': '#ffc107',
            'info': '#17a2b8',
        }
        if style in style_map:
            ctk_kwargs['fg_color'] = style_map[style]
        btn = ctk.CTkButton(parent, **ctk_kwargs)
    except Exception:
        ctk_loaded = False
    if not btn:
        try:
            import ttkbootstrap as tb
            def handle_save():
                # Get city_data from the button's attribute (updated dynamically)
                current_city_data = getattr(btn, 'city_data', None)
                print(f"[DEBUG] Save button clicked - city_data: {current_city_data}")
                on_save_callback(current_city_data)
            btn = tb.Button(parent, text="Save City", command=handle_save)
            if hasattr(btn, 'configure'):
                try:
                    btn.configure(bootstyle=style)
                except Exception:
                    pass
        except Exception:
            import tkinter as tk
            def handle_save():
                # Get city_data from the button's attribute (updated dynamically)
                current_city_data = getattr(btn, 'city_data', None)
                print(f"[DEBUG] Save button clicked - city_data: {current_city_data}")
                on_save_callback(current_city_data)
            btn = tk.Button(parent, text="Save City", command=handle_save)
    
    # Set the initial city_data
    btn.city_data = city_data
    return btn
