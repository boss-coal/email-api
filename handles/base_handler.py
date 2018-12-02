# -*- coding: utf-8 -*-
from twisted.web.resource import Resource
from twisted.internet import defer
from twisted.internet.defer import inlineCallbacks, returnValue
from twisted.web import server
import json, logging
from db.dao import MailDao

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
        ret = json.dumps(self.result, ensure_ascii=False)
        if isinstance(ret, unicode):
            ret = ret.encode('utf-8')
        return ret


class CustomError:
    def __init__(self, err, result=Result(-1, 'unknown error')):
        self.err = err
        self.result = result


class BaseHandler(Resource):
    isLeaf = True
    # mail_dao = MailDao()

    def __init__(self):
        Resource.__init__(self)
        self.request = None
        self.mail_dao = MailDao()

    def finish(self, result):
        self.request.setHeader('Content-type', 'application/json; charset=utf-8')
        self.request.setHeader('Access-Control-Allow-Origin', '*')
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
        args = self.request.args
        if necessary and key not in args:
            self.finishWithError(errmsg='argument \'%s\' is necessary' % key)
        if key in args:
            arg = args[key]
            if arg and len(arg) == 1:
                arg = arg[0]
        else:
            arg = default
        if arg_range and arg not in arg_range:
            self.finishWithError(errmsg='argument \'%s\' should be one of %s' % (key, arg_range))
        return arg

    # @post should return {Result} or {dict}
    @inlineCallbacks
    def post(self):
        result = yield defer.succeed(Result(msg='post success'))
        returnValue(result)

    def loadsJsonArg(self, arg):
        arg = json.loads(arg)
        for k, v in arg.items():
            if isinstance(v, unicode):
                arg[k] = v.encode('utf-8')
        return arg


