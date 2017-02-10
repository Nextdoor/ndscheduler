# Datastores

ndscheduler uses [SQLAlchemy](http://www.sqlalchemy.org/) to do database operations. 
Theoretically ndscheduler supports all databases that [SQLAlchemy](http://www.sqlalchemy.org/) supports.

For now, we've tested 3 different databases as the ndscheduler datastore, including SQLite (default), PostgreSQL and MySQL.

To use a specific database, you need to define two variables in the settings file:
* DATABASE_CLASS: the database class to use
* DATABASE_CONFIG_DICT: the parameters used to connect to the database

Please see [default_settings.py](https://github.com/Nextdoor/ndscheduler/blob/master/ndscheduler/default_settings.py#L55) for example.
