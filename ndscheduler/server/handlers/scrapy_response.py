import tornado.concurrent
import tornado.gen
import tornado.web
import json
from ndscheduler.server.handlers import base

class TestHandler(base.BaseHandler):
   
    @tornado.web.removeslash
    def post(self, *args, **kwargs):
        print(self)
        response = {
            'result': self.json_args
        }
        self.set_status(200)
        self.write(response)