#!/usr/bin/env python3
"""
Run all tests for the grid game application.

This script discovers and runs all test cases in the tests directory.
It provides a simple way to run the entire test suite with a single command.

Usage:
    python run_all_tests.py

The script can optionally generate JUnit XML reports for CI/CD integration.
"""

import unittest
import sys
import os
import xmlrunner  # This will be installed via requirements.txt

# Add the parent directory to the system path to allow imports
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)


def run_all_tests():
    """Discover and run all tests in the tests directory."""
    # Start at the current directory
    start_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Create a test loader
    loader = unittest.TestLoader()
    
    # Discover tests
    suite = loader.discover(start_dir, pattern='test_*.py')
    
    # Check if running in CI environment
    if os.environ.get('CI'):
        # Running in CI, use XMLRunner to generate JUnit report
        runner = xmlrunner.XMLTestRunner(output='junit-report.xml')
        result = runner.run(suite)
        return 0 if result.wasSuccessful() else 1
    else:
        # Running locally, use TextTestRunner for console output
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    print("Running all tests for Grid Game...\n")
    sys.exit(run_all_tests()) 