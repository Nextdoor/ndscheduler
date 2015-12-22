"""Settings and configuration for ndscheduler.

This will create a settings module that overrides default
settings (from the default_settings module) and it will override
those settings with values found in the module specified by the
NDSCHEDULER_SETTINGS_MODULE environment variable.

Any machine that wants to run a scheduler powered by ndscheduler MUST have
NDSCHEDULER_SETTINGS_MODULE as an environment variable or this module
will raise an exception.
"""

import importlib
import logging
import os
import sys

from ndscheduler import default_settings

logger = logging.getLogger()
ch = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)


ENVIRONMENT_VARIABLE = 'NDSCHEDULER_SETTINGS_MODULE'

_settings_module = None


def setup_package():
    global _settings_module
    _settings_module = os.environ.get(ENVIRONMENT_VARIABLE)
    os.environ[ENVIRONMENT_VARIABLE] = 'ndscheduler.default_settings_test'
    # Re-intitialize settings
    global settings
    settings.__init__()


def teardown_package():
    global _settings_module
    if _settings_module:
        os.environ[ENVIRONMENT_VARIABLE] = _settings_module
    # Re-intitialize settings
    global settings
    settings.__init__()


class Settings(object):
    """Singleton class to manage ndscheduler settings."""

    _instance = None

    def __new__(cls, *args, **kwargs):
        """Set this class up as a singleton."""

        if not cls._instance:
            cls._instance = super(Settings, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self, *args, **kwargs):
        """Instantiate the settings."""
        # update this dict from default settings (but only for ALL_CAPS
        # settings)
        for setting in dir(default_settings):
            if setting == setting.upper():
                setattr(self, setting, getattr(default_settings, setting))

        try:
            settings_module_path = os.environ[ENVIRONMENT_VARIABLE]
        except KeyError, e:
            # NOTE: This is arguably an EnvironmentError, but that causes
            # problems with Python's interactive help.
            logger.error(
                ('Settings cannot be imported, because environment '
                 'variable %s is undefined.') % ENVIRONMENT_VARIABLE)
            return

        try:
            settings_module = importlib.import_module(settings_module_path)
        except ImportError, e:
            error = ImportError(
                'Could not import settings "%s" (Is it on sys.path?): %s' %
                (settings_module_path, e))
            logger.error(error)
            return

        for setting in dir(settings_module):
            if setting == setting.upper():
                setting_value = getattr(settings_module, setting)
                setattr(self, setting, setting_value)

        # This setting lets the application know that settings
        # have been properly configured.
        self.PROPERLY_CONFIGURED = True

# Instantiate the settings globally.
settings = Settings()
