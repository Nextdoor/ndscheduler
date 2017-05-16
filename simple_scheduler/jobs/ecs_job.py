"""A sample job that prints string."""

import time
import logging
import boto3
from ndscheduler import job

logger = logging.getLogger(__name__)

client = boto3.client('ecs')

POLL_TIME = 2


class ECSFailureException(BaseException):
    pass


class ECSResponseException(BaseException):
    pass


class ECSJob(job.JobBase):
    retry_count = 3

    @classmethod
    def meta_info(cls):
        return {
            'job_class_string': '%s.%s' % (cls.__module__, cls.__name__),
            'notes': 'This will execute a AWS ECS RunTask!',
            'arguments': [
                {'type': 'string', 'description': 'ECS Cluster to run on'},
                {'type': 'string', 'description': 'task_def_arn'},
                {'type': 'array[dict]', 'description': 'task_def'},
                {'type': 'string', 'description': 'Directly corresponds to the '
                                                  '`overrides` parameter of runTask API'}
            ],
            'example_arguments': '["ClusterName", None, "arn:aws:ecs:<region>'
                                 ':<user_id>:task-definition/<family>:<tag>", None]'
        }

    def _get_task_statuses(self, task_ids):
        """
        Retrieve task statuses from ECS API

        Returns list of {RUNNING|PENDING|STOPPED} for each id in task_ids
        """
        logger.debug('Get status of task_ids: {}'.format(task_ids))
        response = client.describe_tasks(tasks=task_ids, cluster=self.cluster)

        # Error checking
        if response['failures']:
            raise ECSFailureException('There were some failures:\n{0}'.format(
                response['failures']))
        status_code = response['ResponseMetadata']['HTTPStatusCode']
        if status_code != 200:
            msg = 'Task status request received status code {0}:\n{1}'
            raise ECSResponseException(msg.format(status_code, response))

        return [t['lastStatus'] for t in response['tasks']]

    def get_task_statuses(self, task_ids):
        retries = 0
        while True:
            try:
                return self._get_task_statuses(task_ids)
            except ECSResponseException as e:
                if retries <= self.retry_count:
                    msg = 'Response failed retry attempt {}/{}'.format(retries, self.retry_count)
                    logger.warning(msg)
                    time.sleep(POLL_TIME)
                else:
                    raise

    def _track_tasks(self, task_ids):
        """Poll task status until STOPPED"""
        while True:
            statuses = self.get_task_statuses(task_ids)

            if all([status == 'STOPPED' for status in statuses]):
                logger.info('ECS tasks {0} STOPPED'.format(','.join(task_ids)))
                break
        time.sleep(POLL_TIME)
        logger.debug('ECS task status for tasks {0}: {1}'.format(
            ','.join(task_ids), statuses))

    @property
    def cluster(self):
        if not hasattr(self, '_cluster'):
            logger.warning('Cluster not set!')
            return None
        return self._cluster

    @cluster.setter
    def cluster(self, cluster):
        self._cluster = cluster
        logger.debug('Set Cluster: {}'.format(cluster))

    def run(self, cluster, task_def_arn=None, task_def=None, command=None, *args, **kwargs):
        self.cluster = cluster
        if (not task_def and not task_def_arn) or \
                (task_def and task_def_arn):
            raise ValueError(('Either (but not both) a task_def (dict) or'
                              'task_def_arn (string) must be assigned'))
        if not task_def_arn:
            # Register the task and get assigned taskDefinition ID (arn)
            response = client.register_task_definition(**task_def)
            task_def_arn = response['taskDefinition']['taskDefinitionArn']
        logger.debug('Task Definition ARN: {}'.format(task_def_arn))

        # Submit the task to AWS ECS and get assigned task ID
        # (list containing 1 string)
        if command:
            overrides = {'containerOverrides': command}
        else:
            overrides = {}
        response = client.run_task(taskDefinition=task_def_arn,
                                   overrides=overrides, cluster=self.cluster)
        _task_ids = [task['taskArn'] for task in response['tasks']]

        # Wait on task completion
        self._track_tasks(_task_ids)


if __name__ == "__main__":
    # You can easily test this job here
    job = ECSJob.create_test_instance()
    job.run('ClusterName', "arn:aws:ecs:<region>:<user_id>:task-"
                           "definition/<task_def_name>:<revision_number>")
    job.run('DataETLCluster', None, {
        'family': 'hello-world',
        'volumes': [],
        'containerDefinitions': [
            {
                'memory': 1,
                'essential': True,
                'name': 'hello-world',
                'image': 'ubuntu',
                'command': ['/bin/echo', 'hello world']
            }
        ]
    })
