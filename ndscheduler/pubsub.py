from threading import Event, Timer
from functools import partial


class PubSub:
    _events = {}

    @staticmethod
    def subscribe(key, func, unsubscribe_after=True, timeout=None, timeout_func=None):
        if timeout is not None and not unsubscribe_after:
            raise ValueError('timeout can not be used if unsubsubscribe_after == False')

        def callback(event, response, data, timeout_timer):
            if timeout_timer is not None:
                timeout_timer.cancel()
            event.set()
            response['result'] = func(data)

        def timeout_callback():
            timeout_data = timeout_func()
            if key in PubSub._events:
                PubSub._events[key](data=timeout_data)

        event = Event()
        response = dict()
        timeout_timer = None
        if timeout is not None:
            timeout_timer = Timer(timeout, timeout_callback)
            timeout_timer.start()

        PubSub._events[key] = partial(callback, event=event, response=response,
                                      timeout_timer=timeout_timer)

        event.wait()
        if unsubscribe_after:
            PubSub.unsubscribe(key)
        return response['result']

    @staticmethod
    def publish(key, data=None):
        if key in PubSub._events:
            PubSub._events[key](data=data)
        else:
            raise Exception(f'Tried to publish key {key} but no subscribers were found. '
                            'It''s possible that the subscriber timeout value needs to be '
                            'increased f one was supplied.')

    @staticmethod
    def unsubscribe(key):
        del PubSub._events[key]
