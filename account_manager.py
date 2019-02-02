from singleton import singleton
import logging
from imap_smtp.imap import IMAP4Client, loginImap
from imap_smtp.mailproxy import MailProxy
from base import defer, inlineCallbacks, returnValue


class Account(IMAP4Client.LostListener):


    # username is the keyword
    def __init__(self, username, password, smtp_host, imap_host):
        self.id = -1
        self.setting_id = -1
        self.username = username
        self.password = password
        self.smtp_host = smtp_host
        self.imap_host = imap_host
        # self.mail_proxy = None
        # self.connect_deferred = None
        self.idle_proxy_set = set([])
        self.busy_proxy_set = set([])

    def dbFormat(self, with_id=True):
        result = {
            'mail_account_name': self.username,
            'mail_account_psd': self.password,
            'mail_setting_id': self.setting_id
        }
        if with_id:
            result['id'] = self.id
        return result

    @staticmethod
    def fromDb(account):
        ac = Account(account['mail_account_name'], account['mail_account_psd'], '', '')
        ac.id = account['id']
        ac.setting_id = account['mail_setting_id']
        return ac

    @inlineCallbacks
    def get_mail_proxy(self):
        if len(self.idle_proxy_set) == 0:
            yield self.login()
        proxy = self.idle_proxy_set.pop()
        self.busy_proxy_set.add(proxy)
        ret = yield defer.succeed(proxy)
        returnValue(ret)

    def give_back_mail_proxy(self, proxy):
        if proxy in self.busy_proxy_set:
            self.idle_proxy_set.add(proxy)

    def login(self, conn_deferred=None):
        # self.connect_deferred = conn_deferred
        # self.mail_proxy = None
        logging.info('create new client')
        internal_deferred = defer.Deferred().addCallback(self.onLoginImapSuccess, conn_deferred)
        internal_deferred.addErrback(self.onLoginImapFailed, conn_deferred)
        loginImap(self.username, self.password, self.imap_host, conn_deferred=internal_deferred)
        return internal_deferred

    def onLoginImapSuccess(self, client, connect_deferred=None):
        # if self.mail_proxy:
        #     self.mail_proxy.client.setLostListener(None)
        client.setLostListener(self)
        # self.mail_proxy = MailProxy(client)
        proxy = MailProxy(client)
        self.idle_proxy_set.add(proxy)
        logging.debug('%s idle, %s busy', len(self.idle_proxy_set), len(self.busy_proxy_set))
        if connect_deferred:
            connect_deferred.callback(client)

    def onLoginImapFailed(self, err, connect_deferred=None):
        logging.error(err)
        if connect_deferred:
            connect_deferred.errback(err)

    def connected(self):
        return len(self.idle_proxy_set) + len(self.busy_proxy_set) > 0

    @inlineCallbacks
    def onConnectionLost(self, client):
        try:
            remove_item = None
            for item in self.idle_proxy_set:
                if item.client is client:
                    remove_item = item
                    break
            if remove_item:
                self.idle_proxy_set.remove(remove_item)
            remove_item = None
            for item in self.busy_proxy_set:
                if item.client is client:
                    remove_item = item
                    break
            if remove_item:
                self.busy_proxy_set.remove(remove_item)
        finally:
            if not self.connected():
                yield self.login()


@singleton
class AccountManager:

    def __init__(self):
        self.__account_dict__ = {}

    def updateAccount(self, account):
        if account.username in self.__account_dict__:
            logging.info('account{%s} has existed, update the detail' % account.username)
        self.__account_dict__[account.username] = account

    def removeAccount(self, username):
        self.__account_dict__.pop(username)

    def getAccount(self, username):
        return self.__account_dict__.get(username, None)


accountManagerInstance = AccountManager()