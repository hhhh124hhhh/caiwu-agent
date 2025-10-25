#!/usr/bin/env python3
"""
Direct test of TabularDataToolkit without full import
"""

import sys
import asyncio
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

async def test_tabular_toolkit_direct():
    """Test TabularDataToolkit directly"""
    print("Testing TabularDataToolkit directly...")

    try:
        # Import the module components directly
        from utu.config import ToolkitConfig
        from utu.tools.base import AsyncBaseToolkit

        print("✓ Base modules import successful")

        # Test the class definition
        exec("""
import sys
sys.path.insert(0, str(project_root))
from utu.tools.tabular_data_toolkit import TabularDataToolkit

async def test():
    config = {"workspace_root": "./stock_analysis_workspace"}
    toolkit = TabularDataToolkit(config)

    # Test async context manager
    async with TabularDataToolkit(config) as tk:
        print("✓ Async context manager works")

    return True

result = asyncio.run(test())
print("✓ Direct test successful" if result else "✗ Direct test failed")
""")

        return True

    except Exception as e:
        print(f"✗ Direct test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    print("=== Direct TabularDataToolkit Fix Test ===")

    # Test TabularDataToolkit
    toolkit_ok = asyncio.run(test_tabular_toolkit_direct())

    print("\n=== Test Results ===")
    print(f"TabularDataToolkit: {'PASS' if toolkit_ok else 'FAIL'}")

    if toolkit_ok:
        print("\n🎉 TabularDataToolkit async fix is working!")
        print("The error should be resolved.")
    else:
        print("\n⚠ Test failed. Check errors above.")

    return toolkit_ok

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)