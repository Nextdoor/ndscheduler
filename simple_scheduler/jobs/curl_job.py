"""A job to send a HTTP GET periodically."""

import logging
import requests

from ndscheduler import job

logger = logging.getLogger(__name__)


class CurlJob(job.JobBase):
    TIMEOUT = 10

    @classmethod
    def meta_info(cls):
        return {
            'job_class_string': '%s.%s' % (cls.__module__, cls.__name__),
            'notes': ('This sends a HTTP GET to a particular URL'),
            'arguments': [
                # url
                {'type': 'string', 'description': 'What URL you want to make a GET call?'},
            ],
            'example_arguments': ('["http://localhost:8888/api/v1/jobs"]')
        }

    def run(self, url, *args, **kwargs):
        print 'Calling GET on url: %s' % (url)

        session = requests.Session()
        session.request('GET',
                        url,
                        timeout=self.TIMEOUT,
                        headers=None,
                        data=None)


if __name__ == "__main__":
    job = CurlJob.create_test_instance()
    job.run('http://localhost:888/api/v1/jobs')
