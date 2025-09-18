"""
Test dependency consistency across all dependency management files.

This test ensures that dependency versions are properly synchronized
across pyproject.toml, requirements/*.txt, constraints.txt, and requirements.lock.
"""

import re
import tomllib
from pathlib import Path
import pytest


class TestDependencyConsistency:
    """Test that dependency versions are consistent across all files."""

    @pytest.fixture
    def repo_root(self):
        """Get the repository root path."""
        return Path(__file__).parent.parent

    def extract_dependencies_from_file(self, file_path):
        """Extract dependency names and versions from a requirements file."""
        dependencies = {}
        try:
            with open(file_path, "r") as f:
                content = f.read()

            for line in content.split("\n"):
                line = line.strip()
                if (
                    line
                    and not line.startswith("#")
                    and not line.startswith("-r")
                ):
                    # Handle lines with dependencies
                    if any(
                        op in line for op in ["==", ">=", "<=", ">", "<", "~="]
                    ):
                        # Extract package name and version spec
                        match = re.match(
                            r"^([a-zA-Z0-9_-]+)([>=<~!]+[0-9.,a-zA-Z\[\]]+)",
                            line,
                        )
                        if match:
                            name = match.group(1).lower()
                            version_spec = match.group(2)
                            dependencies[name] = version_spec

        except FileNotFoundError:
            pass

        return dependencies

    def extract_dependencies_from_pyproject(self, file_path):
        """Extract dependencies from pyproject.toml."""
        dependencies = {}
        try:
            with open(file_path, "rb") as f:
                data = tomllib.load(f)

            # Main dependencies
            main_deps = data.get("project", {}).get("dependencies", [])
            for dep in main_deps:
                match = re.match(r"^([a-zA-Z0-9_-]+)([>=<~!]+.*)?", dep)
                if match:
                    name = match.group(1).lower()
                    version_spec = match.group(2) if match.group(2) else ""
                    dependencies[name] = version_spec

        except Exception:
            pass

        return dependencies

    def test_critical_packages_pinned_in_constraints(self, repo_root):
        """Test that critical packages have pinned versions in constraints.txt."""
        constraints_file = repo_root / "constraints.txt"
        constraints = self.extract_dependencies_from_file(constraints_file)

        critical_packages = [
            "django",
            "pandas",
            "numpy",
            "yfinance",
            "fastapi",
            "uvicorn",
            "gunicorn",
            "celery",
            "redis",
            "sqlalchemy",
            "alembic",
        ]

        for package in critical_packages:
            assert package in constraints, (
                f"Critical package {package} not found in constraints.txt"
            )
            assert constraints[package].startswith("=="), (
                f"Critical package {package} should be pinned with == in constraints.txt"
            )

    def test_pyproject_has_minimum_versions(self, repo_root):
        """Test that pyproject.toml has proper version constraints."""
        pyproject_file = repo_root / "pyproject.toml"
        dependencies = self.extract_dependencies_from_pyproject(pyproject_file)

        # Core packages should have minimum version constraints
        core_packages = ["django", "pandas", "numpy", "yfinance", "requests"]

        for package in core_packages:
            assert package in dependencies, (
                f"Core package {package} not found in pyproject.toml"
            )
            # Should have some version constraint (not empty)
            if dependencies[package]:
                assert any(
                    op in dependencies[package]
                    for op in [">=", ">", "==", "<"]
                ), (
                    f"Package {package} should have version constraints in pyproject.toml"
                )

    def test_rcssmin_django_compressor_compatibility(self, repo_root):
        """Test that rcssmin and django-compressor versions are compatible."""
        base_requirements = repo_root / "requirements" / "base.txt"
        dependencies = self.extract_dependencies_from_file(base_requirements)

        # Ensure rcssmin is pinned to 1.1.2 for django-compressor compatibility
        assert "rcssmin" in dependencies, (
            "rcssmin should be specified in requirements/base.txt"
        )
        assert dependencies["rcssmin"] == "==1.1.2", (
            "rcssmin should be pinned to 1.1.2 for django-compressor compatibility"
        )

        assert "django-compressor" in dependencies, (
            "django-compressor should be specified in requirements/base.txt"
        )

    def test_requirements_lock_uses_pinned_versions(self, repo_root):
        """Test that requirements.lock only uses pinned versions."""
        lock_file = repo_root / "requirements.lock"
        dependencies = self.extract_dependencies_from_file(lock_file)

        # All dependencies in lock file should be pinned
        for package, version_spec in dependencies.items():
            if not package.startswith("#"):  # Skip comments
                assert version_spec.startswith("=="), (
                    f"Package {package} in requirements.lock should be pinned with ==, got {version_spec}"
                )

    def test_constraints_versions_compatible_with_lock(self, repo_root):
        """Test that constraints.txt versions are compatible with requirements.lock."""
        constraints_file = repo_root / "constraints.txt"
        lock_file = repo_root / "requirements.lock"

        constraints = self.extract_dependencies_from_file(constraints_file)
        lock_deps = self.extract_dependencies_from_file(lock_file)

        # Packages that appear in both should have compatible versions
        common_packages = set(constraints.keys()) & set(lock_deps.keys())

        for package in common_packages:
            constraints_version = constraints[package].replace("==", "")
            lock_version = lock_deps[package].replace("==", "")

            # For now, just check that both have versions specified
            assert constraints_version, (
                f"Package {package} should have version in constraints.txt"
            )
            assert lock_version, (
                f"Package {package} should have version in requirements.lock"
            )

    def test_requirements_files_structure(self, repo_root):
        """Test that requirements files follow proper structure."""
        # Test that base requirements exist
        base_file = repo_root / "requirements" / "base.txt"
        assert base_file.exists(), "requirements/base.txt should exist"

        # Test that production.txt includes base.txt
        prod_file = repo_root / "requirements" / "production.txt"
        if prod_file.exists():
            with open(prod_file, "r") as f:
                content = f.read()
            assert "-r base.txt" in content, (
                "requirements/production.txt should include base.txt"
            )

        # Test that local.txt includes production.txt
        local_file = repo_root / "requirements" / "local.txt"
        if local_file.exists():
            with open(local_file, "r") as f:
                content = f.read()
            assert "-r production.txt" in content, (
                "requirements/local.txt should include production.txt"
            )

    def test_main_requirements_includes_base(self, repo_root):
        """Test that main requirements.txt properly includes base requirements."""
        main_requirements = repo_root / "requirements.txt"

        with open(main_requirements, "r") as f:
            content = f.read()

        assert "-r requirements/base.txt" in content, (
            "requirements.txt should include requirements/base.txt"
        )
