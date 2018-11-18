from base_handler import BaseHandler, Result, CustomError
from base import inlineCallbacks, returnValue, defer
from imap_smtp.imap import loginImap
from account_manager import accountManagerInstance, Account
from imap_smtp.mailproxy import MailProxy
import logging

class BaseAuthHandler(BaseHandler):

    @inlineCallbacks
    def getSetting(self, setting_id):
        settings = yield self.mail_dao.query_server_setting(id=setting_id)
        if not settings:
            self.finishWithError(errmsg='has no setting with id: %s' % setting_id)
        returnValue(settings[0])

class AuthLoginedHandler(BaseAuthHandler):

    @inlineCallbacks
    def post(self):
        self.login_result = []
        accounts = yield self.mail_dao.query_mail_account()
        if not accounts:
            res = yield defer.succeed(Result(msg="no logined account"))
            returnValue(res)

        self.all_deferred = defer.Deferred().addCallback(self.onCheckAll)
        self.rest = len(accounts)
        for i, account in enumerate(accounts):
            ac = Account.fromDb(account)
            setting = yield self.getSetting(account['mail_setting_id'])
            ac.imap_host = setting['imap_server_host']
            ac.smtp_host = setting['smtp_server_host']
            accountManagerInstance.updateAccount(ac)
            self.login_result.append(None)
            conn_deferred = defer.Deferred().addCallback(self.onLoginImapSuccess, ac, i)
            conn_deferred.addErrback(self.onLoginImapFail, ac, i)
            ac.login(conn_deferred)
        yield self.all_deferred

        returnValue(Result(result=self.login_result))

    def checkedOne(self):
        self.rest -= 1
        if self.rest == 0:
            self.all_deferred.callback(None)

    def onCheckAll(self, useless):
        logging.debug('check all')

    def onLoginImapSuccess(self, client, account, index):
        self.login_result[index] = {
            'id': account.id,
            'account_name': account.username,
            'result': 0
        }
        self.checkedOne()

    def onLoginImapFail(self, err, account, index):
        self.login_result[index] = {
            'id': account.id,
            'account_name': account.username,
            'result': -1,
            'errmsg': 'login failed: %s' % err.value
        }
        logging.error(self.login_result[index])
        logging.error(err)
        self.checkedOne()



class AuthLoginHandler(BaseAuthHandler):

    # request args:
    # @mail_account_name(string)
    # @mail_account_psd(string)
    # @mail_setting_id(string)
    # @relogin(bool) {optional}
    @inlineCallbacks
    def post(self):
        self.error_res = None

        conn_deferred = defer.Deferred().addCallback(self.onLoginImapSuccess)
        conn_deferred.addErrback(self.onLoginImapFailed)

        mail_account_name = self.getArg('mail_account_name')
        account = accountManagerInstance.getAccount(mail_account_name)
        try:
            if account:
                if account.connected():
                    returnValue({'msg': 'already connected'})
                if self.getArg('relogin', necessary=False, default=False):
                    account.login(conn_deferred=conn_deferred)
                    yield conn_deferred
                    if account.connected():
                        returnValue({'msg': 'relogin success'})

            mail_account_psd = self.getArg('mail_account_psd')
            mail_setting_id = int(self.getArg('mail_setting_id'))
            mail_setting = yield self.getSetting(mail_setting_id)

            if account:
                account.smtp_host = mail_setting['smtp_server_host']
                account.imap_host = mail_setting['imap_server_host']
                account.password = mail_account_psd
                yield self.mail_dao.update_mail_account(account.dbFormat())
            else:
                account = Account(mail_account_name, mail_account_psd,
                                  mail_setting['smtp_server_host'],
                                  mail_setting['imap_server_host'])
                account.setting_id = mail_setting_id
                account.id = yield self.mail_dao.add_mail_account(mail_account_name, mail_account_psd, mail_setting_id)
            accountManagerInstance.updateAccount(account)

            account.login(conn_deferred=conn_deferred)
            yield conn_deferred

            if account.connected():
                returnValue({'msg': 'login imap server success', 'id': account.id})

        except CustomError, e:
            returnValue(e.result)
        except Exception, e:
            logging.error(e)

        returnValue({'errmsg': 'unknown error'})


    def onLoginImapSuccess(self, client):
        pass

    def onLoginImapFailed(self, err):
        logging.error(err)
        self.finishWithError(errmsg='login imap server failed: %s' % err.value)

