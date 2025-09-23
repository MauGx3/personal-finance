#!/usr/bin/env python3
"""
Changelog generation utilities for the personal-finance project.

This module provides utilities to help maintain and generate changelog entries
in a consistent format compatible with Sphinx documentation.
"""

import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

CHANGELOG_SECTIONS = [
    "Added",
    "Fixed", 
    "Changed",
    "Deprecated",
    "Removed",
    "Security"
]

def get_version_from_package() -> str:
    """Get the current version from the package __init__.py file."""
    try:
        # Try to import version from the package
        sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
        from personal_finance import __version__
        return __version__
    except ImportError:
        # Fallback to reading the file directly
        init_file = Path(__file__).parent.parent / "src" / "personal_finance" / "__init__.py"
        if init_file.exists():
            content = init_file.read_text()
            match = re.search(r'__version__\s*=\s*[\'"]([^\'"]+)[\'"]', content)
            if match:
                return match.group(1)
    
    return "0.1.0"  # Default fallback


def create_new_version_section(version: str, release_date: Optional[str] = None) -> str:
    """Create a new version section for the changelog."""
    if release_date is None:
        release_date = datetime.now().strftime("%Y-%m-%d")
    
    section = f"Version {version} ({release_date})\n"
    section += "-" * len(section) + "\n\n"
    
    for section_name in CHANGELOG_SECTIONS:
        section += f"{section_name}\n"
        section += "~" * len(section_name) + "\n"
        section += "- \n\n"  # Empty placeholder
    
    return section


def validate_changelog_format(changelog_path: Path) -> List[str]:
    """Validate the changelog format and return any issues found."""
    issues = []
    
    if not changelog_path.exists():
        issues.append(f"Changelog file not found: {changelog_path}")
        return issues
    
    content = changelog_path.read_text()
    
    # Check for required sections
    if "Changelog" not in content:
        issues.append("Missing main 'Changelog' heading")
    
    # Check for version format
    version_pattern = r"Version \d+\.\d+\.\d+.*"
    if not re.search(version_pattern, content):
        issues.append("No properly formatted version sections found")
    
    return issues


def get_latest_version_from_changelog(changelog_path: Path) -> Optional[str]:
    """Extract the latest version number from the changelog."""
    if not changelog_path.exists():
        return None
    
    content = changelog_path.read_text()
    version_match = re.search(r"Version (\d+\.\d+\.\d+)", content)
    
    if version_match:
        return version_match.group(1)
    
    return None


def main():
    """Main CLI interface for changelog utilities."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Changelog utilities")
    parser.add_argument("--validate", action="store_true", 
                       help="Validate changelog format")
    parser.add_argument("--get-version", action="store_true",
                       help="Get current package version")
    parser.add_argument("--create-section", metavar="VERSION",
                       help="Create new version section")
    
    args = parser.parse_args()
    
    docs_dir = Path(__file__).parent
    changelog_path = docs_dir / "changelog.rst"
    
    if args.validate:
        issues = validate_changelog_format(changelog_path)
        if issues:
            print("Changelog validation issues:")
            for issue in issues:
                print(f"  - {issue}")
            sys.exit(1)
        else:
            print("✓ Changelog format is valid")
    
    elif args.get_version:
        version = get_version_from_package()
        print(f"Current version: {version}")
    
    elif args.create_section:
        section = create_new_version_section(args.create_section)
        print("New changelog section:")
        print(section)
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()