#!/usr/bin/env python3
"""
Integration tests for logging system to ensure proper logging practices.

This test file validates that logging is working correctly across the application
and that log levels are appropriate.
"""

import unittest
import logging
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, Mock
from io import StringIO

from config import Config
from main import App


class TestLoggingIntegration(unittest.TestCase):
    """Test cases for logging system integration."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_config = Mock(spec=Config)
        self.test_config.log_level = "DEBUG"
        self.test_config.database_path = os.path.join(self.temp_dir, "test.db")
        
    def test_logging_setup(self):
        """Test that logging is properly configured."""
        app = App()
        
        # Test logging setup
        app.setup_logging(self.test_config)
        
        # Check that logger is created
        self.assertIsNotNone(app.logger)
        self.assertEqual(app.logger.name, 'main')
        
    def test_log_levels_configuration(self):
        """Test that different log levels are properly configured."""
        app = App()
        
        # Test with different log levels
        for level in ['DEBUG', 'INFO', 'WARNING', 'ERROR']:
            self.test_config.log_level = level
            app.setup_logging(self.test_config)
            
            root_logger = logging.getLogger()
            expected_level = getattr(logging, level)
            self.assertEqual(root_logger.level, expected_level)
    
    def test_log_file_creation(self):
        """Test that log file is created properly."""
        app = App()
        app.setup_logging(self.test_config)
        
        log_file = Path(self.temp_dir) / "weather_dashboard.log"
        
        # Log a test message
        app.logger.info("Test log message")
        
        # Check that log file was created
        self.assertTrue(log_file.exists())
        
        # Check that message was written to file
        with open(log_file, 'r') as f:
            content = f.read()
            self.assertIn("Test log message", content)
    
    def test_external_library_log_levels(self):
        """Test that external library log levels are properly set."""
        app = App()
        app.setup_logging(self.test_config)
        
        # Check that external library loggers are set to WARNING
        requests_logger = logging.getLogger('requests')
        urllib3_logger = logging.getLogger('urllib3')
        
        self.assertEqual(requests_logger.level, logging.WARNING)
        self.assertEqual(urllib3_logger.level, logging.WARNING)
    
    def test_console_and_file_handlers(self):
        """Test that both console and file handlers are configured."""
        app = App()
        
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            app.setup_logging(self.test_config)
            app.logger.info("Test console output")
            
            # Check console output
            console_output = mock_stdout.getvalue()
            self.assertIn("Test console output", console_output)
        
        # Check file output
        log_file = Path(self.temp_dir) / "weather_dashboard.log"
        with open(log_file, 'r') as f:
            file_content = f.read()
            self.assertIn("Test console output", file_content)
    
    def test_log_format(self):
        """Test that log messages have proper format."""
        app = App()
        app.setup_logging(self.test_config)
        
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            app.logger.info("Test format message")
            
            output = mock_stdout.getvalue()
            
            # Check that format includes timestamp, name, level, and message
            self.assertRegex(output, r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3} - main - INFO - Test format message')
    
    def tearDown(self):
        """Clean up test fixtures."""
        # Clean up temp directory
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)


class TestServiceLogging(unittest.TestCase):
    """Test logging in service classes."""
    
    def test_service_logger_names(self):
        """Test that services use proper logger names."""
        from services.weather_service import WeatherService
        from services.data_service import DataService
        from services.theme_service import ThemeService
        
        config = Mock(spec=Config)
        
        weather_service = WeatherService(config)
        data_service = DataService(config)
        theme_service = ThemeService(config)
        
        # Check logger names match module names
        self.assertEqual(weather_service.logger.name, 'services.weather_service')
        self.assertEqual(data_service.logger.name, 'services.data_service')
        self.assertEqual(theme_service.logger.name, 'services.theme_service')
    
    def test_error_logging_with_context(self):
        """Test that errors are logged with sufficient context."""
        from services.weather_service import WeatherService
        
        config = Mock(spec=Config)
        weather_service = WeatherService(config)
        
        with patch.object(weather_service.logger, 'error') as mock_error:
            # Simulate an error condition
            try:
                raise ValueError("Test error for logging")
            except Exception as e:
                weather_service.logger.error(f"Error getting weather: {e}")
            
            # Check that error was logged with context
            mock_error.assert_called_once()
            call_args = mock_error.call_args[0][0]
            self.assertIn("Error getting weather", call_args)
            self.assertIn("Test error for logging", call_args)


if __name__ == '__main__':
    unittest.main()