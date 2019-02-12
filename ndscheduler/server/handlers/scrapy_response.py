import tornado.concurrent
import tornado.gen
import tornado.web
from ndscheduler.server.handlers import base
from ndscheduler.pubsub import PubSub


class Handler(base.BaseHandler):

    @tornado.web.removeslash
    def post(self):
        jobid = self.json_args['jobid']
        PubSub.publish(jobid, self.json_args)
        self.set_status(200)
        self.write({'result': 'success'})
