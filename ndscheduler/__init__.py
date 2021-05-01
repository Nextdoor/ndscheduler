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
import sys

import confuse
import argparse
from pathlib import Path
from os import environ
import bcrypt
from getpass import getpass
from time import sleep

from ndscheduler import default_settings


logger = logging.getLogger()
ch = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
ch.setFormatter(formatter)
logger.addHandler(ch)

ENVIRONMENT_VARIABLE = "NDSCHEDULER_SETTINGS_MODULE"

_settings_module = None


# Define functions for automated tests
def setup_package():
    global _settings_module
    _settings_module = environ.get(ENVIRONMENT_VARIABLE)
    environ[ENVIRONMENT_VARIABLE] = "ndscheduler.default_settings_test"
    # Re-initialize settings
    global settings
    settings.__init__()


def teardown_package():
    global _settings_module
    if _settings_module:
        environ[ENVIRONMENT_VARIABLE] = _settings_module
    # Re-initialize settings
    global settings
    settings.__init__()


def get_cli_args():
    parser = argparse.ArgumentParser(description="NDscheduler - web based cron replacement", add_help=False,)
    parser.add_argument(
        "--http-port",
        "-p",
        dest="HTTP_PORT",
        metavar="80-65535",
        help="web server port",
        type=int,
        choices=range(80, 65535),
    )
    parser.add_argument(
        "--http-address", "-a", dest="HTTP_ADDRESS", help="web server IP address", type=str,
    )
    parser.add_argument(
        "--nd-settings",
        "-s",
        dest="NDSCHEDULER_SETTINGS_MODULE",
        help="Python module with the settings to be used.",
        type=str,
    )
    parser.add_argument(
        "--debug", dest="DEBUG", action="store_true", help="enable debug mode",
    )
    parser.add_argument(
        "--logging-level", "-l", dest="LOGGING_LEVEL", help="logging level", type=str,
    )
    parser.add_argument(
        "--encrypt", "-e", help="Create hash value from password for use in AUTH_CREDENTIALS.", action="store_true",
    )

    args, _ = parser.parse_known_args()

    if args.DEBUG:
        args.LOGGING_LEVEL = "DEBUG"

    if args.encrypt:
        if args.DEBUG:
            print()
            print("WARNING: running in debug mode, password will be shown in clear text!")
            sleep(1)
        password = getpass(prompt="Enter password which should be hashed: ")
        sleep(0.2)
        pass_check = getpass(prompt="Re-enter password: ")
        if password != pass_check:
            print("The passwords don't match.")
            exit(1)
        if args.DEBUG:
            print(f"Password [{password}]")
        salt = bcrypt.gensalt()
        print(bcrypt.hashpw(password.encode(), salt).decode())
        exit(0)
    else:
        del args.encrypt

    try:
        logger.setLevel(logging._nameToLevel[args.LOGGING_LEVEL.upper()])
    except KeyError as e:
        logger.error(f"Unknown logging level: {e.args[0]}")
        # continue with default logging level
    except AttributeError:
        pass

    logger.debug(f"Command line arguments: {args}")

    return args, parser


