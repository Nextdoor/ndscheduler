"""Represents Postgres datastore."""
import sys
from ndscheduler.corescheduler.datastore import base


class DatastorePostgres(base.DatastoreBase):

    def get_db_url(self):
        """Returns the db url to establish a Postgres connection, where db_config is passed in
        on initialization as:
        {
            'user': 'my_user',
            'password': 'my_password',
            'hostname': 'db.hostname.com',
            'port': 8888,
            'database': 'my_db',
            'sslmode': 'disable'
        }
        :return: string db url
        """

        # Work under Pypy, which doesn't have the default psycopg2
        if '__pypy__' in sys.builtin_module_names:
            db_wrapper = 'postgresql+psycopg2cffi'
        else:
            db_wrapper = 'postgresql'

        return '%s://%s:%s@%s:%d/%s?sslmode=%s' % (
            db_wrapper,
            self.db_config['user'],
            self.db_config['password'],
            self.db_config['hostname'],
            self.db_config['port'],
            self.db_config['database'],
            self.db_config['sslmode'])
