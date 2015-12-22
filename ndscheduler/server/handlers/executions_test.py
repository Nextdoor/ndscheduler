"""Unit tests for executions endpoint."""

import datetime
import json

import tornado.testing

from ndscheduler import constants
from ndscheduler.core import scheduler_manager
from ndscheduler.server import server
from ndscheduler.server.handlers import executions


def mock_get_executions_yield(self):
    return_json = self._get_executions()
    self.finish(return_json)


def mock_get_execution_yield(self, execution_id):
    return_json = self._get_execution(execution_id)
    self.finish(return_json)


class ExecutionsTest(tornado.testing.AsyncHTTPTestCase):

    def setUp(self, *args, **kwargs):
        super(ExecutionsTest, self).setUp(*args, **kwargs)
        self.scheduler.start()
        self.EXECUTIONS_URL = '/api/v1/executions'
        self.old_get_executions_yield = executions.Handler.get_executions_yield
        self.old_get_execution_yield = executions.Handler.get_execution_yield
        executions.Handler.get_executions_yield = mock_get_executions_yield
        executions.Handler.get_execution_yield = mock_get_execution_yield

    def tearDown(self, *args, **kwargs):
        self.scheduler.stop()
        executions.Handler.get_executions_yield = self.old_get_executions_yield
        executions.Handler.get_execution_yield = self.old_get_execution_yield
        super(ExecutionsTest, self).tearDown(*args, **kwargs)

    def get_app(self):
        # Shouldn't use singleton here. Or the test will reuse IOLoop and cause
        #   RuntimeError: IOLoop is closing
        self.scheduler = scheduler_manager.SchedulerManager()
        return server.SchedulerServer(self.scheduler).application

    def test_get_execution(self):
        datastore = self.scheduler.get_datastore()
        execution1 = {
            'eid': '1234',
            'job_id': '5678',
            'state': constants.EXECUTION_STATUS_SCHEDULED
        }
        datastore.add_execution(execution1['eid'], execution1['job_id'], execution1['state'])
        response = self.fetch(self.EXECUTIONS_URL + '/%s?sync=true' % execution1['eid'])
        return_info = json.loads(response.body)
        self.assertEquals(return_info['execution_id'], execution1['eid'])
        self.assertEquals(return_info['state'],
                          constants.EXECUTION_STATUS_DICT[execution1['state']])

    def test_get_execution1(self):
        datastore = self.scheduler.get_datastore()
        execution1 = {
            'eid': '1234',
            'job_id': '5678',
            'state': constants.EXECUTION_STATUS_SCHEDULED,
            'scheduled_time': datetime.datetime.utcnow()
        }
        datastore.add_execution(execution1['eid'], execution1['job_id'], execution1['state'],
                                scheduled_time=execution1['scheduled_time'])
        two_minutes_later = execution1['scheduled_time'] + datetime.timedelta(minutes=2)
        response = self.fetch(self.EXECUTIONS_URL + '?time_range_end=%s' % (
            two_minutes_later.isoformat()))
        return_info = json.loads(response.body)
        self.assertEquals(return_info['executions'][0]['execution_id'], execution1['eid'])
