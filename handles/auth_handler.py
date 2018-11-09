from base_handler import BaseHandler, Result
from base import inlineCallbacks, returnValue, defer
from imap_smtp.imap import loginImap
from account_manager import accountManagerInstance, Account
from imap_smtp.mailproxy import MailProxy
from conf import test_data
import logging

class AuthoLoginedHandler(BaseHandler):

    @inlineCallbacks
    def post(self):
        self.login_result = []
        # todo: get real logined user
        accounts = test_data.getTestLoginedAccounts()
        if not accounts:
            res = yield defer.succeed(Result(msg="no logined account"))
            returnValue(res)

        self.all_deferred = defer.Deferred().addCallback(self.onCheckAll)
        self.rest = len(accounts)
        for i, account in enumerate(accounts):
            self.login_result.append(None)
            conn_deferred = defer.Deferred().addCallback(self.onLoginImapSuccess, account, i)
            conn_deferred.addErrback(self.onLoginImapFail, account, i)
            loginImap(account.username, account.password, account.imap_host, conn_deferred)
        yield self.all_deferred

        returnValue(Result(result=self.login_result))

    def checkedOne(self):
        self.rest -= 1
        if self.rest == 0:
            self.all_deferred.callback(None)

    def onCheckAll(self, useless):
        logging.debug('check all')

    def onLoginImapSuccess(self, client, account, index):
        account.mail_proxy = MailProxy(client)
        self.login_result[index] = {
            'account_name': account.username,
            'result': 0
        }
        accountManagerInstance.addAccount(account)
        self.checkedOne()


    def onLoginImapFail(self, err, account, index):
        self.login_result[index] = {
            'account_name': account.username,
            'result': -1,
            'errmsg': 'login failed: %s' % err.value
        }
        logging.error(self.login_result[index])
        logging.error(err)
        self.checkedOne()



class AuthLoginHandler(BaseHandler):

    # request args:
    # @mail_account_name
    # @mail_account_psd
    # @mail_setting_id
    @inlineCallbacks
    def post(self):
        self.imap_client = None

        mail_account_name = self.getArg('mail_account_name')
        mail_account_psd = self.getArg('mail_account_psd')
        mail_setting_id = int(self.getArg('mail_setting_id'))

        # todo: get real setting
        mail_setting = test_data.getTestSetting(mail_setting_id)

        conn_deferred = defer.Deferred().addCallback(self.onLoginImapSuccess)
        conn_deferred.addErrback(self.onLoginImapFailed)
        loginImap(mail_account_name, mail_account_psd,
                        mail_setting['imap_server_host'],
                        conn_deferred)
        yield conn_deferred

        res = Result()
        # if conn success, client will be assigned
        if self.imap_client:
            account = Account(mail_account_name, mail_account_psd,
                              mail_setting['smtp_server_host'],
                              mail_setting['imap_server_host'])
            account.mail_proxy = MailProxy(self.imap_client)
            accountManagerInstance.addAccount(account)
            res.extend(msg='login imap server success')
        else:
            res.status = -1
            res.errmsg = 'login imap server failed: unknown error'
        returnValue(res)


    def onLoginImapSuccess(self, client):
        self.imap_client = client


    def onLoginImapFailed(self, err):
        logging.error(err)
        self.finishWithError(errmsg='login imap server failed: %s' % err.value)

