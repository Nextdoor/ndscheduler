SHELL:=/bin/bash
PYTHON=.venv/bin/python
PIP=.venv/bin/pip
SOURCE_VENV=. .venv/bin/activate
FLAKE8_CHECKING=$(SOURCE_VENV) && flake8 ndscheduler --max-line-length 120

all: test

init:
	@echo "Initialize dev environment for ndscheduler ..."
	@echo "Install pre-commit hook for git."
	@echo "$(FLAKE8_CHECKING)" > .git/hooks/pre-commit && chmod 755 .git/hooks/pre-commit
	@echo "Setup python virtual environment."
	if [ ! -d ".venv" ]; then python3 -m venv .venv; fi
	$(SOURCE_VENV) && $(PIP) install flake8
	@echo "All Done."

test:
	make install
	make flake8
	# Hacky way to ensure mock is installed before running setup.py
	$(SOURCE_VENV) && pip install mock==1.1.2 && $(PYTHON) setup.py test

install:
	make init
	$(SOURCE_VENV) && $(PYTHON) setup.py install

flake8:
	if [ ! -d ".venv" ]; then make init; fi
	$(SOURCE_VENV) && $(FLAKE8_CHECKING)

clean:
	@($(SOURCE_VENV) && $(PYTHON) setup.py clean) >& /dev/null || python setup.py clean
	@echo "Done."
