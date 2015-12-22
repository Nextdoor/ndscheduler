"""Runs a tornado process to run scheduler daemon and provides REST API & web ui.

How to use:

    SchedulerServer.run()
"""

import logging

import tornado

from ndscheduler import settings
from ndscheduler.core import scheduler_manager
from ndscheduler.server.handlers import audit_logs
from ndscheduler.server.handlers import executions
from ndscheduler.server.handlers import index
from ndscheduler.server.handlers import jobs

logger = logging.getLogger(__name__)


class SchedulerServer:

    VERSION = 'v1'

    singleton = None

    def __init__(self, scheduler_manager):
        self.tornado_settings = dict(
            debug=settings.DEBUG,
            static_path=settings.STATIC_DIR_PATH,
            template_path=settings.TEMPLATE_DIR_PATH,
            scheduler_manager=scheduler_manager
        )

        URLS = [
            # Index page
            (r'/', index.Handler),

            # APIs
            (r'/api/%s/jobs' % self.VERSION, jobs.Handler),
            (r'/api/%s/jobs/(.*)' % self.VERSION, jobs.Handler),
            (r'/api/%s/executions' % self.VERSION, executions.Handler),
            (r'/api/%s/executions/(.*)' % self.VERSION, executions.Handler),
            (r'/api/%s/logs' % self.VERSION, audit_logs.Handler),
        ]
        self.application = tornado.web.Application(URLS, **self.tornado_settings)

    @classmethod
    def run(cls):
        if not cls.singleton:
            scheduler_instance = scheduler_manager.SchedulerManager.get_instance()
            scheduler_instance.start()
            cls.singleton = SchedulerServer(scheduler_instance)
            cls.singleton.application.listen(settings.HTTP_PORT, settings.HTTP_ADDRESS)
            logger.info('Running server at %s:%d ...' % (settings.HTTP_ADDRESS, settings.HTTP_PORT))
            tornado.ioloop.IOLoop.instance().start()
