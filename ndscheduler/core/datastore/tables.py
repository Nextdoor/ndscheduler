"""Define database schemas."""

import sqlalchemy

from ndscheduler import settings
from ndscheduler import utils

METADATA = sqlalchemy.MetaData()

#
# Jobs
# It's defined by apscheduler library.
#

#
# Executions
#
EXECUTIONS = sqlalchemy.Table(
    settings.EXECUTIONS_TABLENAME, METADATA,
    sqlalchemy.Column('eid', sqlalchemy.Text, primary_key=True),
    sqlalchemy.Column('hostname', sqlalchemy.Text, nullable=True),
    sqlalchemy.Column('pid', sqlalchemy.Integer, nullable=True),
    sqlalchemy.Column('state', sqlalchemy.Integer, nullable=False),
    sqlalchemy.Column('scheduled_time', sqlalchemy.DateTime(timezone=True), nullable=False,
                      default=utils.get_current_datetime),
    sqlalchemy.Column('updated_time', sqlalchemy.DateTime(timezone=True),
                      nullable=True, onupdate=utils.get_current_datetime),
    sqlalchemy.Column('description', sqlalchemy.Text, nullable=True),
    sqlalchemy.Column('job_id', sqlalchemy.Text, nullable=False),
    sqlalchemy.Column('task_id', sqlalchemy.Text, nullable=True))

#
# Audit logs
#
AUDIT_LOGS = sqlalchemy.Table(
    settings.AUDIT_LOGS_TABLENAME, METADATA,
    sqlalchemy.Column('job_id', sqlalchemy.Text, nullable=False),
    sqlalchemy.Column('job_name', sqlalchemy.Text, nullable=False),
    sqlalchemy.Column('event', sqlalchemy.Integer, nullable=False),
    sqlalchemy.Column('user', sqlalchemy.Text, nullable=True),
    sqlalchemy.Column('created_time', sqlalchemy.DateTime(timezone=True), nullable=False,
                      default=utils.get_current_datetime),
    sqlalchemy.Column('description', sqlalchemy.Text, nullable=True))
