"""Base class for a job."""

import logging
import os
import socket

from ndscheduler import constants
from ndscheduler import utils
from ndscheduler.core import scheduler_manager

logger = logging.getLogger(__name__)


class JobBase:

    @classmethod
    def get_scheduled_description(cls):
        hostname = socket.gethostname()
        pid = os.getpid()
        return 'hostname: %s | pid: %s' % (hostname, pid)

    @classmethod
    def get_scheduled_error_description(cls):
        return utils.get_stacktrace()

    @classmethod
    def get_running_description(cls):
        hostname = socket.gethostname()
        pid = os.getpid()
        return 'hostname: %s | pid: %s' % (hostname, pid)

    @classmethod
    def get_failed_description(cls):
        return utils.get_stacktrace()

    @classmethod
    def get_succeeded_description(cls):
        hostname = socket.gethostname()
        pid = os.getpid()
        return 'hostname: %s | pid: %s' % (hostname, pid)

    @classmethod
    def run_job(cls, job_id, execution_id, *args, **kwargs):
        """Wrapper to run this job.

        It updates the execution state, i.e., running, succeeded or failed.

        :param str job_id: Job id.
        :param str execution_id: Execution id.
        :param args:
        :param kwargs:
        """
        scheduler = scheduler_manager.SchedulerManager.get_instance()
        datastore = scheduler.get_datastore()
        try:
            datastore.update_execution(execution_id, state=constants.EXECUTION_STATUS_RUNNING,
                                       hostname=socket.gethostname(), pid=os.getpid(),
                                       description=cls.get_running_description())
            cls.run(job_id, execution_id, *args, **kwargs)
            datastore.update_execution(execution_id, state=constants.EXECUTION_STATUS_SUCCEEDED,
                                       description=cls.get_succeeded_description())
        except Exception as e:
            logger.exception(e)
            datastore.update_execution(execution_id,
                                       state=constants.EXECUTION_STATUS_FAILED,
                                       description=cls.get_failed_description())

    @classmethod
    def run(cls, job_id, execution_id, *args, **kwargs):
        """The "main" function for a job.

        Any subclass has to implement this function.

        :param str job_id: Job id.
        :param str execution_id: Execution id.
        :param args:
        :param kwargs:
        :return:
        """
        raise NotImplementedError('Please implement this function')
