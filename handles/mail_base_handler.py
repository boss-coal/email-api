from base_handler import BaseHandler
from base import inlineCallbacks, returnValue, accountManagerInstance

class MailBaseHandler(BaseHandler):

    @inlineCallbacks
    def post(self):
        mail_account_name = self.getArg('mail_account_name')
        self.account = accountManagerInstance.getAccount(mail_account_name)
        if not self.account:
            self.finishWithError(errmsg='no account named %s' % mail_account_name)
        self.mail_proxy = self.account.mail_proxy
        ret = yield self.task()
        returnValue(ret)

    def task(self):
        self.finishWithError(status=500, errmsg='server internal error: should overwrite task')