from handles.base_handler import BaseHandler, Result
from base import inlineCallbacks, returnValue, defer
from twisted.mail.smtp import sendmail
from email.mime.text import MIMEText
from conf.test_data import getTestAccount
from imap_smtp.imap import loginImap
import logging

class TestHandler(BaseHandler):

    isLeaf = True

    def __init__(self):
        BaseHandler.__init__(self)
        self.account = getTestAccount()

    @inlineCallbacks
    def post(self):
        data = {}
        ret = yield self.loginImap()
        data['imap'] = ret
        ret = yield self.sendMail()
        data['smtp'] = ret
        returnValue(Result(data=data))

    # def render_GET(self, request):
    #     return '''
    #     <!Doctype html>
    #     <html>
    #     <head>
    #     <meta charset='utf-8'>
    #     <script
		# 	  src="https://code.jquery.com/jquery-2.2.4.min.js"
		# 	  integrity="sha256-BbhdlvQf/xTY9gja0Dq3HiwQF8LaCRTXxZKRutelT44="
		# 	  crossorigin="anonymous"></script>
		# </head>
    #     <form id="uploadForm" enctype="multipart/form-data">
    #         <input id="file" type="file" name="file"/>
    #         <button id="upload" type="button" onclick="foo()">upload</button>
    #     </form>
    #     <script>
    #     function foo(){
    #         $.ajax({
    #                 url: "/mail/send_mail",
    #                 type: 'POST',
    #                 cache: false,
    #                 data: new FormData($("#uploadForm")[0]),
    #                 processData: false,
    #                 contentType: false,
    #                 success: function (result) {
    #                 },
    #                 error: function (err) {
    #                 }
    #             });
    #     }
    #     </script>
    #     </html>
    #     '''

    @inlineCallbacks
    def loginImap(self):
        account = self.account
        conn_deferred = defer.Deferred().addCallback(self.onLoginImapSuccess)
        loginImap(account.username, account.password, account.imap_host, conn_deferred)
        ret = yield conn_deferred
        returnValue(ret)

    def onLoginImapSudcess(self, client):
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


