"""Unit tests for BaseScheduler class."""

import unittest

import mock

from ndscheduler.corescheduler.core.base import BaseScheduler
from ndscheduler.corescheduler.datastore.providers.sqlite import DatastoreSqlite


class BaseSchedulerTest(unittest.TestCase):
    def test_is_okay_to_run(self):
        with mock.patch(("ndscheduler.corescheduler.core.base." "BaseScheduler.is_okay_to_run")) as mock_should_run:
            mock_should_run.return_value = True
            job_stores = {"default": DatastoreSqlite.get_instance()}
            dcp = "ndscheduler.corescheduler.datastore.providers.sqlite.DatastoreSqlite"
            sched = BaseScheduler(dcp, jobstores=job_stores)
            self.assertNotEqual(sched._process_jobs(), sched.DEFAULT_WAIT_SECONDS)

    def test_is_not_okay_to_run(self):
        with mock.patch(("ndscheduler.corescheduler.core.base." "BaseScheduler.is_okay_to_run")) as mock_should_run:
            mock_should_run.return_value = False
            job_stores = {"default": DatastoreSqlite.get_instance()}
            dcp = "ndscheduler.corescheduler.datastore.providers.sqlite.DatastoreSqlite"
            sched = BaseScheduler(dcp, jobstores=job_stores)
            self.assertEqual(sched._process_jobs(), sched.DEFAULT_WAIT_SECONDS)
