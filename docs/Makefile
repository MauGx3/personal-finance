# Minimal makefile for Sphinx documentation
#

# You can set these variables from the command line, and also
# from the environment for the first two.
SPHINXOPTS    ?=
SPHINXBUILD   ?= sphinx-build
SOURCEDIR     = .
BUILDDIR      = ./_build
APP = /app

.PHONY: html livehtml apidocs changelog-validate changelog-new-section Makefile

# Put it first so that "make" without argument is like "make html".
html:
	@$(SPHINXBUILD) -M html "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O) -c .

# Build, watch and serve docs with live reload
livehtml:
	sphinx-autobuild -b html --host 0.0.0.0 --port 9000 --watch $(APP) -c . $(SOURCEDIR) $(BUILDDIR)/html

# Outputs rst files from django application code
apidocs:
	sphinx-apidoc -o $(SOURCEDIR)/api $(APP)

# Validate changelog format
changelog-validate:
	python $(SOURCEDIR)/changelog_utils.py --validate

# Create new changelog section (usage: make changelog-new-section VERSION=1.2.0)
changelog-new-section:
	@if [ -z "$(VERSION)" ]; then \
		echo "Usage: make changelog-new-section VERSION=x.y.z"; \
		exit 1; \
	fi
	python $(SOURCEDIR)/changelog_utils.py --create-section $(VERSION)

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O) -c .
