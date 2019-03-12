"""Unit tests for DatastoreBase."""

import datetime
import unittest

from ndscheduler import constants
from ndscheduler.core.datastore.providers import base
from apscheduler.schedulers.blocking import BlockingScheduler

class SimpleDatastore(base.DatastoreBase):

    @classmethod
    def get_db_url(cls):
        return 'sqlite:///'

    def get_time_isoformat_from_db(self, time_object):
        return time_object


class DatastoreBaseTest(unittest.TestCase):

    def setUp(self):
        fake_scheduler = BlockingScheduler()
        self.store = SimpleDatastore.get_instance()
        self.store.start(fake_scheduler, None)

    def test_add_execution_get_execution(self):
        eid = '12345'
        job_id = '321'
        self.store.add_execution(eid, job_id, state=constants.EXECUTION_STATUS_SCHEDULED)
        execution = self.store.get_execution(eid)
        self.assertEqual(execution['execution_id'], eid)

    def test_update_execution_get_execution(self):
        eid = '12346'
        job_id = '321'
        self.store.add_execution(eid, job_id, state=constants.EXECUTION_STATUS_SCHEDULED)
        self.store.update_execution(eid, state=constants.EXECUTION_STATUS_RUNNING)
        execution = self.store.get_execution(eid)
        self.assertEqual(execution['execution_id'], eid)
        self.assertEqual(execution['state'],
                         constants.EXECUTION_STATUS_DICT[constants.EXECUTION_STATUS_RUNNING])

    def test_get_executions_by_time_interval(self):
        now = datetime.datetime.now()
        start_time = (now + datetime.timedelta(minutes=20)).isoformat()
        end_time = (now + datetime.timedelta(minutes=100)).isoformat()
        self.store.add_execution('12', '34', state=constants.EXECUTION_STATUS_SCHEDULED,
                                 scheduled_time=now + datetime.timedelta(minutes=5))
        self.store.add_execution('13', '34', state=constants.EXECUTION_STATUS_SCHEDULED,
                                 scheduled_time=now + datetime.timedelta(minutes=50))
        self.store.add_execution('14', '34', state=constants.EXECUTION_STATUS_SCHEDULED,
                                 scheduled_time=now + datetime.timedelta(minutes=70))
        self.store.add_execution('15', '34', state=constants.EXECUTION_STATUS_SCHEDULED,
                                 scheduled_time=now + datetime.timedelta(minutes=120))
        executions = self.store.get_executions(start_time, end_time)
        self.assertEqual(len(executions['executions']), 2)

    def test_add_aduit_log_get_audit_logs(self):
        job_id = '234'
        job_name = 'asdfs'
        event = constants.AUDIT_LOG_ADDED
        user = 'aa'
        description = 'hihi'

        self.store.add_audit_log(job_id, job_name, event, user, description)

        now = datetime.datetime.utcnow()
        five_min_ago = now - datetime.timedelta(minutes=5)

        logs = self.store.get_audit_logs(five_min_ago.isoformat(), now.isoformat())
        self.assertEqual(len(logs['logs']), 1)
