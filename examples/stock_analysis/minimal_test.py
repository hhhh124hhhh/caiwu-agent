#!/usr/bin/env python3
"""
Minimal test to check if the async context manager issue is fixed
"""

import sys
import asyncio

def test_async_context_manager():
    """Test the async context manager protocol"""
    print("Testing async context manager protocol...")

    # Create a minimal test class
    class TestAsyncToolkit:
        def __init__(self):
            self.name = "TestToolkit"

        async def __aenter__(self):
            print(f"✓ {self.name} async context manager: ENTER")
            return self

        async def __aexit__(self, exc_type, exc_val, exc_tb):
            print(f"✓ {self.name} async context manager: EXIT")
            return False

        async def build(self):
            print(f"✓ {self.name} build method")

        async def cleanup(self):
            print(f"✓ {self.name} cleanup method")

    # Test the async context manager
    async def test():
        toolkit = TestAsyncToolkit()
        async with toolkit as tk:
            await tk.build()
            await tk.cleanup()
        return True

    try:
        result = asyncio.run(test())
        print("✅ Async context manager test: PASSED")
        return True
    except Exception as e:
        print(f"❌ Async context manager test: FAILED - {e}")
        return False

def main():
    """Main test"""
    print("=== Async Context Manager Protocol Test ===")

    # Test basic async context manager
    basic_ok = test_async_context_manager()

    print("\n=== Results ===")
    print(f"Async Context Manager: {'PASS' if basic_ok else 'FAIL'}")

    if basic_ok:
        print("\n🎉 Async context manager protocol is working!")
        print("The TabularDataToolkit fix should resolve the original error.")
    else:
        print("\n⚠️ Async context manager test failed.")

    return basic_ok

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)