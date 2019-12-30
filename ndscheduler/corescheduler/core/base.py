"""Ensure there's only one scheduler instancing running."""

import json

from apscheduler.schedulers import tornado as apscheduler_tornado

from ndscheduler.corescheduler import constants
from ndscheduler.corescheduler import utils
from ndscheduler.corescheduler.job import JobBase


class BaseScheduler (apscheduler_tornado.TornadoScheduler):
    """It's a scheduler instance."""

    # Seconds to wake up to see if it's okay to run.
    DEFAULT_WAIT_SECONDS = 60

    def __init__(self, datastore_class_path, *args, **kwargs):
        self.datastore_class_path = datastore_class_path
        super(BaseScheduler, self).__init__(*args, **kwargs)

    @classmethod
    def is_okay_to_run(cls, datastore):
        """Determine if it's okay to schedule jobs.
        Could override this function to dynamically decide whether to run jobs by current process.
        Typically, we try to avoid running multiple scheduler processes that schedule same jobs.
        :param DatastoreBase datastore: a DatastoreBase instance.
        :return: if it's okay to run jobs, returns True; otherwise, False.
        :rtype: bool
        """
        return True

    @classmethod
    def run_job(cls, job_class_path, job_id, db_class_path, db_config,
                db_tablenames, *args, **kwargs):
        """
        :param str job_class_path: String for job class, e.g., 'myscheduler.jobs.a_job.NiceJob'
        :param str job_id: Job id
        :param str db_class_path: String for datstore class, e.g. 'datastores.DatastoreSqlite'
        :param dict db_config: dictionary containing values for db connection
        :param dict db_tablenames: dictionary containing the names for the jobs,
        executions, or audit logs table
        :param args: List of args provided to the job class to be run
        :param kwargs: Keyword arguments
        :return: string execution id
        """
        execution_id = utils.generate_uuid()
        datastore = utils.get_datastore_instance(db_class_path, db_config, db_tablenames)
        datastore.add_execution(execution_id, job_id,
                                constants.EXECUTION_STATUS_SCHEDULED,
                                description=JobBase.get_scheduled_description())
        try:
            job_class = utils.import_from_path(job_class_path)
            datastore.update_execution(execution_id, state=constants.EXECUTION_STATUS_SCHEDULED,
                                       description=job_class.get_scheduled_description())
            cls.run_scheduler_job(job_class, job_id, execution_id, datastore, *args, **kwargs)
        except Exception:
            datastore.update_execution(execution_id,
                                       state=constants.EXECUTION_STATUS_SCHEDULED_ERROR,
                                       description=JobBase.get_scheduled_error_description(),
                                       result=JobBase.get_scheduled_error_result()
                                       )
            return None
        return execution_id

    @classmethod
    def pre_run(cls, job_class, job_id, execution_id, *args, **kwargs):
        """Do any preprocessing before running the job.
        Override this function for your own implementation.
        :param JobBase job_class: Instance of job class
        :param str job_id: Job id
        :param str execution_id: Execution id
        :param args: List of args
        :param kwargs: Keyword Arguments
        """
        pass

    @classmethod
    def post_run(cls, job_class, job_id, execution_id, result_json, *args, **kwargs):
        """Do any postprocessing after running the job.
        Override this function for your own implementation.
        :param JobBase job_class: Instance of job class
        :param str job_id: Job id
        :param str execution_id: Execution id
        :param str result_json: JSON result from job run
        :param args: List of args
        :param kwargs: Keyword Arguments
        """
        pass

    @classmethod
    def run_scheduler_job(cls, job_class, job_id, execution_id, datastore, *args, **kwargs):
        """Run a job.
        :param JobBase job_class: An instance of the job to run, e.g. myscheduler.jobs.a_job.NiceJob
        :param str job_id: Job id
        :param str execution_id: Execution id
        :param DatastoreBase datastore: a datastore instance
        :param args: List of args provided to the job class to be run
        :param kwargs: Keyword arguments
        """
        cls.pre_run(job_class, job_id, execution_id, *args, **kwargs)
        try:
            datastore.update_execution(execution_id, state=constants.EXECUTION_STATUS_RUNNING,
                                       hostname=utils.get_hostname(), pid=utils.get_pid(),
                                       description=job_class.get_running_description())
            result = job_class.run_job(job_id, execution_id, *args, **kwargs)
            result_json = json.dumps(result, indent=4, sort_keys=True)
            datastore.update_execution(execution_id, state=constants.EXECUTION_STATUS_SUCCEEDED,
                                       description=job_class.get_succeeded_description(result),
                                       result=result_json)
            cls.post_run(job_class, job_id, execution_id, result_json, *args, **kwargs)
        except Exception:
            datastore.update_execution(execution_id,
                                       state=constants.EXECUTION_STATUS_FAILED,
                                       description=job_class.get_failed_description(),
                                       result=job_class.get_failed_result())

    def add_scheduler_job(self, job_class_string, name, pub_args=None,
                          month=None, day_of_week=None, day=None,
                          hour=None, minute=None, **kwargs):
        """Add a job. Job information will be persistent in postgres.
        This is a NON-BLOCKING operation, as internally, apscheduler calls wakeup()
        that is async.
        :param str job_class_string: String for job class, e.g., myscheduler.jobs.a_job.NiceJob
        :param str name: String for job name, e.g., Check Melissa job.
        :param list pub_args: List for arguments passed to publish method of a task.
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
        datastore = self._lookup_jobstore('default')
        arguments = [job_class_string, job_id, self.datastore_class_path,
                     datastore.db_config, datastore.table_names]
        arguments.extend(pub_args)

        self.add_job(self.run_job,
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
        :param kwargs: keyword arguments, including:
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

        cron_keywords = ['month', 'day', 'hour', 'minute', 'day_of_week']
        trigger_kwargs = {}
        for cron_key in cron_keywords:
            if cron_key in kwargs:
                trigger_kwargs[cron_key] = kwargs[cron_key]
                del kwargs[cron_key]

        if trigger_kwargs:
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
        """
        :return: Integer for seconds to wake up in next processing cycle.
            If it isn't currently ok to run, it'll just return
            DEFAULT_WAIT_SECONDS, so it'll be able to check again after that.
        :rtype: int
        """

        if self.is_okay_to_run(self._lookup_jobstore('default')):
            return super(apscheduler_tornado.TornadoScheduler, self)._process_jobs()
        else:
            return self.DEFAULT_WAIT_SECONDS
