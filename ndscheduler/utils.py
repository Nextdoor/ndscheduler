"""Some convenient utils functions."""

import datetime
import importlib
import logging
import glob
import os
import pytz
import sys
import traceback
import uuid

from ndscheduler import settings

logger = logging.getLogger(__name__)


def import_from_path(path):
    """Import a module / class from a path string.

    :param str path: class path, e.g., ndscheduler.core.job
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


def generate_uuid():
    """Generates 32-digit hex uuid.

    Example: d8f376e858a411e4b6ae22001ac68d05

    :return: uuid hex string
    :rtype: str
    """
    return uuid.uuid1().hex


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
    return job.args[2:]


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
        'month': unicode(job.trigger.fields[1]),
        'day': unicode(job.trigger.fields[2]),
        'week': unicode(job.trigger.fields[3]),
        'day_of_week': unicode(job.trigger.fields[4]),
        'hour': unicode(job.trigger.fields[5]),
        'minute': unicode(job.trigger.fields[6])}


def get_datastore_instance():
    """Returns a datastore instance.

    :return: a datastore instance
    :rtype: a subclass of ndscheduler.core.datastore.providers.base.DatastoreBase
    """
    database_class = import_from_path(settings.DATABASE_CLASS)
    return database_class.get_instance()


def get_stacktrace():
    """Returns the full stack trace."""

    type_, value_, traceback_ = sys.exc_info()
    return ''.join(traceback.format_exception(type_, value_, traceback_))


def get_all_available_jobs():
    """Returns a list of available jobs info.

    Looks like this:
        [
            {
                'job_class_string': 'myscheduler.jobs.myjob.MyJob',
                'arguments': [
                    {'type': 'string', 'description': 'name of this channel'},
                    {'type': 'string', 'description': 'what this channel does'},
                    {'type': 'int', 'description': 'created year'}
                ],
                'example_arguments': '["music channel", "it's an awesome channel", 1997]',
                'notes': 'need to specify environment variable API_KEY first'
            }
        ]
    :return: a list of available jobs info.
    :rtype: a list of dict
    """

    # Prevent circular import
    from ndscheduler import job

    results = []
    for job_class_package in settings.JOB_CLASS_PACKAGES:
        try:
            package = importlib.import_module(job_class_package)
        except ImportError:
            logger.warn('Cannot import %s. Ignore it for now.' % job_class_package)
            continue

        for dir_path in package.__path__:
            files = glob.glob(os.path.join(dir_path, '*.py'))
            for file in files:
                filename = os.path.basename(file)
                if filename == '__init__.py':
                    continue
                module_name = filename[:-3]
                job_module = importlib.import_module('%s.%s' % (job_class_package, module_name))
                for property in dir(job_module):
                    module_property = getattr(job_module, property)
                    try:
                        if issubclass(module_property, job.JobBase):
                            results.append(module_property.meta_info())
                    except TypeError:
                        pass
    return results
