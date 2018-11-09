from twisted.web.resource import Resource
from twisted.internet import defer
from twisted.internet.defer import inlineCallbacks, returnValue
from twisted.web import server
import json, logging

class Result:
    def __init__(self, status=0, errmsg='', extend=None, **kwargs):
        self.status = status
        self.errmsg = errmsg
        self.result = {
            'status': status,
            'errmsg': errmsg
        }
        if extend and isinstance(extend, dict):
            self.result.update(extend)

        if kwargs:
            self.result.update(kwargs)

    def extend(self, **kwargs):
        self.result.update(kwargs)

    def dumps(self):
        return json.dumps(self.result, ensure_ascii=False)


class CustomError:
    def __init__(self, err, result=Result(-1, 'unknown error')):
        self.err = err
        self.result = result


class BaseHandler(Resource):
    isLeaf = True

    def __init__(self):
        Resource.__init__(self)
        self.request = None

    def finish(self, result):
        self.request.setHeader('Content-type', 'application/json; charset=utf-8')
        if isinstance(result, dict):
            result = Result(extend=result)
        elif isinstance(result, list) or isinstance(result, tuple):
            result = Result(data=result)
        elif not isinstance(result, Result):
            result = Result(errmsg='server error: wrong result fromat')
        self.request.write(result.dumps())
        self.request.finish()
        self.request = None

    def finishWithError(self, status=-1, errmsg='unknown error', err=None):
        raise CustomError(err, Result(status, errmsg))

    def render_GET(self, request):
        return self.render_POST(request)

    def render_POST(self, request):
        logging.debug('request:%s' % self)
        self.request = request
        d = self.post()
        d.addCallback(self.finish).addErrback(self.onError)
        return server.NOT_DONE_YET

    def onError(self, err):
        if isinstance(err.value, CustomError):
            self.finish(err.value.result)
            return
        logging.error(err)
        self.finish(Result(status=1, errmsg=str(err)))

    def getArg(self, key, necessary=True, default=None, arg_range=None):
        if necessary and key not in self.request.args:
            self.finishWithError(errmsg='argument \'%s\' is necessary' % key)
        arg = self.request.args.get(key, default)
        if arg and len(arg) == 1:
            arg = arg[0]
        if arg_range and arg not in arg_range:
            self.finishWithError(errmsg='argument \'%s\' should be one of %s' % (key, arg_range))
        return arg

    # @post should return {Result} or {dict}
    @inlineCallbacks
    def post(self):
        result = yield defer.succeed(Result(msg='post success'))
        returnValue(result)


