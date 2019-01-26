"""Run the scheduler process."""

from ndscheduler.server import server
import ptvsd
import os


class SimpleServer(server.SchedulerServer):

    def post_scheduler_start(self):
        pass
        # New user experience! Make sure we have at least 1 job to demo!
        # jobs = self.scheduler_manager.get_jobs()
        # if len(jobs) == 0:
        #     self.scheduler_manager.add_job(
        #         job_class_string='simple_scheduler.jobs.sample_job.AwesomeJob',
        #         name='My Awesome Job2',
        #         pub_args=['first parameter', {'second parameter': 'can be a dict'}],
        #         minute='*/1')


if __name__ == "__main__":
    if os.environ['DEBUG'] == '1':
        ptvsd.enable_attach(address=('0.0.0.0', 5861))
        ptvsd.wait_for_attach()
    SimpleServer.run()
