#!/usr/bin/env python3
"""
Update script to sync changes from upstream Youtu-Agent repository
"""

import subprocess
import sys
import os

def run_command(command):
    """Run a shell command and return the result"""
    try:
        result = subprocess.run(command, shell=True, check=True, 
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE, 
                              text=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {command}")
        print(f"Error message: {e.stderr}")
        return None

def check_for_conflicts():
    """Check if there are merge conflicts"""
    try:
        result = subprocess.run("git diff --name-only --diff-filter=U", 
                              shell=True, check=True, 
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE, 
                              text=True)
        conflicts = result.stdout.strip().split('\n') if result.stdout.strip() else []
        return [f for f in conflicts if f]  # Remove empty strings
    except subprocess.CalledProcessError:
        return []

def main():
    print("Updating from upstream Youtu-Agent repository...")
    
    # Fetch updates from upstream
    print("1. Fetching updates from upstream...")
    result = run_command("git fetch upstream")
    if result is None:
        print("Failed to fetch from upstream")
        sys.exit(1)
    
    # Check current branch
    print("2. Checking current branch...")
    branch_result = run_command("git branch --show-current")
    if branch_result is None:
        print("Failed to get current branch")
        sys.exit(1)
    
    current_branch = branch_result
    print(f"   Current branch: {current_branch}")
    
    # Try to merge upstream changes
    print("3. Merging upstream changes...")
    merge_result = run_command(f"git merge upstream/main")
    
    # Check for conflicts
    conflicts = check_for_conflicts()
    if conflicts:
        print("WARNING: Merge conflicts detected!")
        print("Conflicting files:")
        for conflict in conflicts:
            print(f"  - {conflict}")
        print("\nPlease resolve conflicts manually, then run:")
        print("  git add <resolved-files>")
        print("  git commit")
        print("  git push origin main")
        sys.exit(1)
    elif merge_result is None:
        print("Failed to merge upstream changes")
        print("You may need to resolve conflicts manually")
        sys.exit(1)
    
    print(merge_result)
    
    # Push to your repository
    print("4. Pushing changes to your repository...")
    push_result = run_command(f"git push origin {current_branch}")
    if push_result is None:
        print("Failed to push changes to your repository")
        sys.exit(1)
    
    print("Update completed successfully!")
    print("Your repository is now synchronized with upstream Youtu-Agent")

if __name__ == "__main__":
    main()