def load_yaml_config(
    config_file=None, args=None, yaml_extras={}, app_name="ndscheduler", default_config=__name__,
):
    # Load config values from YAML file

    # Confuse template for YAML validation
    default_static_dir = Path(__file__).parent.joinpath("static")
    yaml_template = {
        "DEBUG": confuse.Choice([False, True], default=False),
        "STATIC_DIR_PATH": confuse.Filename(default=default_static_dir),
        "TEMPLATE_DIR_PATH": confuse.Filename(default=default_static_dir),
        "APP_INDEX_PAGE": confuse.String(default="index.html"),
        "WEBSITE_TITLE": confuse.String(default="Scheduler"),
        "HTTP_PORT": confuse.Integer(default=7777),
        "HTTP_ADDRESS": confuse.String(default="127.0.0.1"),
        "SSL_CERT": confuse.String(default=""),
        "SSL_KEY": confuse.String(default=""),
        "TORNADO_MAX_WORKERS": confuse.Integer(default=8),
        "THREAD_POOL_SIZE": confuse.Integer(default=4),
        "JOB_MAX_INSTANCES": confuse.Integer(default=3),
        "JOB_COALESCE": confuse.Choice([False, True], default=True),
        "TIMEZONE": confuse.String(default="UTC"),
        "JOB_MISFIRE_GRACE_SEC": confuse.Integer(default=3600),
        # Database settings
        "DATABASE_TABLENAMES": {
            "jobs_tablename": confuse.String(default="scheduler_jobs"),
            "executions_tablename": confuse.String(default="scheduler_execution"),
            "auditlogs_tablename": confuse.String(default="scheduler_jobauditlog"),
        },
        # SQLite
        "DATABASE_CLASS": confuse.Choice(["sqlite", "postgres", "mysql",], default="sqlite",),
        "DATABASE_CONFIG_DICT": {
            "file_path": confuse.String(default="datastore.db"),  # SQLite
            # additional attributes for MySQL and Postgres
            "user": confuse.String(default="username"),
            "password": confuse.String(default=""),
            "hostname": confuse.String(default="localhost"),
            "port": confuse.Integer(default=3306),  # MySQL default
            "database": confuse.String(default="scheduler"),
            "sslmode": confuse.String(default="disable"),
        },  # Postgres
        # ndscheduler is based on apscheduler. Here we can customize the apscheduler's main scheduler class
        # Please see ndscheduler/core/scheduler/base.py
        "SCHEDULER_CLASS": confuse.String(default="ndscheduler.corescheduler.core.base.BaseScheduler"),
        "LOGGING_LEVEL": confuse.String(default="INFO"),
        # Packages that contains job classes, e.g., simple_scheduler.jobs
        "JOB_CLASS_PACKAGES": confuse.StrSeq(default=""),
        # Secure Cookie Hash
        "SECURE_COOKIE": confuse.String(default="__TODO:_GENERATE_YOUR_OWN_RANDOM_VALUE_HERE__"),
        # Name of the secure cookie
        "COOKIE_NAME": confuse.String(default="user"),
        # Secure cookie age in days (decimals are supported)
        "COOKIE_MAX_AGE": confuse.Number(default=1),
        # Authentication
        # If needs authentication, modify the dict below e.g. AUTH_CREDENTIALS = {'username': 'password'}
        # The password must be hashed using bcrypt
        "AUTH_CREDENTIALS": dict,
        "ADMIN_USER": confuse.StrSeq(default=""),
        "HELP_URL": confuse.String(default=""),
        "MAIL_SERVER": confuse.StrSeq(),
        "ADMIN_MAIL": confuse.StrSeq(),
        "SERVER_MAIL": confuse.String(default=""),
    }

    yaml_template.update(yaml_extras)

    db_classes = {
        "sqlite": "ndscheduler.corescheduler.datastore.providers.sqlite.DatastoreSqlite",
        "postgres": "ndscheduler.corescheduler.datastore.providers.postgres.DatastorePostgres",
        "mysql": "ndscheduler.corescheduler.datastore.providers.mysql.DatastoreMySQL",
    }

    yaml_config = confuse.LazyConfig(app_name, default_config)
    logger.debug(f"Loading configuration from YAML config file, dir:{yaml_config.config_dir()}, file:{config_file}, ")
    if config_file:
        if Path(config_file).is_file():
            yaml_config.set_file(config_file)
        elif Path(yaml_config.config_dir()).joinpath(config_file).is_file():
            config_file = Path(yaml_config.config_dir()).joinpath(config_file)
            yaml_config.set_file(config_file)
        else:
            logging.error(f"Config file '{config_file}' doesn't exist.")
            exit(1)
    else:
        config_file = f"{yaml_config.config_dir()}/{confuse.CONFIG_FILENAME}"

    if args:
        yaml_config.set_args(args, dots=True)

    logger.info(f"Loaded YAML configuration: {config_file}")

    # Authentication is optional
    if "AUTH_CREDENTIALS" not in yaml_config:
        yaml_config["AUTH_CREDENTIALS"] = {}

    try:
        valid = yaml_config.get(yaml_template)
    except (confuse.NotFoundError, confuse.ConfigValueError) as e:
        logger.error(f"Value {e} in config file: {yaml_config.config_dir()}/" f"{confuse.CONFIG_FILENAME}")
        exit(1)

    try:
        logger.setLevel(logging._nameToLevel[valid["LOGGING_LEVEL"].upper()])
    except KeyError as e:
        logger.error(f"Unknown logging level: {e.args[0]}")
        # continue with default logging level

    logger.debug(f"YAML config: {valid}")
    # set database class type
    valid["DATABASE_CLASS"] = db_classes[valid["DATABASE_CLASS"]]

    # add YAML config settings (to be used by passwd)
    valid["YAML_CONFIG_FILE"] = config_file
    valid["YAML_CONFIG"] = yaml_config

    return valid


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

        # get command line arguments
        args, parser = get_cli_args()

        # Legacy config mode uses environment variable
        if ENVIRONMENT_VARIABLE in environ or args.NDSCHEDULER_SETTINGS_MODULE:
            # update this dict from default settings (but only for ALL_CAPS
            # settings)
            for setting in dir(default_settings):
                if setting == setting.upper():
                    setattr(self, setting, getattr(default_settings, setting))
            # use user-provided settings
            try:
                if args.NDSCHEDULER_SETTINGS_MODULE:
                    settings_module_path = args.NDSCHEDULER_SETTINGS_MODULE
                else:
                    settings_module_path = environ[ENVIRONMENT_VARIABLE]
                logging.debug(f"Import settings module {settings_module_path}")
                try:
                    settings_module = importlib.import_module(settings_module_path)
                    for setting in dir(settings_module):
                        if setting == setting.upper():
                            setting_value = getattr(settings_module, setting)
                            setattr(self, setting, setting_value)
                except ImportError as e:
                    error = ImportError(
                        'Could not import settings "%s" (Is it on sys.path?): %s' % (settings_module_path, e)
                    )
                    logger.warning(error)
            except KeyError:
                # NOTE: This is arguably an EnvironmentError, but that causes
                # problems with Python's interactive help.
                logger.warning(
                    ("Environment variable %s is undefined. " "Use default settings for now.") % ENVIRONMENT_VARIABLE
                )
            if hasattr(settings_module, "extra_parser"):
                parents = [parser, getattr(settings_module, "extra_parser")]
            else:
                parents = [parser]
            help_parser = argparse.ArgumentParser(
                description="NDscheduler - web based cron replacement",
                # Inherit options from previous parsers
                parents=parents,
            )
            _, _ = help_parser.parse_known_args()
            # update settings with CLI args
            for key, value in vars(args).items():
                if key == key.upper() and value is not None:
                    setattr(self, key, value)
        else:
            # Load config from YAML file
            extra_parser = argparse.ArgumentParser(
                description="NDscheduler - web based cron replacement",
                # Inherit options from previous parsers
                parents=[parser],
            )
            extra_parser.add_argument(
                "--yaml-config", "-y", dest="yaml_config", help="Path to yaml config file", type=str,
            )
            extra_args, _ = extra_parser.parse_known_args()
            valid = load_yaml_config(config_file=extra_args.yaml_config, args=args,)
            for key, value in valid.items():
                setattr(self, key, value)

    # Settings class end


# Instantiate the settings globally.
settings = Settings()

logger.debug(f"Settings: {settings.__dict__}")
