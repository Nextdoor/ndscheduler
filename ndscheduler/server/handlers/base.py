"""Base tornado.web.RequestHandler classes.

This package provides a common set of RequestHandler objects to be
subclassed in the rest of the app for different URLs.
"""

import logging
import json
import bcrypt

from concurrent import futures

import tornado.web
import tornado.gen

from ndscheduler import settings

logger = logging.getLogger(__name__)


class BaseHandler(tornado.web.RequestHandler):

    executor = futures.ThreadPoolExecutor(max_workers=settings.TORNADO_MAX_WORKERS)
    auth_credentials = settings.AUTH_CREDENTIALS

    def prepare(self):
        """Preprocess requests."""

        try:
            if self.request.headers["Content-Type"].startswith("application/json"):
                self.json_args = json.loads(self.request.body.decode())
        except KeyError:
            self.json_args = None

        # clear expired cookies
        if not self.get_secure_cookie(settings.COOKIE_NAME, max_age_days=settings.COOKIE_MAX_AGE):
            self.clear_cookie(settings.COOKIE_NAME)
        # For audit log
        self.username = self.get_username()
        self.scheduler_manager = self.application.settings["scheduler_manager"]
        self.datastore = self.scheduler_manager.get_datastore()

    def get_current_user(self):
        if len(self.auth_credentials) > 0:
            return self.get_secure_cookie(settings.COOKIE_NAME, max_age_days=settings.COOKIE_MAX_AGE)
        else:
            return "anonymous"

    def get_username(self):
        """Returns login username.

        "anonymous" by default.

        :return: username
        :rtype: str
        """

        username = self.get_secure_cookie(settings.COOKIE_NAME, max_age_days=settings.COOKIE_MAX_AGE)
        return "anonymous" if username is None else username.decode()


class LoginHandler(BaseHandler):
    def get(self):
        if len(self.auth_credentials) > 0:
            logger.info("Login %s", self.auth_credentials)
            self.write("Login required!")
            self.write("<script>$('#modalLoginForm').modal({backdrop: 'static', keyboard: false});</script>")
        else:
            self.redirect("/")

    def post(self):
        username = self.get_argument("username")
        hashed = self.auth_credentials.get(username)
        logger.debug(f"Received login for user '{username}'")
        if hashed is not None and bcrypt.checkpw(self.get_argument("password").encode(), hashed.encode()):
            # 6h = 0.25 days
            # 1h = 0.041666667 days
            # 1min = 0.000694444 days
            self.set_secure_cookie(settings.COOKIE_NAME, username, expires_days=settings.COOKIE_MAX_AGE)
            logger.debug(f"Set cookie for user {username}, expires: {settings.COOKIE_MAX_AGE * 1440} minutes")
            self.redirect("/")
        else:
            logger.debug("Wrong username or password")
            self.redirect("/")


class LogoutHandler(BaseHandler):

    # basic_auth_credentials = settings.BASIC_AUTH_CREDENTIALS

    def get(self):
        self.clear_cookie(settings.COOKIE_NAME)
        self.redirect("/")
