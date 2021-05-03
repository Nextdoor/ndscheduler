"""Runs a tornado process to run scheduler daemon and provides REST API & web ui.

How to use:

    SchedulerServer.run()
"""

import logging
import signal
import sys

import tornado
import ssl

from ndscheduler import settings
from ndscheduler.corescheduler import scheduler_manager
from ndscheduler.server.handlers import audit_logs
from ndscheduler.server.handlers import executions
from ndscheduler.server.handlers import index
from ndscheduler.server.handlers import jobs
from ndscheduler.server.handlers import base
from ndscheduler.server.handlers import passwd
from ndscheduler.server.handlers import add_user

logger = logging.getLogger(__name__)


class SchedulerServer:

    VERSION = "v1"

    singleton = None

    def __init__(self, scheduler_instance):
        # Start scheduler
        self.scheduler_manager = scheduler_instance

        self.tornado_settings = dict(
            debug=settings.DEBUG,
            static_path=settings.STATIC_DIR_PATH,
            template_path=settings.TEMPLATE_DIR_PATH,
            scheduler_manager=self.scheduler_manager,
            cookie_secret=settings.SECURE_COOKIE,
            login_url="/login",
            default_handler_class=index.Handler,
            # default_handler_args={
            #     'status_code': 404,
            #     'message': 'Unknown Endpoint'
            # },
        )

        # Setup server
        URLS = [
            # Index page
            (r"/", index.Handler),
            (r"/login", base.LoginHandler),
            (r"/logout", base.LogoutHandler),
            (r"/passwd", passwd.Handler),
            (r"/add_user", add_user.Handler),
            # APIs
            (r"/api/%s/jobs" % self.VERSION, jobs.Handler),
            (r"/api/%s/jobs/(.*)" % self.VERSION, jobs.Handler),
            (r"/api/%s/executions" % self.VERSION, executions.Handler),
            (r"/api/%s/executions/(.*)" % self.VERSION, executions.Handler),
            (r"/api/%s/logs" % self.VERSION, audit_logs.Handler),
        ]
        self.application = tornado.web.Application(URLS, **self.tornado_settings,)

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
        logger.info("Stopping scheduler ...")
        cls.singleton.stop_scheduler()
        logger.info("Done. Bye ~")
        sys.exit(0)

    @classmethod
    def run(cls):
        if not cls.singleton:
            # Add handler for CLI program termination
            signal.signal(signal.SIGINT, cls.signal_handler)
            # Add handler for systemd service termination
            # Note that the default TimeoutStopSec= default is 90s, if the service
            # doesn't stop within this period, systemd will send a SIGKILL
            signal.signal(signal.SIGTERM, cls.signal_handler)

            sched_manager = scheduler_manager.SchedulerManager(
                scheduler_class_path=settings.SCHEDULER_CLASS,
                datastore_class_path=settings.DATABASE_CLASS,
                db_config=settings.DATABASE_CONFIG_DICT,
                db_tablenames=settings.DATABASE_TABLENAMES,
                job_coalesce=settings.JOB_COALESCE,
                job_misfire_grace_sec=settings.JOB_MISFIRE_GRACE_SEC,
                job_max_instances=settings.JOB_MAX_INSTANCES,
                thread_pool_size=settings.THREAD_POOL_SIZE,
                timezone=settings.TIMEZONE,
            )

            cls.singleton = cls(sched_manager)
            cls.singleton.start_scheduler()

            if settings.SSL_CERT and settings.SSL_KEY:
                logger.debug(f"SSL_CERT: {settings.SSL_CERT}, SSL_KEY: {settings.SSL_KEY}")
                # HTTPS server
                prefix = "https"
                ssl_ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
                ssl_ctx.load_cert_chain(settings.SSL_CERT, settings.SSL_KEY)
                http_server = tornado.httpserver.HTTPServer(cls.singleton.application, ssl_options=ssl_ctx)
                http_server.listen(settings.HTTP_PORT, settings.HTTP_ADDRESS)
            else:
                prefix = "http"
                cls.singleton.application.listen(settings.HTTP_PORT, settings.HTTP_ADDRESS)

            logger.info(f"Running server at {prefix}://{settings.HTTP_ADDRESS}:{settings.HTTP_PORT} ...")

            if settings.HTTP_ADDRESS == "":
                addr = "<this_host>"
            else:
                addr = settings.HTTP_ADDRESS
            logger.info(f"Running server at {prefix}://{addr}:{settings.HTTP_PORT} ...")

            tornado.ioloop.IOLoop.instance().start()
