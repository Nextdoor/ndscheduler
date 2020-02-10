"""Run the scheduler process."""

from ndscheduler.server import server


class SimpleServer(server.SchedulerServer):

    def post_scheduler_start(self):
        # New user experience! Make sure we have at least 1 job to demo!
        jobs = self.scheduler_manager.get_jobs()
        if len(jobs) == 0:
            self.scheduler_manager.add_job(
                job_class_string='simple_scheduler.jobs.sample_job.AwesomeJob',
                name='My Awesome Job',
                pub_args=['first parameter', {'second parameter': 'can be a dict'}],
                trigger='cron',
                trigger_params={'minute': '*/1'})


if __name__ == "__main__":
    SimpleServer.run()
