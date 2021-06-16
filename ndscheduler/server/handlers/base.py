"""Base tornado.web.RequestHandler classes.

This package provides a common set of RequestHandler objects to be
subclassed in the rest of the app for different URLs.
"""

import logging
import json
import bcrypt
import ldap

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
        password = self.get_argument("password")
        hashed = self.auth_credentials.get(username)
        logger.debug(f"Received login for user '{username}'")
        if settings.LDAP_SERVER and self.ldap_login(username, password):
            self.set_user_cookie(username)
        elif hashed is not None and bcrypt.checkpw(password.encode(), hashed.encode()):
            logger.debug("Try local authentication")
            self.set_user_cookie(username)
        else:
            logger.debug("Wrong username or password")
        self.redirect("/")

    def set_user_cookie(self, username):
        # 6h = 0.25 days
        # 1h = 0.041666667 days
        # 1min = 0.000694444 days
        self.set_secure_cookie(settings.COOKIE_NAME, username, expires_days=settings.COOKIE_MAX_AGE)
        logger.debug(f"Set cookie for user {username}, expires: {settings.COOKIE_MAX_AGE * 1440} minutes")

    def ldap_login(self, username, password):
        """Verifies credentials for username and password.

        Parameters
        ----------
        username : str
            User ID (uid) to be used for login
        password : str
            User password

        Returns
        -------
        bool
            True if login was successful
        """
        if settings.LDAP_USERS and username not in settings.LDAP_USERS:
            logging.warning(f"User {username} not allowed for LDAP login")
            return False
        LDAP_SERVER = settings.LDAP_SERVER
        # Create fully qualified DN for user
        LDAP_DN = settings.LDAP_LOGIN_DN.replace("{username}", username)
        logger.debug(f"LDAP dn: {LDAP_DN}")
        # disable certificate check
        ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_ALLOW)

        # specify certificate dir or file
        if settings.LDAP_CERT_DIR:
            ldap.set_option(ldap.OPT_X_TLS_CACERTDIR, settings.LDAP_CERT_DIR)
        if settings.LDAP_CERT_FILE:
            ldap.set_option(ldap.OPT_X_TLS_CACERTFILE, settings.LDAP_CERT_FILE)
        try:
            # build a client
            ldap_client = ldap.initialize(LDAP_SERVER)
            ldap_client.set_option(ldap.OPT_REFERRALS, 0)
            # perform a synchronous bind to test authentication
            ldap_client.simple_bind_s(LDAP_DN, password)
            logger.info(f"User '{username}' successfully authenticated via LDAP")
            ldap_client.unbind_s()
            return True
        except (ldap.INVALID_CREDENTIALS, ldap.NO_SUCH_OBJECT):
            ldap_client.unbind()
            logger.warning("LDAP: wrong username or password")
        except ldap.SERVER_DOWN:
            logger.warning("LDAP server not available")
        except ldap.LDAPError as e:
            if isinstance(e, dict) and "desc" in e:
                logger.warning(f"LDAP error: {e['desc']}")
            else:
                logger.warning(f"LDAP error: {e}")
        return False


class LogoutHandler(BaseHandler):

    # basic_auth_credentials = settings.BASIC_AUTH_CREDENTIALS

    def get(self):
        self.clear_cookie(settings.COOKIE_NAME)
        self.redirect("/")
