# Project settings
PROJECT := Flask-API
PACKAGE := flask_api
REPOSITORY := flask-api/flask-api

# Project paths
PACKAGES := $(PACKAGE) tests
CONFIG := $(wildcard *.py)
MODULES := $(wildcard $(PACKAGE)/*.py)

# Python settings
PYTHON_MAJOR ?= 2
PYTHON_MINOR ?= 7

# System paths
PLATFORM := $(shell python -c 'import sys; print(sys.platform)')
ifneq ($(findstring win32, $(PLATFORM)), )
	WINDOWS := true
	SYS_PYTHON_DIR := C:\\Python$(PYTHON_MAJOR)$(PYTHON_MINOR)
	SYS_PYTHON := $(SYS_PYTHON_DIR)\\python.exe
	# https://bugs.launchpad.net/virtualenv/+bug/449537
	export TCL_LIBRARY=$(SYS_PYTHON_DIR)\\tcl\\tcl8.5
else
	ifneq ($(findstring darwin, $(PLATFORM)), )
		MAC := true
	else
		LINUX := true
	endif
	SYS_PYTHON := python$(PYTHON_MAJOR)
	ifdef PYTHON_MINOR
		SYS_PYTHON := $(SYS_PYTHON).$(PYTHON_MINOR)
	endif
endif

# Virtual environment paths
ENV := .venv
ifneq ($(findstring win32, $(PLATFORM)), )
	BIN := $(ENV)/Scripts
	ACTIVATE := $(BIN)/activate.bat
	OPEN := cmd /c start
	PYTHON := $(BIN)/python.exe
	PIP := $(BIN)/pip.exe
else
	BIN := $(ENV)/bin
	ACTIVATE := . $(BIN)/activate
	ifneq ($(findstring cygwin, $(PLATFORM)), )
		OPEN := cygstart
	else
		OPEN := open
	endif
	PYTHON := $(BIN)/python
	PIP := $(BIN)/pip
endif

# MAIN TASKS ###################################################################

SNIFFER := pipenv run sniffer

.PHONY: all
all: install

.PHONY: ci
ci: check test ## Run all tasks that determine CI status

.PHONY: watch
watch: install .clean-test ## Continuously run all CI tasks when files chanage
	$(SNIFFER)

.PHONY: run ## Start the program
run: install
	$(PYTHON) $(PACKAGE)/__main__.py

# PROJECT DEPENDENCIES #########################################################

export PIPENV_SHELL_COMPAT=true
export PIPENV_VENV_IN_PROJECT=true
export PIPENV_IGNORE_VIRTUALENVS=true

DEPENDENCIES := $(ENV)/.installed
METADATA := *.egg-info

.PHONY: install
install: $(DEPENDENCIES) $(METADATA)

$(DEPENDENCIES): $(PIP) Pipfile*
	pipenv install --dev
ifdef WINDOWS
	@ echo "Manually install pywin32: https://sourceforge.net/projects/pywin32/files/pywin32"
else ifdef MAC
	$(PIP) install pync MacFSEvents
else ifdef LINUX
	$(PIP) install pyinotify
endif
	@ touch $@

$(METADATA): $(PYTHON) setup.py
	$(PYTHON) setup.py develop
	@ touch $@

$(PYTHON) $(PIP):
	pipenv --python=$(SYS_PYTHON)
	pipenv run pip --version

# CHECKS #######################################################################

FLAKE8 := pipenv run flake8

.PHONY: check
check: flake8 ## Run linters and static analysis

.PHONY: flake8
flake8: install
	$(FLAKE8) flask_api --ignore=E128,E501 --exclude=__init__.py

# TESTS ########################################################################

NOSE := pipenv run nosetests
COVERAGE := pipenv run coverage
COVERAGE_SPACE := pipenv run coverage.space

RANDOM_SEED ?= $(shell date +%s)

NOSE_OPTIONS := --with-doctest
ifndef DISABLE_COVERAGE
NOSE_OPTIONS += --with-coverage --cover-package=$(PACKAGE) --cover-erase --cover-html --cover-html-dir=htmlcov --cover-branches
endif

.PHONY: test
test: install ## Run unit and integration tests
	$(NOSE) $(PACKAGE) $(NOSE_OPTIONS)
	$(COVERAGE_SPACE) $(REPOSITORY) overall

.PHONY: read-coverage
read-coverage:
	$(OPEN) coverage/index.html

# DOCUMENTATION ################################################################

MKDOCS := pipenv run mkdocs

MKDOCS_INDEX := site/index.html

.PHONY: doc
doc: mkdocs ## Generate documentation

.PHONY: mkdocs
mkdocs: install $(MKDOCS_INDEX)
$(MKDOCS_INDEX): mkdocs.yml docs/*.md
	$(MKDOCS) build --clean --strict

.PHONY: mkdocs-live
mkdocs-live: mkdocs
	eval "sleep 3; open http://127.0.0.1:8000" &
	$(MKDOCS) serve

# BUILD ########################################################################

DIST_FILES := dist/*.tar.gz dist/*.whl

.PHONY: dist
dist: install $(DIST_FILES)
$(DIST_FILES): $(MODULES)
	rm -f $(DIST_FILES)
	$(PYTHON) setup.py check --restructuredtext --strict --metadata
	$(PYTHON) setup.py sdist
	$(PYTHON) setup.py bdist_wheel

# RELEASE ######################################################################

TWINE := pipenv run twine

.PHONY: register
register: dist ## Register the project on PyPI
	@ echo NOTE: your project must be registered manually
	@ echo https://github.com/pypa/python-packaging-user-guide/issues/263
	# TODO: switch to twine when the above issue is resolved
	# $(TWINE) register dist/*.whl

.PHONY: upload
upload: .git-no-changes register ## Upload the current version to PyPI
	$(TWINE) upload dist/*.*
	$(OPEN) https://pypi.python.org/pypi/$(PROJECT)

.PHONY: .git-no-changes
.git-no-changes:
	@ if git diff --name-only --exit-code;        \
	then                                          \
		echo Git working copy is clean...;        \
	else                                          \
		echo ERROR: Git working copy is dirty!;   \
		echo Commit your changes and try again.;  \
		exit -1;                                  \
	fi;

# CLEANUP ######################################################################

.PHONY: clean
clean: .clean-dist .clean-test .clean-doc .clean-build ## Delete all generated and temporary files

.PHONY: clean-all
clean-all: clean .clean-env .clean-workspace

.PHONY: .clean-build
.clean-build:
	find $(PACKAGES) -name '*.pyc' -delete
	find $(PACKAGES) -name '__pycache__' -delete
	rm -rf *.egg-info

.PHONY: .clean-doc
.clean-doc:
	rm -rf README.rst docs/apidocs *.html docs/*.png site

.PHONY: .clean-test
.clean-test:
	rm -rf .cache .pytest .coverage htmlcov xmlreport

.PHONY: .clean-dist
.clean-dist:
	rm -rf *.spec dist build

.PHONY: .clean-env
.clean-env: clean
	rm -rf $(ENV)

.PHONY: .clean-workspace
.clean-workspace:
	rm -rf *.sublime-workspace

# HELP #########################################################################

.PHONY: help
help: all
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.DEFAULT_GOAL := help
