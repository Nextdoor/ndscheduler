"""Serves the single page app web ui."""

import json

from ndscheduler import settings
from ndscheduler import utils
from ndscheduler.version import __version__
from ndscheduler.server.handlers import base
from getpass import getuser
from os import uname
import pkg_resources

import tornado.web


class Handler(base.BaseHandler):
    """Index page request handler."""

    def get(self):
        """Serve up the single page app for scheduler dashboard."""

        # redirect to root if coming from unknown URL via
        if self.request.uri != "/":
            self.redirect("/")
            return

        # Get job pack versions
        job_versions = []
        for job in settings.JOB_CLASS_PACKAGES:
            job_versions.append(
                f"{job} v{pkg_resources.require(job.split('.')[0])[0].version}"
            )

        website_info = {
            "title": settings.WEBSITE_TITLE,
            "version": __version__,
            "job_versions": ", ".join(job_versions),
            "user": getuser(),
            "host": uname()[1],
            "admin_user": self.current_user
            and self.current_user.decode() in settings.ADMIN_USER,
            "help_url": settings.HELP_URL,
        }

        meta_info = utils.get_all_available_jobs()
        self.render(
            settings.APP_INDEX_PAGE,
            jobs_meta_info=json.dumps(meta_info),
            website_info=website_info,
            # current_user=self.get_current_user(),
        )
