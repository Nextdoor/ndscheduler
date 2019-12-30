"""Ensure there's only one scheduler instancing running."""

import logging

from apscheduler.schedulers import tornado as apscheduler_tornado

from ndscheduler import constants
from ndscheduler import job
from ndscheduler import settings
from ndscheduler import utils

logger = logging.getLogger(__name__)


class SingletonScheduler (apscheduler_tornado.TornadoScheduler):
    """It's a "singleton" scheduler instance."""

    # Seconds to wake up to see if it's okay to run.
    DEFAULT_WAIT_SECONDS = 60

    @classmethod
    def is_okay_to_run(cls, database):
        """Determine if it's okay to schedule jobs.

        Could override this function to dynamically decide whether to run jobs by current process.
        Typically, we try to avoid running multiple scheduler processes that schedule same jobs.

        :param DatastoreBase database: a DatastoreBase instance.
        :return: if it's okay to run jobs, returns True; otherwise, False.
        :rtype: bool
        """
        return True

    @classmethod
    def run_job(cls, job_class_path, job_id, *args, **kwargs):
        execution_id = utils.generate_uuid()
        datastore = utils.get_datastore_instance()
        datastore.add_execution(execution_id, job_id,
                                constants.EXECUTION_STATUS_SCHEDULED,
                                description=job.JobBase.get_scheduled_description())
        try:
            job_class = utils.import_from_path(job_class_path)
            datastore.update_execution(execution_id, state=constants.EXECUTION_STATUS_SCHEDULED,
                                       description=job_class.get_scheduled_description())
            cls.run_scheduler_job(job_class, job_id, execution_id, *args, **kwargs)
        except Exception as e:
            logger.exception(e)
            datastore.update_execution(execution_id,
                                       state=constants.EXECUTION_STATUS_SCHEDULED_ERROR,
                                       description=job.JobBase.get_scheduled_error_description(),
                                       result=job.JobBase.get_scheduled_error_result()
                                       )
            return None
        return execution_id

    @classmethod
    def run_scheduler_job(cls, job_class, job_id, execution_id, *args, **kwargs):
        """Run a job.

        Override this function for your own implementation.

        :param str job_class: String for job class.
        :param str job_id: Job id.
        :param list args: List of args.
        :param dict kwargs: Keyword arguments.
        """
        job_class.run_job(job_id, execution_id, *args, **kwargs)

    def add_scheduler_job(self, job_class_string, name, pub_args=None,
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

        Returns:
            String of job id, e.g., 6bca19736d374ef2b3df23eb278b512e
        """
        if not pub_args:
            pub_args = []

        job_id = utils.generate_uuid()

        arguments = [job_class_string, job_id]
        arguments.extend(pub_args)

        scheduler_class = utils.import_from_path(settings.SCHEDULER_CLASS)
        self.add_job(scheduler_class.run_job,
                     'cron', month=month, day=day, day_of_week=day_of_week, hour=hour,
                     minute=minute, args=arguments, kwargs=kwargs, name=name, id=job_id)
        return job_id

    def add_trigger_scheduler_job(self, job_class_string, name, pub_args, trigger,
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

        Returns:
            String of job id, e.g., 6bca19736d374ef2b3df23eb278b512e
        """
        if not pub_args:
            pub_args = []

        job_id = utils.generate_uuid()

        arguments = [job_class_string, job_id]
        arguments.extend(pub_args)

        scheduler_class = utils.import_from_path(settings.SCHEDULER_CLASS)
        self.add_job(scheduler_class.run_job,   # noqa
                     trigger = trigger,         # noqa
                     args    = arguments,       # noqa
                     kwargs  = kwargs,          # noqa
                     name    = name,            # noqa
                     id      = job_id           # noqa
                 )
        return job_id

    def modify_scheduler_job(self, job_id, **kwargs):
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

        # This is a BLOCKING operation
        job = self.get_job(job_id)

        # Handle args
        if 'job_class_string' in kwargs or 'pub_args' in kwargs:
            args = list(job.args)
            if 'job_class_string' in kwargs:
                args[0] = kwargs['job_class_string']
                # 'task_name' is not an argument for modify_job.
                del kwargs['job_class_string']
            if 'pub_args' in kwargs:
                args = args[:2] + kwargs['pub_args']
                del kwargs['pub_args']
            kwargs['args'] = args

        # Handle scheduling time
        if ('month' in kwargs or 'day' in kwargs or 'hour' in kwargs or 'minute' in kwargs or
                'day_of_week' in kwargs):
            trigger_kwargs = {}
            if 'month' in kwargs:
                trigger_kwargs['month'] = kwargs['month']
                del kwargs['month']
            if 'day_of_week' in kwargs:
                trigger_kwargs['day_of_week'] = kwargs['day_of_week']
                del kwargs['day_of_week']
            if 'day' in kwargs:
                trigger_kwargs['day'] = kwargs['day']
                del kwargs['day']
            if 'hour' in kwargs:
                trigger_kwargs['hour'] = kwargs['hour']
                del kwargs['hour']
            if 'minute' in kwargs:
                trigger_kwargs['minute'] = kwargs['minute']
                del kwargs['minute']

            # This is a NON-BLOCKING operation
            job.reschedule(trigger='cron', **trigger_kwargs)

        # This is a NON-BLOCKING operation
        job.modify(**kwargs)

        # apschedule has a "bug" or "feature":
        # Whenever you modify a job, it resumes the job, no matter whether
        # the job is paused or not originally.
        # So we need to manually pause it at the end.
        if not job.next_run_time:
            job.pause()

    def _process_jobs(self):
        """Checks against zookeeper to see if it belongs to current release.

        :return: Integer for seconds to wake up in next processing cycle.
            If it doesn't belong to current release version, it'll just return
            60 seconds, so it'll be able to check again after 60 seconds.
        :rtype: int
        """

        if self.is_okay_to_run(self._lookup_jobstore('default')):
            return super(apscheduler_tornado.TornadoScheduler, self)._process_jobs()
        else:
            return self.DEFAULT_WAIT_SECONDS
