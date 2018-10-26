"""Base class to represent datastore."""

import dateutil.parser
import dateutil.tz

from apscheduler.jobstores import sqlalchemy as sched_sqlalchemy
from sqlalchemy import select
from sqlalchemy import desc

from ndscheduler import constants
from ndscheduler import settings
from ndscheduler import utils
from ndscheduler.core.datastore import tables


class DatastoreBase(sched_sqlalchemy.SQLAlchemyJobStore):

    instance = None

    @classmethod
    def get_instance(cls):
        if not cls.instance:
            cls.instance = cls(url=cls.get_db_url(),
                               tablename=settings.JOBS_TABLENAME)
            tables.METADATA.create_all(cls.instance.engine)
            cls.instance.jobs_t.create(cls.instance.engine, True)
        return cls.instance

    @classmethod
    def destroy_instance(cls):
        cls.instance = None

    @classmethod
    def get_db_url(cls):
        """We can use the dict passed from settings.DATABASE_CONFIG_DICT to construct a db url.

        :return: Database url. See: http://docs.sqlalchemy.org/en/latest/core/engines.html
        :rtype: str
        """
        raise NotImplementedError('Please implement this function.')

    def add_execution(self, execution_id, job_id, state, **kwargs):
        """Insert a record of execution to database.

        :param str execution_id: Execution id.
        :param str job_id: Job id.
        :param int state: Execution state. See ndscheduler.constants.EXECUTION_*
        :param dict kwargs: Keyword arguments
        """
        execution = {
            'eid': execution_id,
            'job_id': job_id,
            'state': state
        }
        execution.update(kwargs)
        execution_insert = tables.EXECUTIONS.insert().values(**execution)
        self.engine.execute(execution_insert)

    def get_execution(self, execution_id):
        """Returns execution dict.

        :param str execution_id: Execution id.
        :return: Diction for execution info.
        :rtype: dict
        """
        selectable = select('*').where(tables.EXECUTIONS.c.eid == execution_id)
        rows = self.engine.execute(selectable)

        for row in rows:
            return self._build_execution(row)

    def update_execution(self, execution_id, **kwargs):
        """Update execution in database.

        :param str execution_id: Execution id.
        :param dict kwargs: Keyword arguments.
        """
        execution_update = tables.EXECUTIONS.update().where(
            tables.EXECUTIONS.c.eid == execution_id).values(**kwargs)
        self.engine.execute(execution_update)

    def _build_execution(self, row):
        """Return job execution info from a row of scheduler_execution table.

        :param obj row: A row instance of scheduler_execution table.
        :return: A dictionary of job execution info.
        :rtype: dict
        """
        # To avoid circular import

        return_json = {
            'execution_id': row.eid,
            'state': constants.EXECUTION_STATUS_DICT[row.state],
            'hostname': row.hostname,
            'pid': row.pid,
            'task_id': row.task_id,
            'description': row.description,
            'result': row.result,
            'scheduled_time': self.get_time_isoformat_from_db(row.scheduled_time),
            'updated_time': self.get_time_isoformat_from_db(row.updated_time)}
        job = self.lookup_job(row.job_id)
        if job:
            return_json['job'] = {
                'job_id': job.id,
                'name': job.name,
                'task_name': utils.get_job_name(job),
                'pub_args': utils.get_job_args(job)}
            return_json['job'].update(utils.get_cron_strings(job))
        return return_json

    def get_time_isoformat_from_db(self, time_object):
        """Convert time object from database to iso 8601 format.

        :param object time_object: a time object from database, which is different on different
            databases. Subclass of this class for specific database has to override this function.
        :return: iso8601 format string
        :rtype: str
        """
        return time_object.isoformat()

    def get_executions(self, time_range_start, time_range_end):
        """Returns info for multiple job executions.

        :param str time_range_start: ISO format for time range starting point.
        :param str time_range_end: ISO for time range ending point.
        :return: A dictionary of multiple execution info, e.g.,
            {
                'executions': [...]
            }

            Sorted by updated_time.
        :rtype: dict
        """
        utc = dateutil.tz.gettz('UTC')
        start_time = dateutil.parser.parse(time_range_start).replace(tzinfo=utc)
        end_time = dateutil.parser.parse(time_range_end).replace(tzinfo=utc)
        selectable = select('*').where(
            tables.EXECUTIONS.c.scheduled_time.between(
                start_time, end_time)).order_by(desc(tables.EXECUTIONS.c.updated_time))

        rows = self.engine.execute(selectable)

        return_json = {
            'executions': [self._build_execution(row) for row in rows]}

        return return_json

    def add_audit_log(self, job_id, job_name, event, user='', description='', **kwargs):
        """Insert an audito log.

        :param str job_id: string for job id.
        :param str job_name: string for job name.
        :param int event: integer for an event.
        :param str user: string for user name.
        :param str description: string for additional info for this event.
            It'll store old job info for modified & delete operations.
        """
        audit_log = {
            'job_id': job_id,
            'job_name': job_name,
            'event': event,
            'user': user,
            'description': description,
        }
        log_insert = tables.AUDIT_LOGS.insert().values(**audit_log)
        self.engine.execute(log_insert)

    def get_audit_logs(self, time_range_start, time_range_end):
        """Returns a list of audit logs.

        :param str time_range_start: ISO format for time range starting point.
        :param str time_range_end: ISO for time range ending point.
        :return: A dictionary of multiple audit logs, e.g.,
            {
                'logs': [
                    {
                        'job_id': ...
                        'event': ...
                        'user': ...
                        'description': ...
                    }
                ]
            }

            Sorted by created_time.
        :rtype: dict
        """
        utc = dateutil.tz.gettz('UTC')
        start_time = dateutil.parser.parse(time_range_start).replace(tzinfo=utc)
        end_time = dateutil.parser.parse(time_range_end).replace(tzinfo=utc)
        selectable = select('*').where(
            tables.AUDIT_LOGS.c.created_time.between(
                start_time, end_time)).order_by(desc(tables.AUDIT_LOGS.c.created_time))

        rows = self.engine.execute(selectable)

        return_json = {
            'logs': [self._build_audit_log(row) for row in rows]}

        return return_json

    def _build_audit_log(self, row):
        """Return audit_log from a row of scheduler_auditlog table.

        :param obj row: A row instance of scheduler_auditlog table.
        :return: A dictionary of audit log.
        :rtype: dict
        """
        return_dict = {
            'job_id': row.job_id,
            'job_name': row.job_name,
            'event': constants.AUDIT_LOG_DICT[row.event],
            'user': row.user,
            'created_time': self.get_time_isoformat_from_db(row.created_time),
            'description': row.description}
        return return_dict
