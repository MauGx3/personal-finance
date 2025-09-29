# ruff: noqa: ERA001, PTH100
# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.

import os
import sys

import django

# Ensure the repository root is on sys.path so Sphinx can import the
# Django settings module (config.settings.local) during CI (GitHub Actions,
# ReadTheDocs, etc.). Previously we tried to use /app which doesn't exist
# in the Actions runner and caused ModuleNotFoundError: No module named 'config'.
sys.path.insert(0, os.path.abspath(".."))

# Also make src/ importable (some projects put the package in src/)
sys.path.insert(0, os.path.abspath("../src"))

# Keep a couple of ReadTheDocs-specific environment fallbacks when appropriate.
if os.getenv("READTHEDOCS", default="False") == "True":
    os.environ["DJANGO_READ_DOT_ENV_FILE"] = "True"
    os.environ["USE_DOCKER"] = "no"
os.environ["DATABASE_URL"] = "sqlite:///readthedocs.db"
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")

# Try to setup Django but be defensive: only call django.setup() when the
# configured settings module can be found. This avoids Sphinx aborting with
# a ConfigError when the project hasn't been installed yet on CI runners.
_DJANGO_AVAILABLE = False
try:  # pragma: no cover - best-effort in CI
    import importlib
    import importlib.util

    # If django is not importable, skip setup entirely.
    try:
        import django as _django
    except Exception:
        _django = None

    if _django is not None:
        settings_mod = os.environ.get("DJANGO_SETTINGS_MODULE")
        # Only call setup() if the settings module (or its package) is importable.
        if settings_mod and importlib.util.find_spec(settings_mod):
            try:
                _django.setup()
                _DJANGO_AVAILABLE = True
            except Exception:
                # If setup fails, continue without Django to allow Sphinx to
                # build non-Django docs. Some autodoc features may be limited.
                _DJANGO_AVAILABLE = False
        else:
            # Don't attempt to initialise Django when settings aren't present.
            _DJANGO_AVAILABLE = False
except Exception:
    _DJANGO_AVAILABLE = False

# -- Project information -----------------------------------------------------

project = "personal-finance"
copyright = """2025, Mauricio Gioachini"""  # noqa: A001
author = "Mauricio Gioachini"

# The version info for the project you're documenting, acts as replacement for
# |version| and |release|, also used in various other places throughout the
# built documents.
#
# Import version from the package
try:
    import sys
    import os

    # Prefer reading the installed package version if available.
    try:
        # When the package is installed (pip install -e .) this will work.
        from importlib.metadata import version as _pkg_version

        version = _pkg_version("personal-finance")
        release = version
    except Exception:
        # Fall back to importing the local package from the repo's src/ dir.
        sys.path.insert(0, os.path.abspath("../src"))
        from personal_finance import __version__

        version = __version__
        release = __version__
except ImportError:
    # Fallback version if import fails
    version = "0.1.0"
    release = "0.1.0"


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.extlinks",
    "sphinx.ext.intersphinx",
    "sphinx.ext.viewcode",
    "sphinx.ext.githubpages",  # Creates .nojekyll file for GitHub Pages
    "sphinx_rtd_theme",
]

# Add any paths that contain templates here, relative to this directory.
# templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "sphinx_rtd_theme"

# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.
html_theme_options = {
    "canonical_url": "",
    "analytics_id": "",  # Provided by you in the web interface
    "analytics_anonymize_ip": False,
    "logo_only": False,
    "display_version": True,
    "prev_next_buttons_location": "bottom",
    "style_external_links": False,
    "vcs_pageview_mode": "",
    "style_nav_header_background": "#2980B9",
    # Toc options
    "collapse_navigation": True,
    "sticky_navigation": True,
    "navigation_depth": 4,
    "includehidden": True,
    "titles_only": False,
}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
# html_static_path = ["_static"]

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = "sphinx"

# Custom sidebar templates, must be a dictionary that maps document names
# to template names.
html_sidebars = {
    "**": [
        "about.html",
        "navigation.html",
        "relations.html",  # needs 'show_related': True theme option to display
        "searchbox.html",
        "donate.html",
    ]
}

# -- Options for extlinks extension ------------------------------------------

# Configure external links for easy referencing
extlinks = {
    "issue": (
        "https://github.com/MauGx3/personal-finance/issues/%s",
        "issue #%s",
    ),
    "pr": ("https://github.com/MauGx3/personal-finance/pull/%s", "PR #%s"),
    "commit": (
        "https://github.com/MauGx3/personal-finance/commit/%s",
        "commit %s",
    ),
}

# -- Options for intersphinx extension ---------------------------------------

# Configure cross-references to other documentation
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "django": (
        "https://docs.djangoproject.com/en/stable/",
        "https://docs.djangoproject.com/en/stable/_objects/",
    ),
    "sphinx": ("https://www.sphinx-doc.org/en/master/", None),
}
