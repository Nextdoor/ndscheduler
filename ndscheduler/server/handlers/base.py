"""Base tornado.web.RequestHandler classes.

This package provides a common set of RequestHandler objects to be
subclassed in the rest of the app for different URLs.
"""

import json
import bcrypt

from concurrent import futures

import tornado.web

from ndscheduler import settings


class BaseHandler(tornado.web.RequestHandler):

    executor = futures.ThreadPoolExecutor(max_workers=settings.TORNADO_MAX_WORKERS)

    auth_credentials = settings.AUTH_CREDENTIALS

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

    def get_current_user(self):
        if len(self.auth_credentials) > 0:
            return self.get_secure_cookie("user", max_age_days=settings.COOKIE_MAX_AGE)
        else:
            return "anonymous"

    def get_username(self):
        """Returns login username.

        "anonymous" by default.

        :return: username
        :rtype: str
        """
        username = self.get_secure_cookie("user", max_age_days=settings.COOKIE_MAX_AGE)
        return "anonymous" if username is None else username.decode()


class LoginHandler(BaseHandler):

    max_age = settings.COOKIE_MAX_AGE

    def get(self):
        self.write("Login required!")

    def post(self):
        username = self.get_argument("username")
        hashed = self.auth_credentials.get(username)
        if hashed is not None and bcrypt.checkpw(
            self.get_argument("password").encode(), hashed.encode()
        ):
            # 6h = 0.25 days
            # 1min = 0.0007 days
            self.set_secure_cookie("user", username, expires_days=self.max_age)
            self.redirect("/")
        else:
            self.redirect("/")


class LogoutHandler(BaseHandler):

    # basic_auth_credentials = settings.BASIC_AUTH_CREDENTIALS

    def get(self):
        self.clear_cookie("user")
        self.redirect("/")
