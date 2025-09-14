#!/usr/bin/env python3
"""
Run all tests for the financial analysis toolkit
"""

import subprocess
import sys
import os


def run_test_script(script_name):
    """Run a test script and return success status"""
    print(f"Running {script_name}...")
    try:
        result = subprocess.run([sys.executable, script_name], 
                              cwd=os.path.dirname(__file__),
                              capture_output=True, 
                              text=True, 
                              timeout=120)
        
        if result.returncode == 0:
            print(f"✓ {script_name} passed")
            print(result.stdout)
            return True
        else:
            print(f"✗ {script_name} failed")
            print(result.stderr)
            return False
    except subprocess.TimeoutExpired:
        print(f"✗ {script_name} timed out")
        return False
    except Exception as e:
        print(f"✗ Error running {script_name}: {e}")
        return False


def main():
    """Run all test scripts"""
    print("=== Running All Tests ===\n")
    
    # List of test scripts to run
    test_scripts = [
        "tests/test_data_tool.py",
        "tests/test_analyzer.py"
    ]
    
    passed = 0
    total = len(test_scripts)
    
    for script in test_scripts:
        if run_test_script(script):
            passed += 1
        print()  # Add spacing between tests
    
    print(f"=== Final Results ===")
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed!")
        return True
    else:
        print("❌ Some tests failed!")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)