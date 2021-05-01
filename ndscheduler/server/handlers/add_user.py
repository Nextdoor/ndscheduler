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
        "added": False,
        "message": None,
    }

    @tornado.web.authenticated
    def get(self):
        self.website_info["added"] = False
        self.website_info["message"] = None
        self.render(
            "add_user.html", website_info=self.website_info,
        )

    @tornado.web.authenticated
    def post(self):
        username = self.get_argument("username")
        new_pwd = self.get_argument("new_pwd")
        if self.current_user.decode() in settings.ADMIN_USER:
            self.website_info["message"] = f"Added new user '{username}'!"
            self.website_info["added"] = True
            print(">>> user added:", self.website_info)
            self.render(
                "add_user.html", website_info=self.website_info,
            )
            salt = bcrypt.gensalt()
            new_pwd = bcrypt.hashpw(new_pwd.encode(), salt).decode()
            settings.AUTH_CREDENTIALS[username] = new_pwd
            with open(settings.YAML_CONFIG_FILE, "w") as f:
                f.write(
                    f"# Configuration updated by user '{self.current_user.decode()}' on {dt.now().strftime('%d.%m.%Y at %H:%M:%S')}\n\n"
                )
                f.write(settings.YAML_CONFIG.dump(full=False))
        else:
            self.website_info["message"] = "No admin right!"
            self.render(
                "add_user.html", website_info=self.website_info,
            )
