Changelog Management
===================

The personal-finance project uses a structured changelog system compatible with Sphinx documentation. This guide explains how to maintain and update the project's changelog.

Overview
--------

The changelog follows the `Keep a Changelog <https://keepachangelog.com/>`_ format and is automatically integrated with the Sphinx documentation system. Changes are categorized into six standard sections:

- **Added**: New features and functionality
- **Fixed**: Bug fixes and issue resolutions  
- **Changed**: Changes to existing functionality
- **Deprecated**: Features marked for removal in future versions
- **Removed**: Removed features and functionality
- **Security**: Security improvements and fixes

Files and Structure
-------------------

The changelog system consists of several files:

- ``docs/changelog.rst`` - Main changelog documentation
- ``docs/changelog_template.rst`` - Template for new entries
- ``docs/changelog_utils.py`` - Python utilities for changelog management
- ``docs/Makefile`` - Build commands including changelog validation

Sphinx Integration
------------------

The changelog is automatically integrated into the Sphinx documentation through:

1. **Extensions**: The ``sphinx.ext.extlinks`` extension provides shortcuts for linking to GitHub issues, PRs, and commits
2. **Navigation**: Added to the main documentation toctree in ``index.rst``
3. **Versioning**: Automatic version detection from the package ``__version__``

External Links
~~~~~~~~~~~~~~

You can use these shortcuts in changelog entries:

- ``:issue:`123``` - Links to GitHub issue #123
- ``:pr:`45``` - Links to pull request #45  
- ``:commit:`abc123``` - Links to specific commit

Usage Instructions
------------------

Validating Changelog Format
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To ensure the changelog follows the correct format:

.. code-block:: bash

   make changelog-validate

Or directly:

.. code-block:: bash

   python docs/changelog_utils.py --validate

Creating New Version Sections
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To create a new version section template:

.. code-block:: bash

   make changelog-new-section VERSION=1.2.0

This generates a properly formatted section with all standard categories.

Manual Editing
~~~~~~~~~~~~~~

When adding entries manually:

1. Open ``docs/changelog.rst``
2. Find the appropriate version section
3. Add entries under the relevant category (Added, Fixed, etc.)
4. Use external link shortcuts when referencing issues or PRs
5. Validate the format using ``make changelog-validate``

Version Management
------------------

The system automatically detects the current version from ``src/personal_finance/__init__.py``. The version is used in:

- Sphinx configuration (``conf.py``)
- Changelog validation
- Documentation generation

To check the current version:

.. code-block:: bash

   python docs/changelog_utils.py --get-version

Best Practices
--------------

1. **Regular Updates**: Update the changelog with every significant change
2. **Clear Descriptions**: Write clear, user-focused descriptions of changes
3. **Categorization**: Place entries in the most appropriate category
4. **External References**: Link to relevant issues and PRs
5. **Version Consistency**: Ensure version numbers match package version
6. **Validation**: Always validate format before committing changes

Integration with Development Workflow
-------------------------------------

The changelog system integrates with:

- **Git Hooks**: Consider adding changelog validation to pre-commit hooks
- **CI/CD**: Validation can be automated in continuous integration
- **Release Process**: Changelog entries help generate release notes
- **Documentation**: Automatically included in generated documentation

Troubleshooting
---------------

Common issues and solutions:

**Version Import Errors**
   If version detection fails, the system falls back to "0.1.0". Ensure the package structure is correct.

**Format Validation Failures**
   Run ``make changelog-validate`` to identify specific formatting issues.

**Missing External Links**
   Verify that ``extlinks`` configuration in ``conf.py`` is correct.

**Documentation Build Errors**
   Check that ``changelog.rst`` is properly included in the main ``index.rst`` toctree.

Migration from Other Systems
----------------------------

If migrating from other changelog formats:

1. Review existing entries for consistency
2. Reorganize into standard categories
3. Add proper reStructuredText formatting
4. Validate the new format
5. Update any automated tooling

Future Enhancements
-------------------

Potential improvements to consider:

- Automated changelog generation from commit messages
- Integration with conventional commits
- Release note generation from changelog entries
- Enhanced validation rules
- Git tag integration for version management