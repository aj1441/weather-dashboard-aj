#!/usr/bin/env python3
"""
Test runner script for the weather dashboard application.

This script discovers and runs all tests in the project, providing
a comprehensive test suite execution with detailed reporting.
"""

import unittest
import sys
import os
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def run_all_tests():
    """Discover and run all tests in the project."""
    # Start from the project root
    start_dir = project_root
    
    # Discover all test files
    loader = unittest.TestLoader()
    suite = loader.discover(start_dir, pattern='test_*.py')
    
    # Create test runner with verbose output
    runner = unittest.TextTestRunner(
        verbosity=2,
        stream=sys.stdout,
        descriptions=True,
        failfast=False
    )
    
    # Run the tests
    print("=" * 80)
    print("WEATHER DASHBOARD TEST SUITE")
    print("=" * 80)
    print(f"Project root: {project_root}")
    print(f"Python version: {sys.version}")
    print("=" * 80)
    
    result = runner.run(suite)
    
    # Print summary
    print("=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped) if hasattr(result, 'skipped') else 0}")
    
    if result.failures:
        print("\nFAILURES:")
        for test, traceback in result.failures:
            print(f"  {test}: {traceback}")
    
    if result.errors:
        print("\nERRORS:")
        for test, traceback in result.errors:
            print(f"  {test}: {traceback}")
    
    # Return appropriate exit code
    return 0 if result.wasSuccessful() else 1

def run_specific_test(test_module):
    """Run a specific test module."""
    try:
        # Import the test module
        module = __import__(test_module)
        
        # Create test suite for the module
        loader = unittest.TestLoader()
        suite = loader.loadTestsFromModule(module)
        
        # Run the tests
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        
        return 0 if result.wasSuccessful() else 1
        
    except ImportError as e:
        print(f"Error importing test module '{test_module}': {e}")
        return 1

def run_service_tests():
    """Run only service layer tests."""
    return run_specific_test('test_services')

def run_model_tests():
    """Run only model tests."""
    return run_specific_test('test_weather_models')

def main():
    """Main entry point for the test runner."""
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == 'services':
            print("Running service layer tests...")
            return run_service_tests()
        elif command == 'models':
            print("Running model tests...")
            return run_model_tests()
        elif command == 'help':
            print("Usage:")
            print("  python test/run_tests.py          # Run all tests")
            print("  python test/run_tests.py services # Run service tests only")
            print("  python test/run_tests.py models   # Run model tests only")
            print("  python test/run_tests.py help     # Show this help")
            return 0
        else:
            print(f"Unknown command: {command}")
            print("Use 'help' to see available commands")
            return 1
    else:
        # Run all tests by default
        return run_all_tests()

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code) 