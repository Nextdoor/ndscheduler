"""Serves the single page app web ui."""

from ndscheduler import settings
from ndscheduler.server.handlers import base


class Handler(base.BaseHandler):
    """Index page request handler."""

    def get(self):
        """Serve up the single page app for scheduler dashboard."""

        self.render(settings.APP_INDEX_PAGE)
