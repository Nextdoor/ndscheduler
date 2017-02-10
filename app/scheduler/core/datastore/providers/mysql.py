"""Represents MySQL datastore."""

from ndscheduler import settings
from ndscheduler.core.datastore.providers import base


class DatastoreMysql(base.DatastoreBase):

    @classmethod
    def get_db_url(cls):
        """
        DATABASE_CONFIG_DICT = {
            'user': 'myuser',
            'password': 'password',
            'hostname': 'mydb.domain.com',
            'port': 5432,
            'database': 'mydatabase'
        }

        :return: database url
        :rtype: str
        """

        return 'mysql+pymysql://%s:%s@%s:%d/%s' % (
            settings.DATABASE_CONFIG_DICT['user'],
            settings.DATABASE_CONFIG_DICT['password'],
            settings.DATABASE_CONFIG_DICT['hostname'],
            settings.DATABASE_CONFIG_DICT['port'],
            settings.DATABASE_CONFIG_DICT['database'])
