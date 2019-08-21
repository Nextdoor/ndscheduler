"""Represents Postgres datastore."""

from ndscheduler.corescheduler.datastore import base


class DatastorePostgres(base.DatastoreBase):

    def get_db_url(self) -> str:
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
        return 'postgresql://%s:%s@%s:%d/%s?sslmode=%s' % (
            self.db_config['user'],
            self.db_config['password'],
            self.db_config['hostname'],
            self.db_config['port'],
            self.db_config['database'],
            self.db_config['sslmode'])
