"""Simple job to send test Apple Push Notifications."""

import logging
import os

from ndscheduler.corescheduler import job
from apns import APNs, Payload

logger = logging.getLogger(__name__)


class APNSJob(job.JobBase):

    @classmethod
    def meta_info(cls):
        return {
            'job_class_string': '%s.%s' % (cls.__module__, cls.__name__),
            'notes': 'This sends a push notification to APNS servers. '
                     'The environment variable APNS_CERT_PATH" should be provided '
                     'for APNS cert file path.',
            'arguments': [
                # APNS device token
                {'token': 'string', 'description': 'Device token'},
                # APNS Title's Alert Text
                {'alert': 'string', 'description': 'What do you want to send?'},
            ],
            'example_arguments': ('["da1232badh2", "Hello from scheduler"]')
        }

    def run(self, token, alert="Hello World",  *args, **kwargs):
        print('Sending %s to %s' % (alert, token))

        cert_file = os.environ['APNS_CERT_PATH'] or 'simple_scheduler/jobs/apns-cert.pem'
        apns = APNs(use_sandbox=False, cert_file=cert_file)
        # Send a notification
        payload = Payload(alert=alert, sound="default", badge=0)
        apns.gateway_server.send_notification(token, payload)


if __name__ == "__main__":
    job = APNSJob.create_test_instance()
    job.run('da1232badh2', 'Hello World')
