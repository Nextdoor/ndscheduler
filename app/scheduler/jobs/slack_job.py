"""A job to send slack message periodically."""

import logging
import json
import os
import socket

import requests

from .. import job

logger = logging.getLogger(__name__)


class SlackJob(job.JobBase):

    MAX_RETRIES = 3
    TIMEOUT = 10

    @classmethod
    def meta_info(cls):
        return {
            'job_class_string': '%s.%s' % (cls.__module__, cls.__name__),
            'notes': ('This sends message to a Slack channel. To run this job, you have to run '
                      'scheduler with environment variable SIMPLE_SCHEDULER_SLACK_URL'),
            'arguments': [
                # channel
                {'type': 'string', 'description': 'What channel you want to send the message to'},

                # name
                {'type': 'string', 'description': 'This bot\'s name'},

                # icon_emoji
                {'type': 'string', 'description': 'An emoji for this bot\'s avatar'},

                # message
                {'type': 'string', 'description': 'The actual message you want to send.'},
            ],
            'example_arguments': ('["#slack-bot-test", "ndscheduler chat bot", ":satisfied:",'
                                  ' "Standup, team! @channel"]')
        }

    def run(self, channel, name, icon_emoji, message, *args, **kwargs):

        try:
            # This URL looks like this:
            # http://hooks.slack.com/services/T024TTTTT/BBB72BBL/AZAAA9u0pA4ad666eMgbi555
            # (not a real api url, don't try it :)
            #
            # You can get this url by adding an incoming webhook:
            # https://nextdoor.slack.com/apps/new/A0F7XDUAZ-incoming-webhooks
            url = os.environ['SIMPLE_SCHEDULER_SLACK_URL']
        except KeyError:
            logger.error('Environment variable SIMPLE_SCHEDULER_SLACK_URL is not specified. '
                         'So we cannot send slack message.')
            raise KeyError('You have to set Environment variable SIMPLE_SCHEDULER_SLACK_URL first.')
        else:
            session = requests.Session()
            adapter = requests.adapters.HTTPAdapter(max_retries=self.MAX_RETRIES)
            session.mount('http://', adapter)
            session.mount('https://', adapter)

            message += ' // `sent from %s`' % socket.gethostname()
            payload = {
                'channel': channel,
                'username': name,
                'text': message,
                'link_names': 1,
                "mrkdwn": 1,
                'icon_emoji': icon_emoji
            }
            session.request('POST', url, timeout=self.TIMEOUT,
                            headers={'content-type': 'application/json'},
                            data=json.dumps(payload))

if __name__ == "__main__":
    # You can easily test this job here
    job = SlackJob.create_test_instance()
    job.run('#slack-bot-test', 'ndscheduler', ':satisfied:', 'Standup, team! @channel')
