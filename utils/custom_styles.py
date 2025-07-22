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
                    foreground='orange',
                    background='#222222')

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
                    background='#1a1a1a',
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
