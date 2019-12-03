# Makefile for easier installation and cleanup.
#
# Uses self-documenting macros from here:
# http://marmelab.com/blog/2016/02/29/auto-documented-makefile.html

PACKAGE=labella
EXAMPLE_DIR=examples

.PHONY: help dist examples

.DEFAULT_GOAL := help

help:
	@grep -E '^[0-9a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) |\
		 awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m\
		 %s\n", $$1, $$2}'

in: inplace
inplace:
	python setup.py build_ext -i

install: ## Install for the current user using the default python command
	python setup.py build_ext --inplace
	python setup.py install --user

test: in ## Run nosetests using the default nosetests command
	poetry run green -v ./tests/

clean: ## Clean build dist and egg directories left after install
	rm -rf ./dist ./build ./$(PACKAGE).egg-info ./cover
	rm -f MANIFEST
	find . -type f -iname '*.pyc' -delete
	find . -type d -name '__pycache__' -empty -delete
	$(MAKE) -C $(EXAMPLE_DIR) clean

develop: ## Install a development version of the package needed for testing
	python setup.py develop --user

dist: ## Make Python source distribution
	python setup.py sdist bdist_wheel

examples: install
	$(MAKE) -C $(EXAMPLE_DIR) all
