from singleton import singleton

class Account:
    def __init__(self, username, password, smtp_host, imap_host, uid=-1):
        self.id = uid
        self.username = username
        self.password = password
        self.smtp_host = smtp_host
        self.imap_host = imap_host
        self.imap_client = None

@singleton
class AccountManager:

    def __init__(self):
        self.__next_uid__ = 1 # todo: del later, user id from db
        self.__account_dict__ = {}
        # todo: read current accounts from db

    def addAccount(self, account):
        # todo: db
        account.id = self.__next_uid__
        self.__account_dict__[account.id] = account
        self.__next_uid__ += 1

    def removeAccount(self, uid):
        self.__account_dict__.pop(uid)
        # todo: db

    def getAccount(self, uid):
        return self.__account_dict__[uid]


def getTestAccount():
    return Account('boss_coal@163.com', 'daweige123', 'smtp.163.com', 'imap.163.com')