"""Define database schemas."""

import sqlalchemy

from ndscheduler.corescheduler import utils


#
# Jobs
# It's defined by apscheduler library.
#


def get_execution_table(metadata, tablename):
    return sqlalchemy.Table(
        tablename, metadata,
        sqlalchemy.Column('eid', sqlalchemy.Unicode(191, _warn_on_bytestring=False),
                          primary_key=True),
        sqlalchemy.Column('hostname', sqlalchemy.Text, nullable=True),
        sqlalchemy.Column('pid', sqlalchemy.Integer, nullable=True),
        sqlalchemy.Column('state', sqlalchemy.Integer, nullable=False),
        sqlalchemy.Column('scheduled_time', sqlalchemy.DateTime(timezone=True), nullable=False,
                          default=utils.get_current_datetime),
        sqlalchemy.Column('updated_time', sqlalchemy.DateTime(timezone=True),
                          default=utils.get_current_datetime, onupdate=utils.get_current_datetime),
        sqlalchemy.Column('description', sqlalchemy.Text, nullable=True),
        sqlalchemy.Column('result', sqlalchemy.Text, nullable=True),
        sqlalchemy.Column('job_id', sqlalchemy.Text, nullable=False),
        sqlalchemy.Column('task_id', sqlalchemy.Text, nullable=True))


def get_auditlogs_table(metadata, tablename):
    return sqlalchemy.Table(
        tablename, metadata,
        sqlalchemy.Column('job_id', sqlalchemy.Text, nullable=False),
        sqlalchemy.Column('job_name', sqlalchemy.Text, nullable=False),
        sqlalchemy.Column('event', sqlalchemy.Integer, nullable=False),
        sqlalchemy.Column('user', sqlalchemy.Text, nullable=True),
        sqlalchemy.Column('created_time', sqlalchemy.DateTime(timezone=True), nullable=False,
                          default=utils.get_current_datetime),
        sqlalchemy.Column('description', sqlalchemy.Text, nullable=True))
