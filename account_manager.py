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
        self.mail_proxy = None
        self.connect_deferred = None

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

    def login(self, conn_deferred=None):
        self.connect_deferred = conn_deferred
        self.mail_proxy = None
        internal_deferred = defer.Deferred().addCallback(self.onLoginImapSuccess)
        internal_deferred.addErrback(self.onLoginImapFailed)
        loginImap(self.username, self.password, self.imap_host, conn_deferred=internal_deferred)
        return internal_deferred

    def onLoginImapSuccess(self, client):
        if self.mail_proxy:
            self.mail_proxy.client.setLostListener(None)
        client.setLostListener(self)
        self.mail_proxy = MailProxy(client)
        if self.connect_deferred:
            self.connect_deferred.callback(client)
            self.connect_deferred = None

    def onLoginImapFailed(self, err):
        logging.error(err)
        if self.connect_deferred:
            self.connect_deferred.errback(err)
            self.connect_deferred = None

    def connected(self):
        return not not self.mail_proxy


    @inlineCallbacks
    def onConnectionLost(self):
        self.mail_proxy = None
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