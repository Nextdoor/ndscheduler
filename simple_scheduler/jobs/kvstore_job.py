"""A sample job that prints string."""

from ndscheduler import job
from ndscheduler.utils import get_datastore_instance


class KVStoreJob(job.JobBase):

    @classmethod
    def meta_info(cls):
        return {
            'job_class_string': '%s.%s' % (cls.__module__, cls.__name__),
            'notes': 'This will print a string in your shell. Check it out! And it save the string in a key/value store.',
            'arguments': [
                # argument1
                {'type': 'string', 'description': 'First argument'},

                # argument2
                {'type': 'string', 'description': 'Second argument'}
            ],
            'example_arguments': '["first argument AAA", "second argument BBB"]'
        }

    def run(self, argument1, argument2, *args, **kwargs):
        print('Hello from AwesomeJob! Argument1: %s, Argument2: %s' % (argument1, argument2))
        datastore = get_datastore_instance()
        datastore.add_keyvalue("sample job with storage", argument1, argument2)
        return [argument1, argument2]


if __name__ == "__main__":
    # You can easily test this job here
    job = KVStoreJob.create_test_instance()
    job.run(123, 456)
