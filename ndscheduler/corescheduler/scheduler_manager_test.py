"""Unit tests for scheduler_manager module."""

from builtins import str

import tornado.testing

from ndscheduler.corescheduler import scheduler_manager
from ndscheduler.corescheduler import utils


class SchedulerManagerTest(tornado.testing.AsyncTestCase):
    def setUp(self, *args, **kwargs):
        super(SchedulerManagerTest, self).setUp(*args, **kwargs)

        scheduler_class = 'core.base.BaseScheduler'
        datastore_class = 'datastore.providers.sqlite.DatastoreSqlite'

        self.scheduler = scheduler_manager.SchedulerManager(scheduler_class, datastore_class)
        self.scheduler.start()

    def tearDown(self, *args, **kwargs):
        self.scheduler.stop()
        super(SchedulerManagerTest, self).tearDown(*args, **kwargs)

    @tornado.testing.gen_test
    def test_add_job_get_job(self):
        task_name = 'hello.world'
        name = 'it is hello world'
        pub_args = ('1', '2', '3')
        month = '*/1'
        day_of_week = 'sat'
        day = '*/2'
        hour = '*/3'
        minute = '*/4'

        # non-blocking operation
        job_id = self.scheduler.add_job(task_name, name, pub_args, month, day_of_week, day,
                                        hour, minute, languages='en-us')

        self.assertTrue(len(job_id), 32)

        # blocking operation
        job = self.scheduler.get_job(job_id)
        self.assertEqual(self.scheduler.get_job_task_class(job), task_name)
        self.assertEqual(job.id, job_id)
        self.assertEqual(job.name, name)
        self.assertEqual(utils.get_job_args(job), pub_args)
        self.assertEqual(utils.get_job_kwargs(job), {'languages': 'en-us'})

        # Year
        self.assertEqual(str(job.trigger.fields[0]), '*')
        # Month
        self.assertEqual(str(job.trigger.fields[1]), month)
        # day of month
        self.assertEqual(str(job.trigger.fields[2]), day)
        # week
        self.assertEqual(str(job.trigger.fields[3]), '*')
        # day of week
        self.assertEqual(str(job.trigger.fields[4]), day_of_week)
        # hour
        self.assertEqual(str(job.trigger.fields[5]), hour)
        # minute
        self.assertEqual(str(job.trigger.fields[6]), minute)
        # second
        self.assertEqual(str(job.trigger.fields[7]), '0')

    @tornado.testing.gen_test
    def test_add_job_modify_job(self):
        job_class_string = 'hello.world2'
        name = 'it is hello world 2'
        pub_args = ('1', '2', '3')
        month = '*/1'
        day_of_week = 'sat'
        day = '*/2'
        hour = '*/3'
        minute = '*/4'

        # non-blocking operation
        job_id = self.scheduler.add_job(job_class_string, name, pub_args, month, day_of_week,
                                        day, hour, minute)

        self.assertTrue(len(job_id), 32)

        job_class_string = 'hello.world1234'
        args = ['5', '6', '7']
        name = 'hello world 3'
        month = '*/6'

        # non-blocking operation
        self.scheduler.modify_job(job_id, name=name, job_class_string=job_class_string,
                                  pub_args=args, month=month)

        # blocking operation
        job = self.scheduler.get_job(job_id)
        self.assertEqual(job.name, name)

        arguments = [job_class_string, job_id]
        arguments += args
        self.assertEqual(list(job.args), arguments)
        self.assertEqual(str(job.trigger.fields[1]), month)
