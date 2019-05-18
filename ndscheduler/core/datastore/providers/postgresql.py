"""Represents PostgreSQL datastore."""

import sys
from ndscheduler import settings
from ndscheduler.core.datastore.providers import base


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

        # Work under Pypy, which doesn't have the default psycopg2
        if '__pypy__' in sys.builtin_module_names:
            db_wrapper = 'postgresql+psycopg2cffi'
        else:
            db_wrapper = 'postgresql'

        return '%s://%s:%s@%s:%d/%s?sslmode=%s' % (
                db_wrapper,
                settings.DATABASE_CONFIG_DICT['user'],
                settings.DATABASE_CONFIG_DICT['password'],
                settings.DATABASE_CONFIG_DICT['hostname'],
                settings.DATABASE_CONFIG_DICT['port'],
                settings.DATABASE_CONFIG_DICT['database'],
                settings.DATABASE_CONFIG_DICT['sslmode']
            )
