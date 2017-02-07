"""Run the scheduler process."""
import os

from scheduler.server import server


class SimpleServer(server.SchedulerServer):

    def post_scheduler_start(self):
        # New user experience! Make sure we have at least 1 job to demo!
        jobs = self.scheduler_manager.get_jobs()
        # if len(jobs) == 0:
        #     self.scheduler_manager.add_job(
        #         job_class_string='jobs.sample_job.AwesomeJob',
        #         name='My Awesome Job',
        #         pub_args=['first parameter', {'second parameter': 'can be a dict'}],
        #         minute='*/1')

def compile_template(fname):
    with open(fname, 'r') as f:
        s = f.read().replace('{{URL_PREFIX}}', os.environ.get('URL_PREFIX', ''))
    compiled = fname.replace('.template', '')
    with open(compiled, 'w') as f:
        f.write(s)

def compile_templates(path):
    for f in os.listdir(path):
        if f.endswith('.template'):
            compile_template(os.path.join(path, f))


if __name__ == "__main__":
    compile_templates('/app/scheduler/static/js')
    SimpleServer.run()
