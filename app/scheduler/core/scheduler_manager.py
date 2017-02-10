"""Represents the core scheduler instance that actually schedules jobs."""


import logging

from apscheduler.executors import pool

from .. import settings
from .. import utils


logger = logging.getLogger(__name__)


class SchedulerManager:

    instance = None

    @classmethod
    def get_instance(cls):
        if not cls.instance:
            cls.instance = cls()
        return cls.instance

    def __init__(self):
        JOB_STORES = {
            'default': utils.get_datastore_instance()
        }

        JOB_DEFAULT = {
            'coalesce': settings.JOB_COALESCE,
            'misfire_grace_time': settings.JOB_MISFIRE_GRACE_SEC,
            'max_instances': settings.JOB_MAX_INSTANCES
        }

        EXECUTORS = {
            'default': pool.ThreadPoolExecutor(settings.THREAD_POOL_SIZE)
        }

        scheduler_class = utils.import_from_path(settings.SCHEDULER_CLASS)
        self.sched = scheduler_class(
            jobstores=JOB_STORES, executors=EXECUTORS, job_defaults=JOB_DEFAULT,
            logger=logger, timezone=settings.TIMEZONE)

    def get_datastore(self):
        return self.sched._lookup_jobstore('default')

    #
    # Manage the entire scheduler
    #
    def start(self):
        """Start scheduler daemon.

        This is a BLOCKING operation, as internally, apscheduler doesn't
        call wakeup() that is async.
        """
        self.sched.start()

    def stop(self):
        """Stop scheduler daemon.

        This is a BLOCKING operation, as internally, apscheduler doesn't
        call wakeup() that is async.
        """
        self.sched.shutdown()
        self.get_datastore().destroy_instance()

    #
    # Manage jobs
    #
    def add_job(self, job_class_string, name, pub_args=None,
                month=None, day_of_week=None, day=None, hour=None, minute=None,
                **kwargs):
        """Add a job. Job infomation will be persistent in postgres.

        This is a NON-BLOCKING operation, as internally, apscheduler calls wakeup()
        that is async.

        :param str job_class_string: String for job class, e.g., myscheduler.jobs.a_job.NiceJob
        :param str name: String for job name, e.g., Check Melissa job.
        :param str pub_args: List for arguments passed to publish method of a task.
        :param str month: String for month cron string, e.g., */10
        :param str day_of_week: String for day of week cron string, e.g., 1-6
        :param str day: String for day cron string, e.g., */1
        :param str hour: String for hour cron string, e.g., */2
        :param str minute: String for minute cron string, e.g., */3
        :param dict kwargs: Other keyword arguments passed to run_job function.
        :return: String of job id, e.g., 6bca19736d374ef2b3df23eb278b512e
        :rtype: str
        """
        return self.sched.add_scheduler_job(job_class_string, name, pub_args, month, day_of_week,
                                            day, hour, minute, **kwargs)

    def pause_job(self, job_id):
        """Pauses the schedule of a job.

        This is a NON-BLOCKING operation, as internally, apscheduler calls wakeup()
        that is async.

        :param str job_id: String for job id to be paused.
        """
        self.sched.pause_job(job_id)

    def get_job(self, job_id):
        """Returns an apscheduler.job.Job instance.

        This is a BLOCKING operation, as internally, apscheduler doesn't
        call wakeup() that is async.

        :param str job_id: String for job id to be returned.

        :return: An apscheduler.job.Job instance.
        :rtype: apscheduler.job.Job
        """
        return self.sched.get_job(job_id)

    def get_jobs(self):
        """Returns a list of apscheduler.job.Job instances.

        This is a BLOCKING operation, as internally, apscheduler doesn't
        call wakeup() that is async.

        :return: A list of apscheduler.job.Job instances.
        :rtype: list
        """
        return self.sched.get_jobs()

    def get_job_task_class(self, job):
        """Shortcut to get task class.

        :param Job job: Instance of apscheduler.job.Job.
        :return: String for task class of this job.
        :rtype: str
        """
        return job.args[0]

    def remove_job(self, job_id):
        """Removes a job.

        This is a BLOCKING operation, as internally, apscheduler doesn't
        call wakeup() that is async.

        :param str job_id: String for job id to be removed.
        """
        self.sched.remove_job(job_id)

    def resume_job(self, job_id):
        """Removes a job.

        This is a NON-BLOCKING operation, as internally, apscheduler calls wakeup()
        that is async.

        :param str job_id: String for job id to be removed.
        """
        self.sched.resume_job(job_id)

    def modify_job(self, job_id, **kwargs):
        """Modifies a job.

        This is a BLOCKING operation, because it calls get_job() that is blocking, even though
        reschedule() and modify() are both non-blocking.

        :param str job_id: String for job id to be modified.
        :param dict kwargs: keyword arguments, including:
            - name: String for job name
            - job_class_string: String for job class string, e.g.,
                myscheduler.jobs.a_job.NiceJob
            - pub_args: List of arguments passed to the task.
            - month: String for month cron string, e.g., */10
            - day_of_week: String for day of week cron string, e.g., 1-6
            - day: String for day cron string, e.g., */1
            - hour: String for hour cron string, e.g., */2
            - minute: String for minute cron string, e.g., */3
        """
        self.sched.modify_scheduler_job(job_id, **kwargs)
