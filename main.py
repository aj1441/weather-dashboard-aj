"""Main entry point for the Weather Dashboard application."""

from gui.tabbed_main_window import TabbedWeatherDashboard

def main():
    """Launch the weather dashboard application"""
    app = TabbedWeatherDashboard()
    app.run()

if __name__ == "__main__":
    main()