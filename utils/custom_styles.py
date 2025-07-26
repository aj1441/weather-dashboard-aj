import ttkbootstrap as tb
from user import USER_THEMES


def apply_custom_styles(style: tb.Style, theme_name="aj_lightly"):
    """
    Define and apply custom styles for ttkbootstrap widgets.
    This function should be called once after initializing ttkbootstrap Style().
    """
    theme_colors = USER_THEMES[theme_name]["colors"]

    # Custom Button
    style.configure('Custom.TButton',
                    font=('Helvetica', 12, 'bold'),
                    foreground=theme_colors.get("bg", "#ffffff"),
                    background=theme_colors.get("info", "#17a2b8"),
                    borderwidth=2,
                    focusthickness=3,
                    focuscolor='none',
                    padding=10)
    style.map('Custom.TButton',
              foreground=[('pressed', theme_colors.get("danger", "#d9534f")), 
                         ('active', theme_colors.get("dark", "#343a40"))],
              background=[('pressed', '#13ce89'), 
                         ('active', theme_colors.get("success", "#02b875"))])

    # Custom Label
    style.configure('Custom.TLabel',
                    font=('Arial', 14),
                    foreground='#343a40',
                    background='#caa8e9')

    # Custom Entry
    style.configure('Custom.TEntry',
                    font=('Courier New', 12),
                    foreground='lime',
                    fieldbackground='black',
                    bordercolor='#333333',
                    lightcolor='#555555',
                    padding=5)

    # Custom Frame
    style.configure('Custom.TFrame',
                    background='#caa8e9',
                    borderwidth=5,
                    relief='groove')

    # Custom Progressbar
    style.configure('Custom.Horizontal.TProgressbar',
                    troughcolor='#2a2a2a',
                    background='#28a745',
                    thickness=20,
                    bordercolor='#444',
                    lightcolor='#28a745',
                    darkcolor='#1e7e34')

                # Frecast Card Styles
    style.configure('ForecastCard.TFrame',
                    background=theme_colors.get("light", "#cfd8dc"),
                    borderwidth=2,
                    relief='raised',
                    bordercolor=theme_colors.get("primary", "#007bff"))

    style.configure('ForecastDay.TLabel',
                    font=('Helvetica Neue', 10, 'bold'),
                    foreground=theme_colors.get("dark", "#121212"),
                    background=theme_colors.get("light", "#cfd8dc"))

    style.configure('ForecastIcon.TLabel',
                    font=('Helvetica Neue', 24),
                    foreground=theme_colors.get("primary", "#00f"),
                    background=theme_colors.get("light", "#cfd8dc"))

    style.configure('ForecastTempHigh.TLabel',
                    font=('Helvetica Neue', 12, 'bold'),
                    foreground=theme_colors.get("danger", "#dc3545"),  # Red for high temp
                    background=theme_colors.get("light", "#cfd8dc"))

    style.configure('ForecastTempLow.TLabel',
                    font=('Helvetica Neue', 11),
                    foreground=theme_colors.get("fg", "lightblue"),
                    background=theme_colors.get("light", "#cfd8dc"))

    style.configure('ForecastDesc.TLabel',
                    font=('Helvetica Neue', 9, 'italic'),
                    foreground=theme_colors.get("info", "#17a2b8"),   # Blue for low temp
                    background=theme_colors.get("light", "#cfd8dc"))

    style.configure('ForecastPrecip.TLabel',
                    font=('Helvetica Neue', 9),
                    foreground="#00bfff",
                    background=theme_colors.get("light", "#cfd8dc"))

    # Custom Scrollbar styles with purple color scheme - force override
    scrollbar_styles = {
        'background': "#bba4e2",     # Thumb: light purple
        'troughcolor': "#e8daf0",     # Track: very light purple  
        'bordercolor': "#b19cd9",     # Border: medium purple
        'arrowcolor': "#8e6cc2",      # Arrows: darker purple
        'darkcolor': "#9975c4",       # 3D shadow: medium-dark purple
        'lightcolor': "#dccae8",      # 3D highlight: lighter purple
        'relief': 'flat',
        'borderwidth': 1
    }
    
    # Apply to multiple scrollbar variants to ensure coverage
    scrollbar_types = ['Vertical.TScrollbar', 'TScrollbar', 'Scrollbar']
    for scrollbar_type in scrollbar_types:
        try:
            style.configure(scrollbar_type, **scrollbar_styles)
            style.map(scrollbar_type,
                      background=[('active', "#b19cd9"),    # Hover: medium purple
                                 ('pressed', "#7d5ba6")])   # Pressed: dark purple
        except Exception:
            pass  # Ignore if style doesn't exist

    # Add more styles below as needed


# Optional: For testing when running this module standalone
if __name__ == "__main__":
    app = tb.Window(themename="darkly")
    style = tb.Style()
    apply_custom_styles(style)

    frame = tb.Frame(app, style='Custom.TFrame', padding=20)
    frame.pack(padx=30, pady=30)

    label = tb.Label(frame, text="Hello, World!", style='Custom.TLabel')
    label.pack(pady=5)

    entry = tb.Entry(frame, style='Custom.TEntry')
    entry.pack(pady=5)

    button = tb.Button(frame, text="Submit", style='Custom.TButton')
    button.pack(pady=5)

    # Custom Progressbar
    from tkinter import IntVar
    progress_var = IntVar(value=50)
    progress = tb.Progressbar(frame,
                              style='Custom.Horizontal.TProgressbar',
                              orient='horizontal',
                              length=300,
                              variable=progress_var,
                              maximum=100)
    progress.pack(pady=10)

    app.mainloop()
