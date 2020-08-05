"""A job to send a HTTP (GET or DELETE) periodically."""

import logging
import requests

from ndscheduler.corescheduler import job

logger = logging.getLogger(__name__)


class CurlJob(job.JobBase):
    TIMEOUT = 10

    @classmethod
    def meta_info(cls):
        return {
            'job_class_string': '%s.%s' % (cls.__module__, cls.__name__),
            'notes': 'This sends a HTTP request to a particular URL',
            'arguments': [
                # url
                {'type': 'string', 'description': 'What URL you want to make a GET call?'},
                # Request Type
                {'type': 'string', 'description': 'What request type do you want? '
                                                  '(currently supported: GET/DELETE)'},

            ],
            'example_arguments': ('["http://localhost:8888/api/v1/jobs", "GET"]'
                                  '["http://localhost:8888/api/v1/jobs/ba12e", "DELETE"]')
        }

    def run(self, url, request_type,  *args, **kwargs):
        print('Calling GET on url: %s' % (url))

        session = requests.Session()
        result = session.request(request_type,
                                 url,
                                 timeout=self.TIMEOUT,
                                 headers=None,
                                 data=None)
        return result.text


if __name__ == "__main__":
    job = CurlJob.create_test_instance()
    job.run('http://localhost:888/api/v1/jobs')
