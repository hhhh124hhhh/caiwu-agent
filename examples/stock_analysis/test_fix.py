#!/usr/bin/env python3
"""
Test script to verify the TabularDataToolkit fix
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

        # Test async context manager
        config = {"workspace_root": "./stock_analysis_workspace"}
        async with TabularDataToolkit(config) as toolkit:
            print("✓ Async context manager works")

            # Test get_tools_map_func
            tools_map = await toolkit.get_tools_map_func()
            print(f"✓ Tools map: {list(tools_map.keys())}")

        print("✓ TabularDataToolkit test passed")
        return True

    except Exception as e:
        print(f"✗ TabularDataToolkit test failed: {e}")
        return False

async def test_orchestra_init():
    """Test orchestra agent initialization"""
    print("\nTesting orchestra agent initialization...")

    try:
        from utu.agents import OrchestraAgent
        from utu.config import ConfigLoader

        # Load config
        config = ConfigLoader.load_agent_config("examples/stock_analysis_final")
        print("✓ Config loaded successfully")

        # Initialize agent (without build)
        runner = OrchestraAgent(config)
        print("✓ OrchestraAgent initialized successfully")

        # Try to build
        await runner.build()
        print("✓ OrchestraAgent built successfully")

        return True

    except Exception as e:
        print(f"✗ OrchestraAgent test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    print("=== TabularDataToolkit Fix Verification ===")

    # Test TabularDataToolkit
    toolkit_ok = asyncio.run(test_tabular_toolkit())

    # Test OrchestraAgent
    orchestra_ok = asyncio.run(test_orchestra_init())

    print("\n=== Test Results ===")
    print(f"TabularDataToolkit: {'PASS' if toolkit_ok else 'FAIL'}")
    print(f"OrchestraAgent: {'PASS' if orchestra_ok else 'FAIL'}")

    if toolkit_ok and orchestra_ok:
        print("\n🎉 All tests passed! The fix is working.")
        print("\nYou can now run the demo with:")
        print("python main.py --stream")
    else:
        print("\n⚠ Some tests failed. Please check the errors above.")

    return toolkit_ok and orchestra_ok

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)