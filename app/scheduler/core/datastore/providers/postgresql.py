"""Represents PostgreSQL datastore."""

from .... import settings
from . import base


class DatastorePostgresql(base.DatastoreBase):

    @classmethod
    def get_db_url(cls):
        """
        DATABASE_CONFIG_DICT = {
            'user': 'myuser',
            'password': 'password',
            'hostname': 'mydb.domain.com',
            'port': 5432,
            'database': 'mydatabase',
            'sslmode': 'disable'
        }

        :return: database url
        :rtype: str
        """

        return 'postgresql://%s:%s@%s:%d/%s?sslmode=%s' % (
            settings.DATABASE_CONFIG_DICT['user'],
            settings.DATABASE_CONFIG_DICT['password'],
            settings.DATABASE_CONFIG_DICT['hostname'],
            settings.DATABASE_CONFIG_DICT['port'],
            settings.DATABASE_CONFIG_DICT['database'],
            settings.DATABASE_CONFIG_DICT['sslmode'])
