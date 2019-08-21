"""Represents MySQL datastore."""

from ndscheduler.corescheduler.datastore import base


class DatastoreMySQL(base.DatastoreBase):

    def get_db_url(self):
        """Returns the db url to establish a MySQL connection, where db_config is passed in
        on initialization as:
        {
            'user': 'my_user',
            'password': 'my_password',
            'hostname': 'db.hostname.com',
            'port': 8888,
            'database': 'my_db'
        }
        :return: string db url
        """
        return 'mysql+pymysql://%s:%s@%s:%d/%s' % (
            self.db_config['user'],
            self.db_config['password'],
            self.db_config['hostname'],
            self.db_config['port'],
            self.db_config['database'])
