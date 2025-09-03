import sys
from pathlib import Path

# Ensure the project's src/ directory is on sys.path so tests and
# VS Code test discovery can import the `personal_finance` package
# without installing the package.
ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))
