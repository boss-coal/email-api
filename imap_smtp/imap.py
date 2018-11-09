from twisted.internet import endpoints
from twisted.internet import protocol
from twisted.mail import imap4
from twisted.internet import reactor
import logging
from base import inlineCallbacks
from twisted.internet import ssl
from flanker import mime

msg = mime.from_string('abc')

class IMAP4Client(imap4.IMAP4Client):
    def __init__(self, username, password, **kwargs):
        imap4.IMAP4Client.__init__(self)
        self.username = username
        self.password = password
        self.conn_deferred = kwargs.get('conn_deferred', None)


    def serverGreeting(self, caps):
        logging.debug('caps: %s' % caps)
        self.serverCapabilities = caps
        self.insecureLogin()

    def newMessages(self, exists, recent):
        logging.debug('new messages {exists: %s, recent: %s}' % (exists, recent))

    def flagsChanged(self, newFlags):
        logging.debug('flags changed: %s' % newFlags)

    @inlineCallbacks
    def connectionLost(self, reason):
        logging.debug('connection lost: %s' % reason)
        # re-login
        # yield self.insecureLogin()

    def timeoutConnection(self):
        logging.debug('client timeout')


    @inlineCallbacks
    def insecureLogin(self):
        try:
            ret = yield self.login(self.username, self.password)
            self.onLoginSuccess()
        except Exception, e:
            self.onLoginFailed(e)

    @inlineCallbacks
    def onLoginSuccess(self):
        logging.debug('on login success')
        if self.conn_deferred:
            self.conn_deferred.callback(self)
            self.conn_deferred = None
        # lines = yield self.noop()
        # logging.debug('noop: %s' % lines)

    def onLoginFailed(self, err):
        logging.debug(err)
        if self.conn_deferred:
            self.conn_deferred.errback(err)
            self.conn_deferred = None



class IMAP4ClientFactory(protocol.ClientFactory):
    usedUp = False

    protocol = IMAP4Client

    def __init__(self, username, password, **kwargs):
        self.p = self.protocol(username, password, **kwargs)
        self.conn_deferred = kwargs.get('conn_deferred', None)

    def buildProtocol(self, addr):
        p = self.p
        p.factory = self

        p.registerAuthenticator(imap4.PLAINAuthenticator(p.username))
        p.registerAuthenticator(imap4.LOGINAuthenticator(p.username))
        p.registerAuthenticator(
                imap4.CramMD5ClientAuthenticator(p.username))
        self.p = None
        return p

    def clientConnectionFailed(self, connector, reason):
        if self.conn_deferred:
            self.conn_deferred.errback(reason)
            self.conn_deferred = None


def loginImap(username, password, imap_host, conn_deferred=None, port=143):
    username = username.encode('ascii')
    password = password.encode('ascii')
    factory = IMAP4ClientFactory(username, password, conn_deferred=conn_deferred)

    ep = endpoints.HostnameEndpoint(reactor, imap_host, port)
    if port == 993:
        if isinstance(imap_host, bytes):
            imap_host = imap_host.decode('utf-8')
        context_factory = ssl.optionsForClientTLS(hostname=imap_host)
        ep = endpoints.wrapClientTLS(context_factory, ep)
    ep.connect(factory)


