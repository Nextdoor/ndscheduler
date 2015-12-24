"""Settings to override default settings."""

import logging

#
# Override settings
#
DEBUG = True

HTTP_PORT = 8888
HTTP_ADDRESS = '0.0.0.0'

#
# Set logging level
#
logging.getLogger().setLevel(logging.DEBUG)

JOB_CLASS_PACKAGES = ['simple_scheduler.jobs']

DATABASE_CLASS = 'ndscheduler.core.datastore.providers.mysql.DatastoreMysql'
DATABASE_CONFIG_DICT = {
    'user': 'root',
    'password': '',
    'hostname': 'localhost',
    'port': 3306,
    'database': 'scheduler'
}
