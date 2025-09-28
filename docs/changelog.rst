Changelog
=========

This document tracks all notable changes to the personal-finance project.

The format is based on `Keep a Changelog <https://keepachangelog.com/en/1.0.0/>`_,
and this project adheres to `Semantic Versioning <https://semver.org/spec/v2.0.0.html>`_.

Version 0.1.0 (Unreleased)
---------------------------

Added
~~~~~
- *(assets)* Add assets CRUD, API, serializers and tests
- Add personal finance package with portfolio management and stock data integration
- Implement GUI layer with FastAPI and Tkinter for personal finance management
- Update Python version requirement and add gunicorn to dependencies
- Analyze test suite expansion requirements
- Expand test suite with comprehensive coverage
- Complete test suite expansion with comprehensive coverage
- Add complete sphinx changelog compatibility system
- *(deploy)* Add Leapcell stack example, deployment notes, and runtime PORT binding
- *(deploy)* Add Procfile, one-off migrate docs, readiness/liveness endpoints, and Leapcell env flags
- *(logs)* Migrate core logger from logging to loguru with security compliance
- *(logs)* Migrate Django apps and config files to loguru
- Add missing Django migrations for tax and backtesting apps
- *(api)* Implement comprehensive API router with viewset imports and error handling
- *(ci)* Enhance caching and dependency installation in CI workflow
- *(tasks)* Add new tasks for data source service, realtime price streamer, and data profiler completion
- *(memory-bank)* Mark TASK001 as completed and update tasks index
- *(loguru)* Implement minimal shim for loguru package for testing
- *(logging)* Centralize log level management and format across modules
- *(logging)* Add support for TRACE level and container-aware logging configuration

Fixed
~~~~~
- Requirements.txt to reduce vulnerabilities
- Requirements.txt to reduce vulnerabilities
- Add explicit check=False to subprocess.run calls for PYL-W1510
- Remove useless except handlers that raise immediately (PYL-W0706)
- Remove all exec() calls to address security vulnerability PYL-W0122
- Address logging security audit issues (PY-A6006)
- Resolve CI/CD test failures with Django setup and model compatibility
- *(ci)* Correct copilot setup workflow virtual environment handling
- *(deploy)* Use production settings for PaaS and avoid crash
- *(procfile)* Run gunicorn with production settings
- *(settings)* Guard dev-only packages in local settings to avoid PaaS crash
- *(health)* Add /kaithhealth alias for Leapcell probe
- *(api)* Make API router imports resilient so health probes and URLConf import won't crash on missing optional deps
- *(tests)* Let pytest-django manage test DB; remove manual migrate
- *(models)* Change on_delete behavior for Holding model's portfolio field to CASCADE
- Address PR review comments - update type hints and fix unused imports
- *(security)* Remove 0.0.0.0 from ALLOWED_HOSTS to resolve BAN-B104
- *(ci)* Ensure loguru is installed for logging modules in CI
- *(gitignore)* Add .DS_Store to ignore list
- *(docker)* Switch to pg_isready for Postgres readiness checks
- *(docker)* Bind Postgres to localhost to enhance security
- *(docker)* Add healthcheck using pg_isready for Postgres readiness

Changed
~~~~~~~
- Remove assert statement from non-test files
- Change methods not using its bound instance to staticmethods

Deprecated
~~~~~~~~~~
- N/A

Removed
~~~~~~~
- N/A

Security
~~~~~~~~
- Implemented secure user authentication and authorization
- Added data validation and sanitization
- Configured secure Django settings for production deployment
