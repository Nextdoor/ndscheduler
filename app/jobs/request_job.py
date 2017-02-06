"""A job to send a HTTP (GET or DELETE) periodically."""

import logging
import requests

from ndscheduler import job

logger = logging.getLogger(__name__)


class RequestJob(job.JobBase):
    TIMEOUT = 10

    @classmethod
    def meta_info(cls):
        return {
            'job_class_string': '%s.%s' % (cls.__module__, cls.__name__),
            'notes': 'This sends a HTTP request to a particular URL',
            'arguments': [
                {'type': 'string', 'description': 'Which URL do you want to call?'},
                {'type': 'string', 'description': 'HTTP method?'},
                {'type': 'string', 'description': 'Payload?'},

            ],
            'example_arguments': ('["http://localhost:8888/api/v1/jobs", "POST", "{}"]')
        }

    def run(self, url, http_method, payload, *args, **kwargs):
        print('Calling %s on url: %s' % (http_method, url))

        result = requests.post(url,
                               timeout=self.TIMEOUT,
                               headers={'Content-Type': 'application/json'},
                               data=payload)
        print(result.text)


if __name__ == "__main__":
    job = RequestJob.create_test_instance()
    job.run('http://localhost:888/api/v1/jobs')
