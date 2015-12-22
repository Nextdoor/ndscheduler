"""Handler for executions endpoint."""

from datetime import datetime
from datetime import timedelta

import tornado.web
import tornado.gen

from ndscheduler import constants
from ndscheduler import utils
from ndscheduler.core.scheduler import base as scheduler_base
from ndscheduler.server.handlers import base


class Handler(base.BaseHandler):

    def _get_execution(self, execution_id):
        """Returns a dictionary of a job execution info.

        This is a blocking operation.

        :param str execution_id: Execution id.

        :return: If success, a dictionary of a job execution info; otherwise, a dictionary
            of error message.
        :rtype: dict
        """
        execution = self.datastore.get_execution(execution_id)
        if not execution:
            self.set_status(400)
            return {'error': 'Execution not found: %s' % execution_id}
        return execution

    @tornado.concurrent.run_on_executor
    def get_execution(self, execution_id):
        """Wrapper for _get_execution() to run on threaded executor.

        :param str execution_id: Execution id.

        :return: Job execution info.
        :rtype: str
        """
        return self._get_execution(execution_id)

    @tornado.gen.engine
    def get_execution_yield(self, execution_id):
        """Wrapper for get_execution to run in async mode

        :param str execution_id: Execution id.
        """
        return_json = yield self.get_execution(execution_id)
        self.finish(return_json)

    def _get_executions(self):
        """Returns a dictionary of executions in a specific time range.

        This is a blocking operation.

        :return: executions info.
        :rtype: dict
        """

        now = datetime.utcnow()
        time_range_end = self.get_argument('time_range_end', now.isoformat())
        ten_minutes_ago = now - timedelta(minutes=10)
        time_range_start = self.get_argument('time_range_start', ten_minutes_ago.isoformat())

        executions = self.datastore.get_executions(time_range_start, time_range_end)
        return executions

    @tornado.concurrent.run_on_executor
    def get_executions(self):
        """Wrapper for _get_executions to run on threaded executor.

        :return: executions info.
        :rtype: dict
        """
        return self._get_executions()

    @tornado.gen.engine
    def get_executions_yield(self):
        """Wrapper for get_executions to run in async mode."""
        return_json = yield self.get_executions()
        self.finish(return_json)

    @tornado.web.removeslash
    @tornado.web.asynchronous
    @tornado.gen.engine
    def get(self, execution_id=None):
        """Returns a execution or multiple executions.

        Handles two endpoints:
            GET /api/v1/executions                 (when execution_id == None)
                It takes two query string parameters:
                - time_range_end - unix epoch timestamp. Default: now
                - time_range_start - unix epoch timestamp. Default: 10 minutes ago.
                These two parameters limit the executions to return:
                time_range_start <= execution.scheduled_time <= time_range_end

            GET /api/v1/executions/{execution_id}  (when execution_id != None)

        :param str execution_id: Execution id.
        """
        if execution_id is None:
            self.get_executions_yield()
        else:
            self.get_execution_yield(execution_id)

    def _run_job(self, job_id):
        """Kicks off a job.

        :param str job_id: Job id.

        :return: A dictionary with the only field of execution_id.
        :rtype: dict
        """

        job = self.scheduler_manager.get_job(job_id)
        if not job:
            self.set_status(400)
            return {'error': 'Job not found: %s' % job_id}
        job_name = utils.get_job_name(job)
        args = utils.get_job_args(job)
        kwargs = job.kwargs
        execution_id = scheduler_base.SingletonScheduler.run_job(job_name,
                                                                 job_id, *args, **kwargs)

        # Audit log
        self.datastore.add_audit_log(job_id, job.name, constants.AUDIT_LOG_CUSTOM_RUN,
                                     self.username, execution_id)

        response = {
            'execution_id': execution_id}
        return response

    @tornado.concurrent.run_on_executor
    def run_job(self, job_id):
        """Wrapper for _run_job() to run on threaded executor.

        :param str job_id: String for a job id.

        :return: A dictionary with the only field of execution_id.
        :rtype: dict
        """
        return self._run_job(job_id)

    @tornado.gen.engine
    def run_job_yield(self, job_id):
        """Wrapper for run_job to run in async mode.

        :param str job_id:
        :return:
        """
        return_json = yield self.run_job(job_id)
        self.finish(return_json)

    @tornado.web.removeslash
    @tornado.web.asynchronous
    @tornado.gen.engine
    def post(self, job_id):
        """Runs a job.

        Handles an endpoint:
            POST /api/v1/executions

        Args:
            job_id: String for job id.
        """
        self.run_job_yield(job_id)

    @tornado.web.removeslash
    def delete(self, job_id):
        """Stops a job execution.

        Handles an endpoint:
            POST /api/v1/executions
        """
        raise tornado.web.HTTPError(501, 'Not implemented yet.')
