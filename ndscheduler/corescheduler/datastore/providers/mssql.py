"""Represents MySQL datastore."""

from ndscheduler.corescheduler.datastore import base


class DatastoreMsSQL(base.DatastoreBase):

    def get_db_url(self):
        """Returns the db url to establish a Microsoft SQL connection, where db_config is passed in
        on initialization as:
        {
            'user': 'my_user',
            'password': 'my_password',
            'hostname': 'db.hostname.com',
            'database': 'my_db'
        }
        :return: string db url
        """
        return 'mssql+pyodbc://%s:%s@%s/%s?driver=SQL+Server+Native+Client+10.0' % (
            self.db_config['user'],
            self.db_config['password'],
            self.db_config['hostname'],
            self.db_config['database'])
