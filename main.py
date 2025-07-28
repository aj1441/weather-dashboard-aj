"""Main entry point for the Weather Dashboard application.

This module serves as the application's entry point and handles:
1. Environment validation and configuration loading
2. Logging setup and initialization
3. Application startup coordination
4. High-level error handling and graceful shutdown

The main.py file is kept focused on application bootstrapping,
with all business logic and utilities moved to appropriate modules.
"""

import logging
import sys
import os
import signal
from pathlib import Path
from config import Config
from gui.tabbed_main_window import TabbedWeatherDashboard
from utils.conversion_utils import add_numbers, convert_to_fahrenheit
from utils.performance_optimizer import cleanup_performance_data


class App:
    """
    Main Weather Dashboard Application class.
    
    Encapsulates application lifecycle management including:
    - Configuration loading and validation
    - Logging setup
    - GUI initialization and execution
    - Error handling and graceful shutdown
    """
    
    def __init__(self):
        """Initialize the application."""
        self.config = None
        self.logger = None
        self.gui_app = None
    
    def setup_logging(self, config: Config):
        """
        Configure application-wide logging with both file and console handlers.
        
        Args:
            config: Application configuration object containing log settings
            
        This function:
        1. Creates log directory if needed
        2. Sets up console and file logging handlers
        3. Configures external library log levels
        4. Establishes unified log format
        """
        
        # Ensure log directory exists
        log_dir = Path(config.database_path).parent
        log_dir.mkdir(exist_ok=True)
        
        # Configure logging format
        log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        log_file = log_dir / 'weather_dashboard.log'
        
        # Setup logging configuration
        logging.basicConfig(
            level=getattr(logging, config.log_level.upper()),
            format=log_format,
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler(log_file, mode='a', encoding='utf-8')
            ]
        )
        
        # Set specific logger levels for external libraries
        logging.getLogger('requests').setLevel(logging.WARNING)
        logging.getLogger('urllib3').setLevel(logging.WARNING)
        
        self.logger = logging.getLogger(__name__)
    
    def validate_environment(self):
        """
        Validate that required environment is set up correctly.
        
        Returns:
            Config: Validated configuration object or None if validation fails
            
        This function:
        1. Loads and validates environment variables
        2. Validates API key format
        3. Ensures required directories exist
        4. Provides helpful error messages for common issues
        """
        try:
            config = Config.from_environment()
            
            # Basic API key validation (just check it's not the placeholder)
            if "your_" in config.api_key.lower() or len(config.api_key) < 10:
                logging.warning("API key appears to be a placeholder - please set your real API key in .env file")
            
            # Ensure data directory exists
            data_dir = Path(config.database_path).parent
            data_dir.mkdir(exist_ok=True)
            
            return config
            
        except ValueError as e:
            print(f"Configuration Error: {e}")
            print("\nTo fix this:")
            print("1. Create a .env file in the project root")
            print("2. Add your OpenWeatherMap API key:")
            print("   API_KEY=your_32_character_api_key_here")
            print("3. Optionally set other configuration:")
            print("   LOG_LEVEL=DEBUG")
            print("   REQUEST_TIMEOUT=15")
            return None
    
    def initialize(self):
        """
        Initialize the application with configuration and logging.
        
        Returns:
            bool: True if initialization successful, False otherwise
        """
        # Validate environment and load configuration
        self.config = self.validate_environment()
        if not self.config:
            return False
        
        # Setup logging
        self.setup_logging(self.config)
        
        self.logger.info("="*50)
        self.logger.info("Starting Weather Dashboard Application")
        self.logger.info(f"Python version: {sys.version}")
        self.logger.info(f"Working directory: {os.getcwd()}")
        self.logger.info(f"Config - Database: {self.config.database_path}")
        self.logger.info(f"Config - API timeout: {self.config.request_timeout}s")
        self.logger.info(f"Config - Max retries: {self.config.max_retries}")
        self.logger.info(f"Config - Rate limit: {self.config.min_request_interval}s")
        self.logger.info("="*50)
        
        # Print fallback tracking daily report
        try:
            from utils.fallback_tracker import fallback_tracker
            fallback_tracker.print_daily_report()
        except Exception as e:
            self.logger.warning(f"Could not load fallback tracker: {e}")
        
        return True
    
    def run(self):
        """
        Run the application main loop.
        
        Handles:
        - GUI initialization
        - Application execution
        - Error handling
        - Graceful shutdown
        """
        if not self.initialize():
            sys.exit(1)
        
        try:
            # Launch the GUI application
            self.gui_app = TabbedWeatherDashboard(self.config)
            self.logger.info("GUI application initialized successfully")
            
            self.gui_app.run()
            
        except ImportError as e:
            self.logger.error(f"Missing required dependencies: {e}")
            print(f"Import Error: {e}")
            print("\nTo fix this, install missing dependencies:")
            print("pip install -r requirements.txt")
            sys.exit(1)
            
        except KeyboardInterrupt:
            self.logger.info("Application interrupted by user")
            print("\nShutting down gracefully...")
            
        except Exception as e:
            self.logger.exception("Unexpected error occurred")
            print(f"Unexpected error: {e}")
            print("Check the log file for details: data/weather_dashboard.log")
            sys.exit(1)
        
        finally:
            # Clean up performance data before shutdown
            if self.logger:
                try:
                    cleanup_performance_data()
                except Exception as e:
                    self.logger.warning(f"Error during performance cleanup: {e}")
                
                self.logger.info("Weather Dashboard application shutting down")


def main():
    """
    Entry point for the Weather Dashboard application.
    
    Creates and runs the main App instance.
    """
    app = App()
    app.run()

if __name__ == "__main__":
    main()
    