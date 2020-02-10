"""Unit tests for scheduler_manager module."""

from builtins import str

import tornado.testing

from ndscheduler.corescheduler import scheduler_manager
from ndscheduler.corescheduler import utils


class SchedulerManagerTest(tornado.testing.AsyncTestCase):
    def setUp(self, *args, **kwargs):
        super(SchedulerManagerTest, self).setUp(*args, **kwargs)

        scheduler_class = 'ndscheduler.corescheduler.core.base.BaseScheduler'
        datastore_class = 'ndscheduler.corescheduler.datastore.providers.sqlite.DatastoreSqlite'

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
        trigger_params = dict(
            month='*/1',
            day_of_week='sat',
            day='*/2',
            hour='*/3',
            minute='*/4'
            )
        trigger = 'cron'

        # non-blocking operation
        job_id = self.scheduler.add_job(task_name, name, trigger, pub_args,
                                        trigger_params, languages='en-us')

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
        self.assertEqual(str(job.trigger.fields[1]), trigger_params['month'])
        # day of month
        self.assertEqual(str(job.trigger.fields[2]), trigger_params['day'])
        # week
        self.assertEqual(str(job.trigger.fields[3]), '*')
        # day of week
        self.assertEqual(str(job.trigger.fields[4]), trigger_params['day_of_week'])
        # hour
        self.assertEqual(str(job.trigger.fields[5]), trigger_params['hour'])
        # minute
        self.assertEqual(str(job.trigger.fields[6]), trigger_params['minute'])
        # second
        self.assertEqual(str(job.trigger.fields[7]), '0')

    @tornado.testing.gen_test
    def test_add_job_modify_job(self):
        job_class_string = 'hello.world2'
        name = 'it is hello world 2'
        pub_args = ('1', '2', '3')
        trigger_params = dict(
            month='*/1',
            day_of_week='sat',
            day='*/2',
            hour='*/3',
            minute='*/4'
            )
        trigger = 'cron'

        # non-blocking operation
        job_id = self.scheduler.add_job(job_class_string, name, trigger, pub_args, trigger_params)

        self.assertTrue(len(job_id), 32)

        job_class_string = 'hello.world1234'
        args = ['5', '6', '7']
        name = 'hello world 3'
        trigger = 'cron'
        trigger_params = dict(
            month='*/6'
            )

        # non-blocking operation
        self.scheduler.modify_job(job_id, name=name, job_class_string=job_class_string,
                                  trigger=trigger,
                                  pub_args=args, trigger_params=trigger_params)

        # blocking operation
        job = self.scheduler.get_job(job_id)
        self.assertEqual(job.name, name)

        arguments = [job_class_string, job_id,
                     'ndscheduler.corescheduler.datastore.providers.sqlite.DatastoreSqlite',
                     None, None]
        arguments += args
        self.assertEqual(list(job.args), arguments)
        self.assertEqual(str(job.trigger.fields[1]), trigger_params['month'])
