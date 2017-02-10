"""Settings to override default settings."""

import logging

logging.getLogger().setLevel(logging.DEBUG)

DEBUG = True
HTTP_PORT = 8888
HTTP_ADDRESS = '0.0.0.0'
JOB_CLASS_PACKAGES = ['scheduler.jobs']
