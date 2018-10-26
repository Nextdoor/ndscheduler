"""Unit tests for jobs endpoint."""

import json

import tornado.testing

from ndscheduler import utils
from ndscheduler.core import scheduler_manager
from ndscheduler.server import server
from ndscheduler.server.handlers import jobs


def mock_get_jobs_yield(self):
    return_json = self._get_jobs()
    self.finish(return_json)


def mock_get_job_yield(self, job_id):
    return_json = self._get_job(job_id)
    self.finish(return_json)


def mock_delete_job_yield(self, job_id):
    self._delete_job(job_id)


def mock_modify_job_yield(self, job_id):
    self._modify_job(job_id)


class JobsTest(tornado.testing.AsyncHTTPTestCase):

    def setUp(self, *args, **kwargs):
        super(JobsTest, self).setUp(*args, **kwargs)

        self.server.start_scheduler()
        self.JOBS_URL = '/api/v1/jobs'
        self.old_get_jobs_yield = jobs.Handler.get_jobs_yield
        self.old_get_job_yield = jobs.Handler.get_job_yield
        self.old_delete_job_yield = jobs.Handler.delete_job_yield
        self.old_modify_job_yield = jobs.Handler.modify_job_yield

        jobs.Handler.get_jobs_yield = mock_get_jobs_yield
        jobs.Handler.get_job_yield = mock_get_job_yield
        jobs.Handler.delete_job_yield = mock_delete_job_yield
        jobs.Handler.modify_job_yield = mock_modify_job_yield

    def tearDown(self, *args, **kwargs):
        self.server.stop_scheduler()
        jobs.Handler.get_jobs_yield = self.old_get_jobs_yield
        jobs.Handler.get_job_yield = self.old_get_job_yield
        jobs.Handler.delete_job_yield = self.old_delete_job_yield
        jobs.Handler.modify_job_yield = self.old_modify_job_yield

        super(JobsTest, self).tearDown(*args, **kwargs)

    def get_app(self):
        """This is required by tornado.testing."""
        # Shouldn't use singleton here. Or the test will reuse IOLoop and cause
        #   RuntimeError: IOLoop is closing
        self.scheduler = scheduler_manager.SchedulerManager()
        self.server = server.SchedulerServer(self.scheduler)
        return self.server.application

    def test_add_job_success(self):
        headers = {'Content-Type': 'application/json; charset=UTF-8'}
        data = {
            'job_class_string': 'hello.world',
            'name': 'hello world job',
            'minute': '*/5'}
        response = self.fetch(self.JOBS_URL, method='POST', headers=headers,
                              body=json.dumps(data))
        return_info = json.loads(response.body.decode())
        self.assertTrue('job_id' in return_info)
        self.assertEquals(len(return_info['job_id']), 32)
        job = self.scheduler.get_job(return_info['job_id'])
        self.assertEqual(job.name, data['name'])

    def test_add_job_failed(self):
        headers = {'Content-Type': 'application/json; charset=UTF-8'}
        data = {
            'job_class_string': 'hello.world',
            'name': 'hello world job'}
        response = self.fetch(self.JOBS_URL, method='POST', headers=headers,
                              body=json.dumps(data))
        self.assertEquals(response.code, 400)

        data = {
            'job_class_string': 'hello.world',
            'minute': '*/5'}
        response = self.fetch(self.JOBS_URL, method='POST', headers=headers,
                              body=json.dumps(data))
        self.assertEquals(response.code, 400)

    def test_pause_resume_job(self):
        headers = {'Content-Type': 'application/json; charset=UTF-8'}
        data = {
            'job_class_string': 'hello.world',
            'name': 'hello world job',
            'minute': '*/5'}
        response = self.fetch(self.JOBS_URL, method='POST', headers=headers,
                              body=json.dumps(data))
        return_info = json.loads(response.body.decode())
        self.assertTrue('job_id' in return_info)
        self.assertEquals(len(return_info['job_id']), 32)

        response = self.fetch(self.JOBS_URL + '/' + return_info['job_id'],
                              method='PATCH', body='{}')
        self.assertEquals(response.code, 200)

        response = self.fetch(self.JOBS_URL + '/' + return_info['job_id'], method='OPTIONS')
        self.assertEquals(response.code, 200)

    def test_get_jobs(self):
        headers = {'Content-Type': 'application/json; charset=UTF-8'}
        data = {
            'job_class_string': 'hello.world',
            'name': 'hello world job',
            'minute': '*/5'}
        response = self.fetch(self.JOBS_URL, method='POST', headers=headers,
                              body=json.dumps(data))
        return_info = json.loads(response.body.decode())
        self.assertTrue('job_id' in return_info)
        self.assertEquals(len(return_info['job_id']), 32)

        response = self.fetch(self.JOBS_URL + '?sync=true')
        return_info = json.loads(response.body.decode())
        self.assertEquals(len(return_info['jobs']), 1)
        job = return_info['jobs'][0]
        self.assertEquals(job['job_class_string'], data['job_class_string'])
        self.assertEquals(job['name'], data['name'])
        self.assertEquals(job['minute'], data['minute'])

    def test_delete_job(self):
        headers = {'Content-Type': 'application/json; charset=UTF-8'}
        data = {
            'job_class_string': 'hello.world',
            'name': 'hello world job',
            'minute': '*/5'}
        response = self.fetch(self.JOBS_URL, method='POST', headers=headers,
                              body=json.dumps(data))
        return_info = json.loads(response.body.decode())
        self.assertTrue('job_id' in return_info)
        self.assertEquals(len(return_info['job_id']), 32)

        response = self.fetch(self.JOBS_URL + '/' + return_info['job_id'] + '?sync=true',
                              method='DELETE')
        self.assertEquals(response.code, 200)

        response = self.fetch(self.JOBS_URL + '?sync=true')
        return_info = json.loads(response.body.decode())
        self.assertEquals(len(return_info['jobs']), 0)

    def test_modify_job(self):
        headers = {'Content-Type': 'application/json; charset=UTF-8'}
        data = {
            'job_class_string': 'hello.world',
            'name': 'hello world job',
            'minute': '*/5'}
        response = self.fetch(self.JOBS_URL, method='POST', headers=headers,
                              body=json.dumps(data))
        return_info = json.loads(response.body.decode())
        self.assertTrue('job_id' in return_info)
        self.assertEquals(len(return_info['job_id']), 32)
        job = self.scheduler.get_job(return_info['job_id'])
        self.assertEquals(utils.get_job_name(job), data['job_class_string'])
        self.assertEquals(job.name, data['name'])

        headers = {'Content-Type': 'application/json; charset=UTF-8'}
        data = {
            'job_class_string': 'hello.world!!!!',
            'name': 'hello world job~~~~',
            'minute': '*/59'}
        response = self.fetch(self.JOBS_URL + '/' + return_info['job_id'] + '?sync=true',
                              method='PUT', headers=headers, body=json.dumps(data))
        self.assertEquals(response.code, 200)
        job = self.scheduler.get_job(return_info['job_id'])
        self.assertEquals(utils.get_job_name(job), data['job_class_string'])
        self.assertEquals(job.name, data['name'])
