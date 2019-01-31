"""Serves the single page app web ui."""

import json

from ndscheduler import settings
from ndscheduler import utils
from ndscheduler.server.handlers import base


class Handler(base.BaseHandler):
    """Index page request handler."""

    def get(self):
        """Serve up the single page app for scheduler dashboard."""

        website_info = {
            'title': settings.WEBSITE_TITLE,
        }
        
        meta_info = utils.get_all_available_jobs()
        self.render(settings.APP_INDEX_PAGE, 
                    jobs_meta_info=json.dumps(meta_info),
                    website_info=website_info,
                    )
