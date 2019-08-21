"""Constants used in corescheduler library."""

#
# Database settings
#
DEFAULT_JOBS_TABLENAME = 'scheduler_jobs'
DEFAULT_EXECUTIONS_TABLENAME = 'scheduler_execution'
DEFAULT_AUDIT_LOGS_TABLENAME = 'scheduler_jobauditlog'

#
# APScheduler Settings
#
DEFAULT_THREAD_POOL_SIZE = 4
DEFAULT_JOB_MAX_INSTANCES = 3
DEFAULT_JOB_COALESCE = True
DEFAULT_TIMEZONE = 'UTC'

# When a job is misfired -- A job were to run at a specific time, but due to some
# reason (e.g., scheduler restart), we miss that run.
#
# By default, if a job is misfired within 1 hour, the scheduler will rerun it.
# Otherwise, if it's misfired over 1 hour, the scheduler will not rerun it.
DEFAULT_JOB_MISFIRE_GRACE_SEC = 3600

#
# Execution status
#
EXECUTION_STATUS_SCHEDULED = 0
EXECUTION_STATUS_RUNNING = 1
EXECUTION_STATUS_STOPPING = 2
EXECUTION_STATUS_STOPPED = 3
EXECUTION_STATUS_FAILED = 4
EXECUTION_STATUS_SUCCEEDED = 5
EXECUTION_STATUS_TIMEOUT = 6
EXECUTION_STATUS_SCHEDULED_ERROR = 7

EXECUTION_STATUS_DICT = {
    EXECUTION_STATUS_SCHEDULED: 'scheduled',
    EXECUTION_STATUS_RUNNING: 'running',
    EXECUTION_STATUS_STOPPING: 'stopping',
    EXECUTION_STATUS_STOPPED: 'stopped',
    EXECUTION_STATUS_FAILED: 'failed',
    EXECUTION_STATUS_SUCCEEDED: 'succeeded',
    EXECUTION_STATUS_TIMEOUT: 'timeout',
    EXECUTION_STATUS_SCHEDULED_ERROR: 'scheduled error'
}

#
# Audit logs status
#
AUDIT_LOG_ADDED = 0
AUDIT_LOG_MODIFIED = 1
AUDIT_LOG_DELETED = 2
AUDIT_LOG_PAUSED = 3
AUDIT_LOG_RESUMED = 4
AUDIT_LOG_CUSTOM_RUN = 5

AUDIT_LOG_DICT = {
    AUDIT_LOG_ADDED: 'added',
    AUDIT_LOG_MODIFIED: 'modified',
    AUDIT_LOG_DELETED: 'deleted',
    AUDIT_LOG_PAUSED: 'paused',
    AUDIT_LOG_RESUMED: 'resumed',
    AUDIT_LOG_CUSTOM_RUN: 'custom_run'
}
