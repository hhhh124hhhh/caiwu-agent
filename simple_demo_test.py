#!/usr/bin/env python3
"""
Simple demo test without unicode issues
"""

import os
import sys
from pathlib import Path

def check_system_readiness():
    """Check if system is ready for demo"""
    print("=== Demo System Check ===")

    # Check workspace
    workspace_path = Path("./stock_analysis_workspace")
    workspace_path.mkdir(exist_ok=True)
    print(f"Workspace: {workspace_path.absolute()}")

    # Check configuration files
    config_files = [
        "configs/agents/examples/stock_analysis_final.yaml",
        "examples/stock_analysis/stock_analysis_examples.json",
        "configs/agents/workers/report_agent.yaml"
    ]

    all_good = True
    for config_file in config_files:
        if Path(config_file).exists():
            print(f"✓ {config_file}")
        else:
            print(f"✗ {config_file}")
            all_good = False

    # Check environment variables
    required_vars = ["UTU_LLM_TYPE", "UTU_LLM_MODEL", "UTU_LLM_API_KEY"]
    print("\nEnvironment Variables:")
    for var in required_vars:
        value = os.environ.get(var)
        if value:
            masked = value[:10] + "..." if len(value) > 10 else value
            print(f"✓ {var}: {masked}")
        else:
            print(f"✗ {var}: Not set")
            all_good = False

    return all_good

def check_demo_files():
    """Check existing demo files"""
    print("\n=== Existing Demo Files ===")

    workspace_path = Path("./stock_analysis_workspace")
    if workspace_path.exists():
        files = list(workspace_path.glob("*"))
        if files:
            print(f"Found {len(files)} files:")
            for file in files:
                size = file.stat().st_size
                file_type = "HTML" if file.suffix == ".html" else "PDF" if file.suffix == ".pdf" else "Other"
                print(f"  - {file.name} ({size} bytes) [{file_type}]")
        else:
            print("No existing demo files found")

    return True

def main():
    """Main test function"""
    print("Demo Readiness Test")
    print("==================")

    system_ok = check_system_readiness()
    files_ok = check_demo_files()

    print("\n=== Test Results ===")
    print(f"System Ready: {'YES' if system_ok else 'NO'}")
    print(f"Demo Files: {'YES' if files_ok else 'NO'}")

    if system_ok:
        print("\n=== Demo Instructions ===")
        print("1. cd examples/stock_analysis")
        print("2. python main.py --stream")
        print("3. Select demo case 1-5")
        print("4. View generated HTML/PDF files")
        print("\nDemo Cases Available:")
        print("1. Single Company Analysis (Shaanxi Construction)")
        print("2. Brand Value Analysis (Kweichow Moutai)")
        print("3. EV Giants Comparison (CATL vs BYD)")
        print("4. Banking Stability Analysis (ICBC)")
        print("5. Multi-Company Comparison")

        return True
    else:
        print("\nSystem not ready for demo. Please check configuration.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)