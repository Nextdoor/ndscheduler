"""Base tornado.web.RequestHandler classes.

This package provides a common set of RequestHandler objects to be
subclassed in the rest of the app for different URLs.
"""

import json
import base64

from concurrent import futures

import tornado.ioloop
import tornado.web

from ndscheduler import settings


class BaseHandler(tornado.web.RequestHandler):

    executor = futures.ThreadPoolExecutor(max_workers=settings.TORNADO_MAX_WORKERS)

    basic_auth_credentials = settings.BASIC_AUTH_CREDENTIALS
    basic_auth_realm = 'Scheduler'

    def send_challenge(self):
        """Send challenge response."""
        header = 'Basic realm="{}"'.format(self.basic_auth_realm)
        self.set_status(401)
        self.set_header('WWW-Authenticate', header)
        self.finish()

    def get_basic_auth_result(self):
        """Get HTTP basic access authentication result."""
        auth_header = self.request.headers.get('Authorization', '')
        if not auth_header.startswith('Basic '):
            self.send_challenge()
            return

        auth_data = auth_header.split(' ')[-1]
        auth_data = base64.b64decode(auth_data).decode('utf-8')
        username, password = auth_data.split(':')

        challenge = self.basic_auth_credentials.get(username)
        if challenge != password:
            self.send_challenge()

    def prepare(self):
        """Preprocess requests."""
        if len(self.basic_auth_credentials) > 0:
            self.get_basic_auth_result()

        try:
            if self.request.headers['Content-Type'].startswith('application/json'):
                self.json_args = json.loads(self.request.body.decode())
        except KeyError:
            self.json_args = None

        # For audit log
        self.username = self.get_username()
        self.scheduler_manager = self.application.settings['scheduler_manager']
        self.datastore = self.scheduler_manager.get_datastore()

    def get_username(self):
        """Returns login username.

        Empty string by default.

        :return: username
        :rtype: str
        """
        return ''
