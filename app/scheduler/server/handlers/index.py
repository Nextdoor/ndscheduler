"""Serves the single page app web ui."""

import json

from ... import settings
from ... import utils
from . import base


class Handler(base.BaseHandler):
    """Index page request handler."""

    def get(self):
        """Serve up the single page app for scheduler dashboard."""

        meta_info = utils.get_all_available_jobs()
        self.render(settings.APP_INDEX_PAGE,
                    jobs_meta_info=json.dumps(meta_info),
                    url_prefix=settings.URL_PREFIX)
