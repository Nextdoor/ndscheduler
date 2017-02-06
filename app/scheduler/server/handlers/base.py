"""Base tornado.web.RequestHandler classes.

This package provides a common set of RequestHandler objects to be
subclassed in the rest of the app for different URLs.
"""

import json
import logging

from concurrent import futures

import tornado.ioloop
import tornado.web

from ... import settings


logger = logging.getLogger(__name__)


class BaseHandler(tornado.web.RequestHandler):

    executor = futures.ThreadPoolExecutor(max_workers=settings.TORNADO_MAX_WORKERS)

    def prepare(self):
        """Preprocess requests."""
        try:
            if self.request.headers['Content-Type'].startswith('application/json'):
                payload = self.request.body.decode('utf-8')
                self.json_args = json.loads(payload)
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
