from singleton import singleton
import logging

class Account:

    # username is the keyword
    def __init__(self, username, password, smtp_host, imap_host):
        self.username = username
        self.password = password
        self.smtp_host = smtp_host
        self.imap_host = imap_host
        self.mail_proxy = None

@singleton
class AccountManager:

    def __init__(self):
        self.__account_dict__ = {}
        # todo: read current accounts from db

    def addAccount(self, account):
        # todo: db
        if account.username in self.__account_dict__:
            logging.warn('account{%s} has existed' % account.username)
        self.__account_dict__[account.username] = account

    def removeAccount(self, username):
        self.__account_dict__.pop(username)
        # todo: db

    def getAccount(self, username):
        return self.__account_dict__.get(username, None)


accountManagerInstance = AccountManager()