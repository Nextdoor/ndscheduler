"""Base class to represent datastore."""

import dateutil.tz
import dateutil.parser
from apscheduler.jobstores import sqlalchemy as sched_sqlalchemy
from sqlalchemy import desc, select, MetaData

from ndscheduler.corescheduler import constants
from ndscheduler.corescheduler import utils
from ndscheduler.corescheduler.datastore import tables


class DatastoreBase(sched_sqlalchemy.SQLAlchemyJobStore):

    instance = None

    @classmethod
    def get_instance(cls, db_config=None, table_names=None):
        if not cls.instance:
            cls.instance = cls(db_config, table_names)
        return cls.instance

    @classmethod
    def destroy_instance(cls):
        cls.instance = None

    def __init__(self, db_config, table_names):
        """
        :param dict db_config: dictionary containing values for db connection
        :param dict table_names: dictionary containing the names for the jobs,
        executions, or audit logs table, e.g. {
            'executions_tablename': 'scheduler_executions',
            'jobs_tablename': 'scheduler_jobs',
            'auditlogs_tablename': 'scheduler_auditlogs'
        }
        If any of these keys is not provided, the default table name is selected from constants.py
        """
        self.metadata = MetaData()
        self.table_names = table_names
        self.db_config = db_config

        executions_tablename = constants.DEFAULT_EXECUTIONS_TABLENAME
        jobs_tablename = constants.DEFAULT_JOBS_TABLENAME
        auditlogs_tablename = constants.DEFAULT_AUDIT_LOGS_TABLENAME
        if table_names:
            if 'executions_tablename' in table_names:
                executions_tablename = table_names['executions_tablename']

            if 'jobs_tablename' in table_names:
                jobs_tablename = table_names['jobs_tablename']

            if 'auditlogs_tablename' in table_names:
                auditlogs_tablename = table_names['auditlogs_tablename']

        self.executions_table = tables.get_execution_table(self.metadata, executions_tablename)
        self.auditlogs_table = tables.get_auditlogs_table(self.metadata, auditlogs_tablename)

        super(DatastoreBase, self).__init__(url=self.get_db_url(), tablename=jobs_tablename)

        self.metadata.create_all(self.engine)

    def get_db_url(self):
        """We can use the dict passed from db_config_dict to construct a db url.
        :return: Database url. See: http://docs.sqlalchemy.org/en/latest/core/engines.html
        :rtype: str
        """
        raise NotImplementedError('Please implement this function.')

    def add_execution(self, execution_id, job_id, state, **kwargs):
        """Insert a record of execution to database.
        :param str execution_id: Execution id.
        :param str job_id: Job id.
        :param int state: Execution state. See ndscheduler.constants.EXECUTION_*
        """
        execution = {
            'eid': execution_id,
            'job_id': job_id,
            'state': state
        }
        execution.update(kwargs)
        execution_insert = self.executions_table.insert().values(**execution)
        self.engine.execute(execution_insert)

    def get_execution(self, execution_id):
        """Returns execution dict.
        :param str execution_id: Execution id.
        :return: Diction for execution info.
        :rtype: dict
        """
        selectable = select('*').where(self.executions_table.c.eid == execution_id)
        rows = self.engine.execute(selectable)

        for row in rows:
            return self._build_execution(row)

    def update_execution(self, execution_id, **kwargs):
        """Update execution in database.
        :param str execution_id: Execution id.
        :param kwargs: Keyword arguments.
        """
        execution_update = self.executions_table.update().where(
            self.executions_table.c.eid == execution_id).values(**kwargs)
        self.engine.execute(execution_update)

    def _build_execution(self, row):
        """Return job execution info from a row of scheduler_execution table.
        :param obj row: A row instance of scheduler_execution table.
        :return: A dictionary of job execution info.
        :rtype: dict
        """
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
            self.executions_table.c.scheduled_time.between(
                start_time, end_time)).order_by(desc(self.executions_table.c.updated_time))

        rows = self.engine.execute(selectable)

        return_json = {
            'executions': [self._build_execution(row) for row in rows]}

        return return_json

    def add_audit_log(self, job_id, job_name, event, **kwargs):
        """Insert an audit log.
        :param str job_id: string for job id.
        :param str job_name: string for job name.
        :param int event: integer for an event.
        """
        audit_log = {
            'job_id': job_id,
            'job_name': job_name,
            'event': event
        }
        audit_log.update(kwargs)
        log_insert = self.auditlogs_table.insert().values(**audit_log)
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
            self.auditlogs_table.c.created_time.between(
                start_time, end_time)).order_by(desc(self.auditlogs_table.c.created_time))

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
