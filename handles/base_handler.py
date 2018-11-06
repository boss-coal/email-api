from twisted.web.resource import Resource
from twisted.internet import defer
from twisted.internet.defer import inlineCallbacks, returnValue
from twisted.web import server
import json

class Result:
    def __init__(self, result=0, msg='', data=None):
        self.result = result
        self.msg = msg
        self.data = data

    def dumps(self):
        return json.dumps({
            'result': self.result,
            'msg': self.msg,
            'data': self.data
        }, ensure_ascii=False)


class CustomError:
    def __init__(self, err, result=Result(-1, 'unknown error')):
        self.err = err
        self.result = result


class BaseHandler(Resource):

    def __init__(self):
        Resource.__init__(self)
        self.request = None

    def finish(self, result):
        self.request.setHeader('Content-type', 'application/json; charset=utf-8')
        self.request.write(result.dumps())
        self.request.finish()
        self.request = None

    def render_GET(self, request):
        self.request = request
        d = self.get()
        d.addCallback(self.finish)
        return server.NOT_DONE_YET

    def render_POST(self, request):
        self.request = request
        d = self.post()
        d.addCallback(self.finish)
        return server.NOT_DONE_YET


    @inlineCallbacks
    def get(self):
        result = yield defer.succeed(Result(msg='get success'))
        returnValue(result)


    @inlineCallbacks
    def post(self):
        result = yield defer.succeed(Result(msg='post success'))
        returnValue(result)


