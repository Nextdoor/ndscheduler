"""A job that sends a Celery task to a queue"""

import sys

from celery import Celery, Task

from .. import job


class CeleryJob(job.JobBase):

    @classmethod
    def meta_info(cls):
        return {
            'job_class_string': '%s.%s' % (cls.__module__, cls.__name__),
            'notes': 'This will run a predefined celery task',
            'arguments': [
                {'type': 'string', 'description': 'task name'},
                {'type': 'list', 'description': 'arguments'},
                {'type': 'string', 'description': 'broker'},
                {'type': 'string', 'description': 'backend'},
            ],
            'example_arguments': '["tasks.add", [1, 2], "redis://redis:6379/0", "redis://redis:6379/0"]'
        }

    def get_failed_description(self):
        return self.celery_traceback

    def get_succeeded_description(self):
        return "Task result: {}".format(self.celery_result)[:100]

    def run(self, task_name, task_args, broker, backend, *args, **kwargs):
        app = Celery('tasks', backend=backend, broker=broker)
        remote_task = Task()
        remote_task.name = task_name
        res = remote_task.apply_async(args=task_args)
        try:
            self.celery_result = res.get()
        except Exception as e:
            self.celery_traceback = res.traceback
            raise e


if __name__ == "__main__":
    # You can easily test this job here
    job = CeleryJob.create_test_instance()
    job.run()
