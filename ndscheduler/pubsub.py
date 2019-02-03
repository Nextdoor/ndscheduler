from threading import Event, Timer
from functools import partial


class PubSub:
    _events = {}

    @staticmethod
    def subscribe(key, func, unsubscribe_after=True, timeout=None, timeout_func=None):
        event = Event()
        response = dict()

        if timeout is not None and not unsubscribe_after:
            raise ValueError('timeout can not be used if unsubsubscribe_after == False')

        def callback(event, response, data):
            event.set()
            response['result'] = func(data)

        def timeout_callback():
            timeout_data = timeout_func()
            if key in PubSub._events:
                PubSub._events[key](data=timeout_data)

        PubSub._events[key] = partial(callback, event=event, response=response)
        if timeout is not None:
            Timer(timeout, timeout_callback).start()

        event.wait()
        if unsubscribe_after:
            PubSub.unsubscribe(key)
        return response['result']

    @staticmethod
    def publish(key, data=None):
        PubSub._events[key](data=data)

    @staticmethod
    def unsubscribe(key):
        del PubSub._events[key]
