"""Represents SQLite datastore."""

import datetime
import pytz

from ndscheduler import settings
from ndscheduler.core.datastore.providers import base


class DatastoreSqlite(base.DatastoreBase):

    @classmethod
    def get_db_url(cls):
        """

        DATABASE_CONFIG_DICT = {
            'file_path': 'an_absolute_path'
        }

        :return: database url
        :rtype: str
        """
        if 'file_path' in settings.DATABASE_CONFIG_DICT:
            file_path = settings.DATABASE_CONFIG_DICT['file_path']
        else:
            # If file_path is not specified, then use in-memory sqlite db.
            file_path = ''

        return 'sqlite:///' + file_path

    def get_time_isoformat_from_db(self, time_object):
        date = datetime.datetime.strptime(time_object, '%Y-%m-%d %H:%M:%S.%f')
        date = pytz.utc.localize(date)
        return date.isoformat()
