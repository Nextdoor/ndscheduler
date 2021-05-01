"""Some convenient utils functions."""

import importlib
import logging
import glob
import os

from ndscheduler import settings

logger = logging.getLogger(__name__)


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
    from ndscheduler.corescheduler import job

    results = []
    for job_class_package in settings.JOB_CLASS_PACKAGES:
        try:
            package = importlib.import_module(job_class_package)
        except ImportError:
            logger.warn("Cannot import %s. Ignore it for now." % job_class_package)
            continue

        for dir_path in package.__path__:
            files = glob.glob(os.path.join(dir_path, "*.py"))
            for file in files:
                filename = os.path.basename(file)
                if filename == "__init__.py":
                    continue
                module_name = filename[:-3]
                job_module = importlib.import_module("%s.%s" % (job_class_package, module_name))
                for property in dir(job_module):
                    module_property = getattr(job_module, property)
                    try:
                        if issubclass(module_property, job.JobBase):
                            results.append(module_property.meta_info())
                    except TypeError:
                        pass
    return results
