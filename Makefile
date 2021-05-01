SHELL:=/bin/bash
PYTHON=.venv/bin/python
PIP=.venv/bin/pip
SOURCE_VENV=. .venv/bin/activate
FLAKE8_CHECKING=$(SOURCE_VENV) && flake8 ndscheduler simple_scheduler --max-line-length 120

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
	export NDSCHEDULER_SETTINGS_MODULE=simple_scheduler.settings
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

simple:
	if [ ! -d ".venv" ]; then make install; fi

	# Install dependencies
	$(PIP) install -r simple_scheduler/requirements.txt;

	# Uninstall ndscheduler, so that simple scheduler can pick up non-package code
	$(SOURCE_VENV) && $(PIP) uninstall -y ndscheduler || true
	$(SOURCE_VENV) && \
		NDSCHEDULER_SETTINGS_MODULE=simple_scheduler.settings PYTHONPATH=.:$(PYTHONPATH) \
		$(PYTHON) simple_scheduler/scheduler.py
