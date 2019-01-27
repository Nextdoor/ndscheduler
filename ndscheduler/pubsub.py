from threading import Event
from functools import partial

class PubSub:
    _events = {}
    @staticmethod
    def subscribe(key, func, unsubscribe_after=True):
        event = Event()
        response = dict()

        def callback(event, response, data):
            event.set()
            response['result'] = func(data)

        PubSub._events[key] = partial(callback, event=event, response=response)
        
        event.wait()
        print('awaited event')
        if unsubscribe_after:
            PubSub.unsubscribe(key)
        print('resturning ' + str(response))    
        return response
    
    @staticmethod
    def publish(key, data=None):
        print('publishing ' + key)
        PubSub._events[key](data=data)

    @staticmethod
    def unsubscribe(key):
        del PubSub._events[key]