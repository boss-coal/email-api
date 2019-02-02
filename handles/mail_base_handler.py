from base_handler import BaseHandler
from base import inlineCallbacks, returnValue
from account_manager import accountManagerInstance

class MailBaseHandler(BaseHandler):

    @inlineCallbacks
    def post(self):
        mail_account_name = self.getArg('mail_account_name')
        self.account = accountManagerInstance.getAccount(mail_account_name)
        if not self.account:
            self.finishWithError(errmsg='no account named %s' % mail_account_name)
        self.mail_proxy = yield self.account.get_mail_proxy()
        ret = yield self.task()
        self.account.give_back_mail_proxy(self.mail_proxy)
        self.mail_proxy = None
        returnValue(ret)

    def task(self):
        self.finishWithError(status=500, errmsg='server internal error: should overwrite task')