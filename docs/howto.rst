How To - Project Documentation
======================================================================

Get Started
----------------------------------------------------------------------

Documentation can be written as rst files in `personal_finance/docs`.


To build and serve docs, use the commands::

    docker compose -f docker-compose.docs.yml up



Changes to files in `docs/_source` will be picked up and reloaded automatically.

`Sphinx <https://www.sphinx-doc.org/>`_ is the tool used to build documentation.

Docstrings to Documentation
----------------------------------------------------------------------

The sphinx extension `apidoc <https://www.sphinx-doc.org/en/master/man/sphinx-apidoc.html>`_ is used to automatically document code using signatures and docstrings.

Numpy or Google style docstrings will be picked up from project files and available for documentation. See the `Napoleon <https://sphinxcontrib-napoleon.readthedocs.io/en/latest/>`_ extension for details.

For an in-use example, see the `page source <_sources/users.rst.txt>`_ for :ref:`users`.

To compile all docstrings automatically into documentation source files, use the command:
    ::

        make apidocs

Changelog Management
----------------------------------------------------------------------

The project includes an integrated changelog system compatible with Sphinx. The changelog tracks all notable changes and is automatically included in the generated documentation.

To validate the changelog format:
    ::

        make changelog-validate

To create a new version section:
    ::

        make changelog-new-section VERSION=1.2.0

For detailed information about changelog management, see :doc:`changelog_guide`.


This can be done in the docker container:
    ::

        docker run --rm docs make apidocs
