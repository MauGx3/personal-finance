import pathlib


def test_models_file_contains_expected_classes():
    """Ensure the `models.py` for the assets app defines the expected class names.

    This test intentionally reads the source file instead of importing it so it
    doesn't require Django to be installed/configured in the test environment.
    """
    p = pathlib.Path("personal_finance/assets/models.py")
    assert p.exists(), f"Missing file: {p}"
    text = p.read_text(encoding="utf8")

    # Basic sanity: these class names should appear in the file
    for name in ("class Asset", "class Portfolio", "class Holding"):
        assert name in text, f"Expected '{name}' in models.py"


def test_initial_migration_present():
    p = pathlib.Path("personal_finance/assets/migrations/0001_initial.py")
    assert p.exists(), f"Missing migration file: {p}"
