"""Base tornado.web.RequestHandler classes.

This package provides a common set of RequestHandler objects to be
subclassed in the rest of the app for different URLs.
"""

import json

from concurrent import futures

import tornado.ioloop
import tornado.web

from ndscheduler import settings

from tornado_http_auth import DigestAuthMixin, auth_required


class BaseHandler(tornado.web.RequestHandler, DigestAuthMixin):

    executor = futures.ThreadPoolExecutor(max_workers=settings.TORNADO_MAX_WORKERS)

    @auth_required(realm='Protected', auth_func=settings.BASIC_AUTH_CREDENTIALS.get)
    def prepare(self):
        """Preprocess requests."""
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
