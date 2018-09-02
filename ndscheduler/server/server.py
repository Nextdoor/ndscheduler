"""Runs a tornado process to run scheduler daemon and provides REST API & web ui.

How to use:

    SchedulerServer.run()
"""

import logging
import signal
import sys

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

    def __init__(self, scheduler_instance, custom_tornado_settings=None):
        """
        Start scheduler

        Pass:
          scheduler_instance - instance of the `SchedulerManager` class
          custom_tornado_settings - optional dictionary of settings, to
                                    be merged if present with the defaults
                                    set below, adding to and/or replacing
                                    the settings in `self.tornado_settings`
        """

        self.scheduler_manager = scheduler_instance

        self.tornado_settings = dict(
            debug=settings.DEBUG,
            static_path=settings.STATIC_DIR_PATH,
            template_path=settings.TEMPLATE_DIR_PATH,
            scheduler_manager=self.scheduler_manager
        )
        if custom_tornado_settings is not None:
            self.tornado_settings.update(custom_tornado_settings)

        # Setup server
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

    def start_scheduler(self):
        self.scheduler_manager.start()
        self.post_scheduler_start()

    def post_scheduler_start(self):
        """Implement this function to do things once scheduler starts"""
        pass

    def stop_scheduler(self):
        self.scheduler_manager.stop()
        self.post_scheduler_stop()

    def post_scheduler_stop(self):
        """Implement this function to do things once scheduler stops"""
        pass

    @classmethod
    def signal_handler(cls, signal, frame):
        logger.info('Stopping scheduler ...')
        cls.singleton.stop_scheduler()
        logger.info('Done. Bye ~')
        sys.exit(0)

    @classmethod
    def run(cls):
        if not cls.singleton:
            signal.signal(signal.SIGINT, cls.signal_handler)

            cls.singleton = cls(scheduler_manager.SchedulerManager.get_instance())
            cls.singleton.start_scheduler()
            cls.singleton.application.listen(settings.HTTP_PORT, settings.HTTP_ADDRESS)
            logger.info('Running server at %s:%d ...' % (settings.HTTP_ADDRESS, settings.HTTP_PORT))
            logger.info('*** You can access scheduler web ui at http://localhost:%d'
                        ' ***' % settings.HTTP_PORT)
            tornado.ioloop.IOLoop.instance().start()
