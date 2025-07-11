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
from pathlib import Path
from config import Config
from gui.tabbed_main_window import TabbedWeatherDashboard


def setup_logging(config: Config):
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

def validate_environment():
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

def main():
    """
    Launch the weather dashboard application with enhanced configuration and error handling.
    
    The startup sequence:
    1. Environment validation
    2. Logging setup
    3. Configuration logging
    4. GUI initialization
    5. Application main loop
    6. Graceful shutdown
    
    Handles common startup errors:
    - Missing dependencies
    - Configuration errors
    - Unexpected exceptions
    """
    
    # Validate environment and load configuration
    config = validate_environment()
    if not config:
        sys.exit(1)
    
    # Setup logging
    setup_logging(config)
    logger = logging.getLogger(__name__)
    
    logger.info("="*50)
    logger.info("Starting Weather Dashboard Application")
    logger.info(f"Python version: {sys.version}")
    logger.info(f"Working directory: {os.getcwd()}")
    logger.info(f"Config - Database: {config.database_path}")
    logger.info(f"Config - API timeout: {config.request_timeout}s")
    logger.info(f"Config - Max retries: {config.max_retries}")
    logger.info(f"Config - Rate limit: {config.min_request_interval}s")
    logger.info("="*50)
    
    try:
        # Launch the GUI application
        app = TabbedWeatherDashboard(config)
        logger.info("GUI application initialized successfully")
        
        app.run()
        
    except ImportError as e:
        logger.error(f"Missing required dependencies: {e}")
        print(f"Import Error: {e}")
        print("\nTo fix this, install missing dependencies:")
        print("pip install -r requirements.txt")
        sys.exit(1)
        
    except Exception as e:
        logger.exception("Unexpected error occurred")
        print(f"Unexpected error: {e}")
        print("Check the log file for details: data/weather_dashboard.log")
        sys.exit(1)
    
    finally:
        logger.info("Weather Dashboard application shutting down")

if __name__ == "__main__":
    main()