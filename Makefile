# Project settings
PROJECT := Flask-API
PACKAGE := flask_api
REPOSITORY := flask-api/flask-api

# Project paths
PACKAGES := $(PACKAGE) tests
CONFIG := $(wildcard *.py)
MODULES := $(wildcard $(PACKAGE)/*.py)

# Virtual environment paths
export PIPENV_VENV_IN_PROJECT=true
export PIPENV_IGNORE_VIRTUALENVS=true
VENV := .venv

# MAIN TASKS ##################################################################

.PHONY: all
all: install

.PHONY: ci
ci: check test ## Run all tasks that determine CI status

.PHONY: run ## Start the program
run: install
	pipenv run python $(PACKAGE)/__main__.py

# PROJECT DEPENDENCIES ########################################################

DEPENDENCIES := $(VENV)/.installed

.PHONY: install
install: $(DEPENDENCIES)

$(DEPENDENCIES): Pipfile* setup.py
	pipenv run python setup.py develop
	pipenv install --dev -r requirements-dev.txt
	@ touch $@

# CHECKS ######################################################################

FLAKE8 := pipenv run flake8

.PHONY: check
check: flake8 ## Run linters and static analysis

.PHONY: flake8
flake8: install
	$(FLAKE8) flask_api --ignore=E128,E501,W503 --exclude=__init__.py

# TESTS #######################################################################

PYTEST := pipenv run pytest --cov=$(PACKAGE) --cov-report=html
COVERAGESPACE := pipenv run coveragespace

RANDOM_SEED ?= $(shell date +%s)

.PHONY: test
test: install ## Run unit and integration tests
	$(PYTEST) $(PACKAGE) $(NOSE_OPTIONS)
	$(COVERAGESPACE) update overall

.PHONY: read-coverage
read-coverage:
	open htmlcov/index.html

# DOCUMENTATION ###############################################################

MKDOCS := pipenv run mkdocs

MKDOCS_INDEX := site/index.html

.PHONY: docs
docs: mkdocs ## Generate documentation

.PHONY: mkdocs
mkdocs: install $(MKDOCS_INDEX)
$(MKDOCS_INDEX): mkdocs.yml docs/*.md
	$(MKDOCS) build --clean --strict

.PHONY: mkdocs-live
mkdocs-live: mkdocs
	eval "sleep 3; open http://127.0.0.1:8000" &
	$(MKDOCS) serve

# BUILD #######################################################################

DIST_FILES := dist/*.tar.gz dist/*.whl

.PHONY: dist
dist: install $(DIST_FILES)
$(DIST_FILES): $(MODULES)
	rm -f $(DIST_FILES)
	pipenv run python setup.py check --restructuredtext --strict --metadata
	pipenv run python setup.py sdist
	pipenv run python setup.py bdist_wheel

# RELEASE ######################################################################

TWINE := pipenv run twine

.PHONY: upload
upload: dist ## Upload the current version to PyPI
	git diff --name-only --exit-code
	$(TWINE) upload dist/*.*
	open https://pypi.org/project/$(PROJECT)

# CLEANUP #####################################################################

.PHONY: clean
clean: .clean-build .clean-docs .clean-test .clean-install ## Delete all generated and temporary files

.PHONY: clean-all
clean-all: clean
	rm -rf $(VENV)

.PHONY: .clean-install
.clean-install:
	find $(PACKAGES) -name '*.pyc' -delete
	find $(PACKAGES) -name '__pycache__' -delete
	rm -rf *.egg-info

.PHONY: .clean-test
.clean-test:
	rm -rf .cache .pytest .coverage htmlcov xmlreport

.PHONY: .clean-docs
.clean-docs:
	rm -rf *.rst docs/apidocs *.html docs/*.png site

.PHONY: .clean-build
.clean-build:
	rm -rf *.spec dist build

# HELP ########################################################################

.PHONY: help
help: all
	@ grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.DEFAULT_GOAL := help
