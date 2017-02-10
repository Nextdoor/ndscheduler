"""Unit tests for SingletonScheduler class."""

import mock
import unittest

from ndscheduler.core import scheduler_manager


class SingletonSchedulerTest(unittest.TestCase):

    def test_is_okay_to_run(self):
        with mock.patch(('ndscheduler.core.scheduler.base.'
                         'SingletonScheduler.is_okay_to_run')) as mock_should_run:
            mock_should_run.return_value = True
            sched = scheduler_manager.SchedulerManager().sched
            self.assertNotEqual(sched._process_jobs(), sched.DEFAULT_WAIT_SECONDS)

    def test_is_not_okay_to_run(self):
        with mock.patch(('ndscheduler.core.scheduler.base.'
                         'SingletonScheduler.is_okay_to_run')) as mock_should_run:
            mock_should_run.return_value = False
            sched = scheduler_manager.SchedulerManager().sched
            self.assertEqual(sched._process_jobs(), sched.DEFAULT_WAIT_SECONDS)
