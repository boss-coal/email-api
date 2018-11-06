from handles.base_handler import BaseHandler, Result
from base import inlineCallbacks, returnValue, defer
from twisted.mail.smtp import sendmail
from email.mime.text import MIMEText
from account_manager import getTestAccount
from imap_smtp.imap import loginImap

class TestHandler(BaseHandler):

    isLeaf = True

    def __init__(self):
        BaseHandler.__init__(self)
        self.account = getTestAccount()

    @inlineCallbacks
    def get(self):
        data = {}
        ret = yield self.loginImap()
        data['imap'] = ret
        ret = yield self.sendMail()
        data['smtp'] = ret
        returnValue(Result(data=data))

    @inlineCallbacks
    def loginImap(self):
        account = self.account
        conn_deferred = defer.Deferred().addCallback(self.onLoginImapSucess)
        loginImap(account.username, account.password, account.imap_host, conn_deferred)
        ret = yield conn_deferred
        returnValue(ret)

    def onLoginImapSucess(self, client):
        return 'login imap success'

    def onLoginImapFailed(self, err):
        return str(err)


    @inlineCallbacks
    def sendMail(self):
        msg = MIMEText('smtp dev')
        msg['Subject'] = 'send mail by twisted' if 'sj' not in self.request.args else self.request.args['sj'][0]
        msg['From'] = self.account.username
        msg['To'] = 'luegg701@163.com'
        ret = yield sendmail(self.account.smtp_host,
                             msg['From'],
                             [msg['To']],
                              msg.as_string(),
                             username=msg['From'],
                             password=self.account.password
                             )
        returnValue(ret)


