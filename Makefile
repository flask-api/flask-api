.PHONY: all
all: install

# PROJECT DEPENDENCIES #########################################################

export PIPENV_SHELL_COMPAT=true
export PIPENV_VENV_IN_PROJECT=true

ENV := .venv
DEPENDENCIES := $(ENV)/.installed
PIP := $(ENV)/bin/pip

.PHONY: install
install: $(DEPENDENCIES)

$(DEPENDENCIES): $(PIP) Pipfile*
	pipenv install --dev --ignore-hashes
	@ touch $@

$(PIP):
	pipenv --python=python3.6

# VALIDATION TARGETS ###########################################################

.PHONY: test
test: install ## Run tests and linters
	pipenv run nosetests flask_api
	pipenv run flake8 flask_api --ignore=E128,E501 --exclude=__init__.py

# CLEANUP ######################################################################

.PHONY: clean
clean:
	rm -rf $(ENV)
