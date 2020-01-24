"""Handler for jobs endpoint."""

import json

import tornado.concurrent
import tornado.gen
import tornado.web

import apscheduler.triggers.cron
import apscheduler.triggers.interval

from ndscheduler.corescheduler import constants
from ndscheduler.corescheduler import utils
from ndscheduler.server.handlers import base


class Handler(base.BaseHandler):

    def _get_jobs(self):
        """Returns a dictionary for all jobs info.

        It's a blocking operation.
        """
        jobs = self.scheduler_manager.get_jobs()
        return_json = []
        for job in jobs:
            return_json.append(self._build_job_dict(job))
        return {'jobs': return_json}

    def _build_job_dict(self, job):
        """Transforms apscheduler's job structure to a python dictionary.

        :param Job job: An apscheduler.job.Job instance.
        :return: dictionary for job info
        :rtype: dict
        """
        if job.next_run_time:
            next_run_time = job.next_run_time.isoformat()
        else:
            next_run_time = ''
        return_dict = {
            'job_id': job.id,
            'name': job.name,
            'next_run_time': next_run_time,
            'job_class_string': utils.get_job_name(job),
            'pub_args': utils.get_job_args(job)}

        if isinstance(job.trigger, apscheduler.triggers.cron.CronTrigger):
            return_dict["trigger"] = "cron"
            return_dict["trigger_params"] = utils.get_cron_strings(job)
        elif isinstance(job.trigger, apscheduler.triggers.interval.IntervalTrigger):
            return_dict["trigger"] = "interval"
            trigger_params = {
                'interval': job.trigger.interval.total_seconds()
            }
            return_dict["trigger_params"] = trigger_params
        else:
            return_dict["trigger"] = "unknown"
            return_dict["trigger_params"] = {}

        return return_dict

    @tornado.concurrent.run_on_executor
    def get_jobs(self):
        """Wrapper to run _get_jobs() on a thread executor.

        :return: dictionary for jobs
            A dictionary of jobs, e.g., :
            {
                jobs: [...]
            }
        :rtype: dict
        """
        return self._get_jobs()

    @tornado.gen.engine
    def get_jobs_yield(self):
        """Wrapper for get_jobs in async mode."""
        return_json = yield self.get_jobs()
        self.finish(return_json)

    def _get_job(self, job_id):
        """Returns a dictionary for a job info.

        It's a blocking operation.

        :param str job_id: Job id.

        :return: dictionary for a job
        :rtype: dict
        """
        job = self.scheduler_manager.get_job(job_id)
        if not job:
            self.set_status(400)
            return {'error': 'Job not found: %s' % job_id}
        return self._build_job_dict(job)

    @tornado.concurrent.run_on_executor
    def get_job(self, job_id):
        """Wrapper to run _get_jobs() on a thread executor.

        :param str job_id: Job id.
        :return: A dictionary of a job.
        :rtype: dict
        """
        return self._get_job(job_id)

    @tornado.gen.engine
    def get_job_yield(self, job_id):
        """Wrapper for get_job() to run in async mode.

        :param str job_id: Job id.
        """
        return_json = yield self.get_job(job_id)
        self.finish(return_json)

    @tornado.web.removeslash
    @tornado.web.asynchronous
    @tornado.gen.engine
    def get(self, job_id=None):
        """Returns a job or multiple jobs.

        Handles two endpoints:
            GET /api/v2/jobs           (when job_id == None)
            GET /api/v2/jobs/{job_id}  (when job_id != None)

        :param str job_id: String for job id.
        """
        if job_id is None:
            self.get_jobs_yield()
        else:
            self.get_job_yield(job_id)

    @tornado.web.removeslash
    def post(self):
        """Adds a job.

        add_job() is a non-blocking operation, but audit log is a blocking operation.

        Handles an endpoint:
            POST /api/v2/jobs
        """
        self._validate_post_data()

        # This is non-blocking function.
        # It returns job_id immediately.
        job_id = self.scheduler_manager.add_job(**self.json_args)

        # Blocking operation.
        self.datastore.add_audit_log(job_id, self.json_args['name'],
                                     constants.AUDIT_LOG_ADDED, user=self.username)

        response = {
            'job_id': job_id}
        self.set_status(201)
        self.write(response)

    def _delete_job(self, job_id):
        """Deletes a job.

        It's a blocking operation.

        :param str job_id: String for a job id.
        """

        job = self._get_job(job_id)

        self.scheduler_manager.remove_job(job_id)

        self.datastore.add_audit_log(job_id, job['name'], constants.AUDIT_LOG_DELETED,
                                     user=self.username, description=json.dumps(job))

    @tornado.concurrent.run_on_executor
    def delete_job(self, job_id):
        """Wrapper for _delete_job() to run on a threaded executor."""
        self._delete_job(job_id)

    @tornado.gen.engine
    def delete_job_yield(self, job_id):
        yield self.delete_job(job_id)

    @tornado.web.removeslash
    @tornado.web.asynchronous
    @tornado.gen.engine
    def delete(self, job_id):
        """Deletes a job.

        Handles an endpoint:
            DELETE /api/v2/jobs/{job_id}

        :param str job_id: Job id
        """
        self.delete_job_yield(job_id)

        response = {
            'job_id': job_id}
        self.set_status(200)
        self.finish(response)

    def _generate_description_for_item(self, item_name, old_item, new_item):
        """Returns a diff for one field of a job.

        :param str item_name: Description of the item
        :param old_item: Item of old job.
        :param new_item: Item of modified job.

        :return: String for description.
        :rtype: str
        """
        if old_item != new_item:
            return ('<b>%s</b>: <font color="red">%s</font> =>'
                    ' <font color="green">%s</font><br>') % (item_name, old_item, new_item)
        return ''

    def _generate_trigger_description(self, trigger, trigger_params):
        """Returns a trigger description for the job

        :param str trigger: Trigger of the job
        :param dict trigger_params: Parameters of the trigger

        :return: Description of the trigger
        :rtype: str
        """


        if trigger == 'cron':
            descr = f"{trigger}: minute=\"{trigger_params['minute']}\" "\
                    f"hour=\"{trigger_params['hour']}\" " \
                    f"day=\"{trigger_params['day']}\" " \
                    f"month=\"{trigger_params['month']}\" " \
                    f"minute=\"{trigger_params['day_of_week']}\""
        elif trigger == 'interval':
            descr = f"{trigger}: interval=\"{trigger_params['interval']}\""
        else:
            descr = "unknown"

        return descr

    def _generate_pubargs_description(self, pub_args):
        """Generates description text for pub_args.

        :param pub_args: List or tuple of pup_args.

        :return: String description of pup_args.
        :rtype: str
        """

        if isinstance(pub_args, tuple):
            return str(list(pub_args))
        else:
            return str(pub_args)


    def _generate_description_for_modify(self, old_job, new_job):
        """Generates description text after modifying a job.

        :param dict old_job: Dict for old job.
        :param dict new_job: Dict for new job after modification.

        :return: String for description.
        :rtype: str
        """

        description = self._generate_description_for_item('Name', old_job['name'], new_job['name'])
        description += self._generate_description_for_item('Job Class', old_job['job_class_string'], new_job['job_class_string'])
        description += self._generate_description_for_item('Trigger',
            self._generate_trigger_description(old_job['trigger'], old_job['trigger_params']),
            self._generate_trigger_description(new_job['trigger'], new_job['trigger_params']))
        description += self._generate_description_for_item('Arguments',
            self._generate_pubargs_description(old_job['pub_args']),
            self._generate_pubargs_description(new_job['pub_args']))

        return description

    def _modify_job(self, job_id):
        """Modifies a job's info.

        This is a blocking operation.

        :param str job_id: String for a job id.
        """
        old_job = self._get_job(job_id)

        self.scheduler_manager.modify_job(job_id, **self.json_args)

        job = self._get_job(job_id)

        # Audit log
        self.datastore.add_audit_log(
            job_id, job['name'], constants.AUDIT_LOG_MODIFIED,
            user=self.username, description=self._generate_description_for_modify(old_job, job))

    @tornado.concurrent.run_on_executor
    def modify_job(self, job_id):
        """Wrapper for _modify_job() to run on threaded executor.

        :param str job_id: String for a job id.
        """
        self._modify_job(job_id)

    @tornado.gen.engine
    def modify_job_yield(self, job_id):
        """Wrapper for modify_job() to run in async mode.

        :param str job_id: Job id.
        """
        yield self.modify_job(job_id)

    @tornado.web.removeslash
    @tornado.web.asynchronous
    @tornado.gen.engine
    def put(self, job_id):
        """Modifies a job.

        Handles an endpoint:
            PUT /api/v2/jobs/{job_id}

        :param str job_id: Job id.
        """
        self._validate_post_data()
        self.modify_job_yield(job_id)

        response = {
            'job_id': job_id}
        self.set_status(200)
        self.finish(response)

    @tornado.web.removeslash
    def patch(self, job_id):
        """Pauses a job.

        pause_job() is a non-blocking operation, but audit log is a blocking operation.

        Handles an endpoint:
            PATCH /api/v2/jobs/{job_id}

        :param str job_id: Job id.
        """

        # This is non-blocking function.
        # It returns job_id immediately.
        self.scheduler_manager.pause_job(job_id)

        # Blocking operation.
        job = self._get_job(job_id)

        self.datastore.add_audit_log(job_id, job['name'],
                                     constants.AUDIT_LOG_PAUSED, user=self.username)

        response = {
            'job_id': job_id}
        self.set_status(200)
        self.write(response)

    @tornado.web.removeslash
    def options(self, job_id):
        """Resumes a job.

        resume_job() is a non-blocking operation, but audit log is a blocking operation.

        Handles an endpoint:
            OPTIONS /api/v2/jobs/{job_id}

        :param str job_id: Job id.
        """

        # This is non-blocking function.
        # It returns job_id immediately.
        self.scheduler_manager.resume_job(job_id)

        # Blocking operation.
        job = self._get_job(job_id)
        self.datastore.add_audit_log(job_id, job['name'], constants.AUDIT_LOG_RESUMED,
                                     user=self.username)

        response = {
            'job_id': job_id}
        self.set_status(200)
        self.write(response)

    def _validate_post_data(self):
        """Validates POST data for adding a job.


        :return: a dictionary that serves as kwargs for Scheduler.add_job()
        :rtype: dict

        :raises: HTTPError(400: Bad arguments).
        """
        all_required_fields = ['name', 'job_class_string']
        for field in all_required_fields:
            if field not in self.json_args:
                raise tornado.web.HTTPError(400, reason='Require this parameter: %s' % field)

        #TODO better validating
        at_least_one_required_fields = ['month', 'day', 'hour', 'minute', 'day_of_week']
        valid_cron_string = False
        for field in at_least_one_required_fields:
            if field in self.json_args:
                valid_cron_string = True
                break
        #TODO ignore validating
        valid_cron_string = True

        if not valid_cron_string:
            raise tornado.web.HTTPError(400, reason=('Require at least one of following parameters:'
                                                     ' %s' % str(at_least_one_required_fields)))
