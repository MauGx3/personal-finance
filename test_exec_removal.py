#!/usr/bin/env python3
"""
Test to verify that all exec() function calls have been removed from the source code.
This addresses the security vulnerability PYL-W0122.
"""

import sys
import subprocess


def test_no_exec_in_source_code():
    """Test that no exec() calls remain in the source code files."""
    print("Testing for remaining exec() calls in source code...")

    # Search for exec() calls in Python files, excluding virtual environments and this test file
    try:
        result = subprocess.run(
            [
                "grep",
                "-r",
                "exec(",
                ".",
                "--include=*.py",
                "-n",
                "--exclude-dir=.venv*",
                "--exclude-dir=venv*",
                "--exclude=test_exec_removal.py",
            ],
            capture_output=True,
            text=True,
            cwd="/home/runner/work/personal-finance/personal-finance",
        )

        if result.returncode == 0:
            # Found exec() calls
            print("❌ Found remaining exec() calls in source code:")
            print(result.stdout)
            return False
        else:
            # No exec() calls found (grep returns 1 when no matches)
            print("✅ No exec() calls found in source code!")
            return True

    except Exception as e:
        print(f"Error during search: {e}")
        return False


def test_functionality_still_works():
    """Test that the modified files still function correctly."""
    print("\nTesting that modified files still work correctly...")

    try:
        # Test the data profiler implementation
        result1 = subprocess.run(
            [sys.executable, "test_data_profiler_implementation.py"],
            capture_output=True,
            text=True,
            cwd="/home/runner/work/personal-finance/personal-finance",
        )

        if result1.returncode != 0:
            print("❌ test_data_profiler_implementation.py failed:")
            print(result1.stdout)
            print(result1.stderr)
            return False

        # Test the demonstration solution
        result2 = subprocess.run(
            [sys.executable, "demonstrate_solution.py"],
            capture_output=True,
            text=True,
            cwd="/home/runner/work/personal-finance/personal-finance",
        )

        if result2.returncode != 0:
            print("❌ demonstrate_solution.py failed:")
            print(result2.stdout)
            print(result2.stderr)
            return False

        print("✅ All modified files work correctly!")
        return True

    except Exception as e:
        print(f"Error during functionality test: {e}")
        return False


def main():
    """Run all security validation tests."""
    print("Security Audit: exec() Removal Validation")
    print("=" * 50)

    success = True

    # Test 1: No exec() calls in source code
    if not test_no_exec_in_source_code():
        success = False

    # Test 2: Functionality still works
    if not test_functionality_still_works():
        success = False

    print("\n" + "=" * 50)
    if success:
        print("✅ SECURITY AUDIT PASSED!")
        print("All exec() function calls have been successfully removed.")
        print("The code is now more secure and follows best practices.")
        print("\nChanges made:")
        print("• Replaced exec() with direct function definitions")
        print("• Replaced exec() with direct function calls")
        print("• Maintained all original functionality")
        print("• Improved code readability and maintainability")
    else:
        print("❌ SECURITY AUDIT FAILED!")
        print("Some issues remain to be addressed.")

    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
