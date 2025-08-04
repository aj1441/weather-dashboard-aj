#!/usr/bin/env python3
"""
Fixed test runner script that runs tests in virtual environment context.

This script ensures tests run with proper dependencies and environment setup.
"""

import unittest
import sys
import os
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def run_all_tests():
    """Discover and run all tests in the project with proper error handling."""
    
    # Check if we're in a virtual environment
    venv_path = project_root / "venv"
    if not venv_path.exists():
        print("❌ Virtual environment not found. Please run:")
        print("   python3 -m venv venv")
        print("   source venv/bin/activate  # or venv\\Scripts\\activate on Windows")
        print("   pip install -r requirements.txt")
        return False
    
    # Start from the test directory to avoid import issues
    start_dir = project_root / "test"
    
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
    print("WEATHER DASHBOARD TEST SUITE (FIXED)")
    print("=" * 80)
    print(f"Project root: {project_root}")
    print(f"Python version: {sys.version}")
    print(f"Virtual env: {'✅ Active' if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix) else '❌ Not active'}")
    print("=" * 80)
    
    try:
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
            print("\n❌ FAILURES:")
            for test, traceback in result.failures:
                print(f"  - {test}")
        
        if result.errors:
            print("\n❌ ERRORS:")
            for test, traceback in result.errors:
                print(f"  - {test}")
        
        print("=" * 80)
        
        if result.wasSuccessful():
            print("✅ ALL TESTS PASSED!")
            return True
        else:
            print("❌ SOME TESTS FAILED")
            return False
            
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return False

def run_specific_module(module_name):
    """Run tests for a specific module."""
    print(f"Running tests for module: {module_name}")
    
    # Import and run specific test module
    try:
        suite = unittest.TestLoader().loadTestsFromName(f'test.{module_name}')
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        return result.wasSuccessful()
    except Exception as e:
        print(f"❌ Error running {module_name} tests: {e}")
        return False

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Run Weather Dashboard tests')
    parser.add_argument('--module', '-m', help='Run tests for specific module')
    parser.add_argument('--list', '-l', action='store_true', help='List available test modules')
    
    args = parser.parse_args()
    
    if args.list:
        test_files = list(Path('test').glob('test_*.py'))
        print("Available test modules:")
        for test_file in test_files:
            module_name = test_file.stem
            print(f"  - {module_name}")
    elif args.module:
        success = run_specific_module(args.module)
        sys.exit(0 if success else 1)
    else:
        success = run_all_tests()
        sys.exit(0 if success else 1)