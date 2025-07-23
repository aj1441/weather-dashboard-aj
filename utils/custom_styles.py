import ttkbootstrap as tb
from user import USER_THEMES


def apply_custom_styles(style: tb.Style, theme_name="aj_lightly"):
    """
    Define and apply custom styles for ttkbootstrap widgets.
    This function should be called once after initializing ttkbootstrap Style().
    """
    theme_colors = USER_THEMES[theme_name]["colors"]
    # Example: Register a frame style for each color
    for key, hex_color in theme_colors.items():
        if hex_color.startswith("#") and len(hex_color) == 7:
            style_name = f"{key}.TFrame"
            style.configure(style_name, background=hex_color)

    # Custom Button
    style.configure('Custom.TButton',
                    font=('Helvetica', 12, 'bold'),
                    foreground='white',
                    background='#007BFF',
                    borderwidth=2,
                    focusthickness=3,
                    focuscolor='none',
                    padding=10)
    style.map('Custom.TButton',
              foreground=[('pressed', 'white'), ('active', '#FFD700')],
              background=[('pressed', '#0056b3'), ('active', '#3399FF')])

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
                    background=theme_colors.get("bg", "#222222"),
                    borderwidth=2,
                    relief='raised')

    style.configure('ForecastDay.TLabel',
                    font=('Helvetica Neue', 10, 'bold'),
                    foreground=theme_colors.get("fg", "white"),
                    background=theme_colors.get("bg", "#222222"))

    style.configure('ForecastIcon.TLabel',
                    font=('Helvetica Neue', 24),
                    foreground=theme_colors.get("primary", "#00f"),
                    background=theme_colors.get("bg", "#222222"))

    style.configure('ForecastTempHigh.TLabel',
                    font=('Helvetica Neue', 12, 'bold'),
                    foreground=theme_colors.get("accent", theme_colors.get("primary", "#ff0")),
                    background=theme_colors.get("bg", "#222222"))

    style.configure('ForecastTempLow.TLabel',
                    font=('Helvetica Neue', 11),
                    foreground=theme_colors.get("fg", "lightblue"),
                    background=theme_colors.get("bg", "#222222"))

    style.configure('ForecastDesc.TLabel',
                    font=('Helvetica Neue', 9, 'italic'),
                    foreground=theme_colors.get("fg", "white"),
                    background=theme_colors.get("bg", "#222222"))

    style.configure('ForecastPrecip.TLabel',
                    font=('Helvetica Neue', 9),
                    foreground="#00bfff",
                    background=theme_colors.get("bg", "#222222"))


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
