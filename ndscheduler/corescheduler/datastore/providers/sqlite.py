"""Represents SQLite datastore."""

import datetime

import pytz

from ndscheduler.corescheduler.datastore import base


class DatastoreSqlite(base.DatastoreBase):
    def get_db_url(self):
        """Returns the db url to establish a SQLite connection, where db_config is passed in
        on initialization as:
        {
            'file_path': 'an_absolute_file_path'
        }
        If 'file_path' is not passed in, an in-memory SQLite db is created.
        :return: string db url
        """
        file_path = ""
        if self.db_config and "file_path" in self.db_config:
            file_path = self.db_config["file_path"]
        return "sqlite:///" + file_path

    def get_time_isoformat_from_db(self, time_object):
        date = datetime.datetime.strptime(time_object, "%Y-%m-%d %H:%M:%S.%f")
        date = pytz.utc.localize(date)
        return date.isoformat()
