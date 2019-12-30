"""Some convenient utils functions."""

import datetime
import os
import socket
import sys
import traceback
import uuid

import pytz


def import_from_path(path):
    """Import a module / class from a path string.
    :param str path: class path, e.g., ndscheduler.corescheduler.job
    :return: class object
    :rtype: class
    """

    components = path.split('.')
    module = __import__('.'.join(components[:-1]))
    for comp in components[1:-1]:
        module = getattr(module, comp)
    return getattr(module, components[-1])


def get_current_datetime():
    """Retrieves the current datetime.
    :return: A datetime representing the current time.
    :rtype: datetime
    """
    return datetime.datetime.utcnow().replace(tzinfo=pytz.utc)


def get_job_name(job):
    """Returns job name.
    :param Job job: An apscheduler.job.Job instance.
    :return: task name
    :rtype: str
    """
    return job.args[0]


def get_job_args(job):
    """Returns arguments of a job.
    :param Job job: An apscheduler.job.Job instance.
    :return: task arguments
    :rtype: list of str
    """
    return job.args[5:]


def get_job_kwargs(job):
    """Returns keyword arguments of a job.
    :param Job job: An apscheduler.job.Job instance.
    :return: keyword arguments
    :rtype: dict
    """
    return job.kwargs


def get_cron_strings(job):
    """Returns cron strings.
    :param Job job: An apscheduler.job.Job instance.
    :return: cron strings
    :rtype: dict
    """
    return {
        'month': str(job.trigger.fields[1]),
        'day': str(job.trigger.fields[2]),
        'week': str(job.trigger.fields[3]),
        'day_of_week': str(job.trigger.fields[4]),
        'hour': str(job.trigger.fields[5]),
        'minute': str(job.trigger.fields[6])}


def generate_uuid():
    """Generates 32-digit hex uuid.
    Example: d8f376e858a411e4b6ae22001ac68d05
    :return: uuid hex string
    :rtype: str
    """
    return uuid.uuid4().hex


def get_stacktrace():
    """Returns the full stack trace."""

    type_, value_, traceback_ = sys.exc_info()
    return ''.join(traceback.format_exception(type_, value_, traceback_))


def get_hostname():
    """Returns the host name."""
    return socket.gethostname()


def get_pid():
    """Returns the process ID"""
    return os.getpid()


def get_datastore_instance(datastore_class_path, db_config=None, db_tablenames=None):
    datastore_class = import_from_path(datastore_class_path)
    return datastore_class.get_instance(db_config, db_tablenames)
