# Minimal makefile for Sphinx documentation
# You can set these variables from the command line.
SPHINXOPTS  =
SPHINXBUILD = sphinx-build
SPHINXMODS  = sphinx-apidoc
SPHINXPROJ  = MangAdventure
SOURCEDIR   = .
BUILDDIR    = _build
APIEXCLUDE  = '../*migrations*' \
              '../setup.py' \
              '../manage.py' \
              '../*bad_bots.py' \
              '../*tests*'

.PHONY: help modules Makefile

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

# Generate modules documentation
modules:
	@$(SPHINXMODS) -M --no-toc --force -o "$(SOURCEDIR)/modules" \
		$(SPHINXOPTS) $(O) "$(SOURCEDIR)/.." $(APIEXCLUDE)

# Get the latest changes
changes:
	@awk '{gsub(/``/, "`")} /^$$/ && c==2 {exit} c==2; /^$$/{c++}' changelog.rst

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option. $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
