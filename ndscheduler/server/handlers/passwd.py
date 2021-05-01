import tornado.concurrent
import tornado.gen
import tornado.web
import confuse

from ndscheduler import settings
from ndscheduler.server.handlers import base
from ndscheduler.version import __version__
from getpass import getuser
from os import uname
import bcrypt
from time import sleep
from datetime import datetime as dt


class Handler(base.BaseHandler):
    """Index page request handler."""

    website_info = {
        "title": settings.WEBSITE_TITLE,
        "version": __version__,
        "user": getuser(),
        "host": uname()[1],
        "changed": False,
        "message": None,
    }

    def get(self):
        self.website_info["changed"] = False
        self.website_info["message"] = None
        self.render(
            "passwd.html", website_info=self.website_info,
        )

    def post(self):
        username = self.get_argument("username")
        new_pwd = self.get_argument("new_pwd")
        hashed = self.auth_credentials.get(username)
        if hashed is not None and bcrypt.checkpw(
            self.get_argument("password").encode(), hashed.encode()
        ):
            self.website_info["message"] = f"Changed Password!"
            self.website_info["changed"] = True
            self.render(
                "passwd.html", website_info=self.website_info,
            )
            salt = bcrypt.gensalt()
            new_pwd = bcrypt.hashpw(new_pwd.encode(), salt).decode()
            settings.AUTH_CREDENTIALS[username] = new_pwd
            with open(settings.YAML_CONFIG_FILE, "w") as f:
                f.write(
                    f"# Password changed by user '{self.current_user.decode()}' on {dt.now().strftime('%d.%m.%Y at %H:%M:%S')}\n\n"
                )
                f.write(settings.YAML_CONFIG.dump(full=False))
        else:
            self.website_info["message"] = "Wrong Password"
            self.render(
                "passwd.html", website_info=self.website_info,
            )
