SHELL:=/bin/bash
PYTHON=python
PIP=pip
FLAKE8_CHECKING=flake8 ndscheduler simple_scheduler --max-line-length 100

all: test

init:
	@echo "Initialize dev environment for ndscheduler ..."
	@echo "Install pre-commit hook for git."
	@echo "$(FLAKE8_CHECKING)" > .git/hooks/pre-commit && chmod 755 .git/hooks/pre-commit
	@echo "Setup python virtual environment."
	$(PIP) install flake8
	@echo "All Done."

test:
	make install
	make flake8
	$(PYTHON) setup.py test

install:
	make init
	$(PYTHON) setup.py install

flake8:
	$(FLAKE8_CHECKING)

clean:
	@($(PYTHON) setup.py clean) >& /dev/null || python setup.py clean
	@echo "Done."

simple:
	# Install dependencies
	$(PIP) install -r simple_scheduler/requirements.txt;

	# Uninstall ndscheduler, so that simple scheduler can pick up non-package code
	$(PIP) uninstall -y ndscheduler || true
	NDSCHEDULER_SETTINGS_MODULE=simple_scheduler.settings PYTHONPATH=.:$(PYTHONPATH) \
		$(PYTHON) simple_scheduler/scheduler.py
