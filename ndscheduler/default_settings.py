"""Default settings."""

import logging
import os


#
# Development mode or production mode
# If DEBUG is True, then auto-reload is enabled, i.e., when code is modified, server will be
# reloaded immediately
#
DEBUG = True

#
# Static Assets
#
# The web UI is a single page app. All javascripts/css files should be in STATIC_DIR_PATH
#
STATIC_DIR_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'static')
TEMPLATE_DIR_PATH = STATIC_DIR_PATH
APP_INDEX_PAGE = 'index.html'

#
# Server setup
#
HTTP_PORT = 7777
HTTP_ADDRESS = '127.0.0.1'

TORNADO_MAX_WORKERS = 8

#
# ApScheduler settings
#
THREAD_POOL_SIZE = 4
JOB_MAX_INSTANCES = 3
JOB_COALESCE = True
TIMEZONE = 'UTC'

# When a job is misfired -- A job were to run at a specific time, but due to some
# reason (e.g., scheduler restart), we miss that run.
#
# By default, if a job is misfired within 1 hour, the scheduler will rerun it.
# Otherwise, if it's misfired over 1 hour, the scheduler will not rerun it.
JOB_MISFIRE_GRACE_SEC = 3600

#
# Database settings
#
JOBS_TABLENAME = 'scheduler_jobs'
EXECUTIONS_TABLENAME = 'scheduler_execution'
AUDIT_LOGS_TABLENAME = 'scheduler_jobauditlog'

# See different database providers in ndscheduler/core/datastore/providers/

# SQLite
#
DATABASE_CLASS = 'ndscheduler.core.datastore.providers.sqlite.DatastoreSqlite'
DATABASE_CONFIG_DICT = {
    'file_path': 'datastore.db'
}

# Postgres
#
# DATABASE_CLASS = 'ndscheduler.core.datastore.providers.postgresql.DatastorePostgresql'
# DATABASE_CONFIG_DICT = {
#     'user': 'username',
#     'password': '',
#     'hostname': 'localhost',
#     'port': 5432,
#     'database': 'scheduler',
#     'sslmode': 'disable'
# }

# MySQL
#
# DATABASE_CLASS = 'ndscheduler.core.datastore.providers.mysql.DatastoreMysql'
# DATABASE_CONFIG_DICT = {
#     'user': 'username',
#     'password': '',
#     'hostname': 'localhost',
#     'port': 3306,
#     'database': 'scheduler'
# }

# ndschedule is based on apscheduler. Here we can customize the apscheduler's main scheduler class
# Please see ndscheduler/core/scheduler/base.py
SCHEDULER_CLASS = 'ndscheduler.core.scheduler.base.SingletonScheduler'

#
# Set logging level
#
logging.getLogger().setLevel(logging.INFO)


# Packages that contains job classes, e.g., simple_scheduler.jobs
JOB_CLASS_PACKAGES = []
