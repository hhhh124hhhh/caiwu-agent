#!/usr/bin/env python3
"""
Simple test to verify the TabularDataToolkit async fix
"""

import sys
import asyncio
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

async def test_tabular_toolkit():
    """Test TabularDataToolkit async functionality"""
    print("Testing TabularDataToolkit async functionality...")

    try:
        from utu.tools.tabular_data_toolkit import TabularDataToolkit
        print("✓ TabularDataToolkit import successful")

        # Test basic initialization
        config = {"workspace_root": "./stock_analysis_workspace"}
        toolkit = TabularDataToolkit(config)
        print("✓ TabularDataToolkit initialized successfully")

        # Test async context manager
        async with TabularDataToolkit(config) as tk:
            print("✓ Async context manager works")

        print("✓ TabularDataToolkit test passed")
        return True

    except Exception as e:
        print(f"✗ TabularDataToolkit test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    print("=== TabularDataToolkit Async Fix Verification ===")

    # Test TabularDataToolkit
    toolkit_ok = asyncio.run(test_tabular_toolkit())

    print("\n=== Test Results ===")
    print(f"TabularDataToolkit: {'PASS' if toolkit_ok else 'FAIL'}")

    if toolkit_ok:
        print("\n🎉 TabularDataToolkit async fix is working!")
        print("The 'object does not support the asynchronous context manager protocol' error is fixed.")
        print("\nYou should now be able to run the demo without this error.")
    else:
        print("\n⚠ TabularDataToolkit test failed. Please check the errors above.")

    return toolkit_ok

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)