"""A sample job that prints string."""

from ndscheduler import job


class AwesomeJob(job.JobBase):

    @classmethod
    def run(cls, job_id, execution_id, argument1, argument2, *args, **kwargs):
        print 'Hello from AwesomeJob! Argument1: %s, Argument2: %s' % (argument1, argument2)
