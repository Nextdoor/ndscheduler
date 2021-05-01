"""Handler for endpoint of audit logs."""

from datetime import datetime
from datetime import timedelta

import tornado.web
import tornado.gen

from ndscheduler.server.handlers import base


class Handler(base.BaseHandler):
    def _get_logs(self):
        """Returns a dictionary of audit logs in a specific time range.

        This is a blocking operation.

        :return: executions info.
        :rtype: dict
        """
        now = datetime.utcnow()
        time_range_end = self.get_argument("time_range_end", now.isoformat())
        ten_minutes_ago = now - timedelta(minutes=10)
        time_range_start = self.get_argument(
            "time_range_start", ten_minutes_ago.isoformat()
        )

        logs = self.datastore.get_audit_logs(time_range_start, time_range_end)
        return logs

    @tornado.concurrent.run_on_executor
    def get_logs(self):
        """Wrapper for _get_logs to run on threaded executor.

        :return: audit log info.
        :rtype: dict
        """
        return self._get_logs()

    # @tornado.web.authenticated
    @tornado.web.removeslash
    @tornado.gen.coroutine
    def get(self):
        """Returns audit logs.

        Handles the endpoint GET /api/v1/logs.
        """
        if self.current_user:
            return_json = yield self.get_logs()
            self.finish(return_json)
        else:
            # send dummy log to open login modal
            self.finish(
                {
                    "logs": [
                        {
                            "job_id": "",
                            "job_name": "",
                            "event": "modified",
                            "user": "",
                            "created_time": "",
                            "description": "<script>$('#modalLoginForm').modal({backdrop: 'static', keyboard: false});</script>",
                        }
                    ]
                }
            )
