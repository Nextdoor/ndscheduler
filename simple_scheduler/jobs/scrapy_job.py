"""A job to send a HTTP (GET or DELETE) periodically."""

import logging
import requests
from ndscheduler import job
from ndscheduler.pubsub import PubSub

logger = logging.getLogger(__name__)


class ScrapyJob(job.JobBase):
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

    def run(self, spider_name):
        result = requests.post('http://event_processor:6800/schedule.json',
                               data={'project': 'In2ItChicago', 'spider': spider_name})
        json = result.json()
        if 'status' not in json or json['status'] != 'ok':
            raise Exception('scrapy job failed: ' + json)

        result = PubSub.subscribe(json['jobid'], lambda result: result)
        if result['status'] == 'failure':
            raise Exception('Failure during scrapy processing: ' + str(result))
        return result


if __name__ == "__main__":
    job = ScrapyJob.create_test_instance()
    job.run('history')
