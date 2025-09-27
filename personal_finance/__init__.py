from pathlib import Path

# If a src/ copy of the package exists, add it to the package search path so
# submodules can be loaded from either the repo root or src/ depending on
# where a module is defined. We append (not prepend) to avoid hiding repo-root
# modules such as `personal_finance/assets/models.py`.
_repo_root = Path(__file__).resolve().parent.parent
_src_pkg = _repo_root / "src" / "personal_finance"
if _src_pkg.exists():
    src_pkg_str = str(_src_pkg)
    if src_pkg_str not in __path__:
        __path__.append(src_pkg_str)

__version__ = "0.1"
__version_info__ = tuple(
    int(num) if num.isdigit() else num
    for num in __version__.replace("-", ".", 1).split(".")
)
