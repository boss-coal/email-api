from twisted.internet import endpoints
from twisted.internet import protocol
from twisted.mail import imap4
from twisted.internet import reactor
import logging
from base import inlineCallbacks
from handles.base_handler import Result

class IMAP4Client(imap4.IMAP4Client):
    def __init__(self, username, password, **kwargs):
        imap4.IMAP4Client.__init__(self)
        self.username = username
        self.password = password
        self.conn_deferred = kwargs.get('conn_deferred', None)


    def serverGreeting(self, caps):
        self.serverCapabilities = caps
        self.insecureLogin()

    @inlineCallbacks
    def insecureLogin(self):
        try:
            ret = yield self.login(self.username, self.password)
            self.onLoginSuccess()
        except Exception, e:
            self.onLoginFailed(e)

    def onLoginSuccess(self):
        logging.debug('on login success')
        if self.conn_deferred:
            self.conn_deferred.callback(self)

    def onLoginFailed(self, err):
        logging.debug(err)
        if self.conn_deferred:
            self.conn_deferred.errback(err)



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


def loginImap(username, password, imap_host, conn_deferred=None):
    username = username.encode('ascii')
    password = password.encode('ascii')
    factory = IMAP4ClientFactory(username, password, conn_deferred=conn_deferred)

    port = 143
    ep = endpoints.HostnameEndpoint(reactor, imap_host, port)
    # if port 993
    # if isinstance(imap_host, bytes):
    #     imap_host = imap_host.decode('utf-8')
    # context_factory = ssl.optionsForClientTLS(hostname=imap_host)
    # ep = endpoints.wrapClientTLS(context_factory, ep)
    ep.connect(factory)


