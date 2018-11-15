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
        # ret = yield self.loginImap()
        # data['imap'] = ret
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
        msg.as_string()
        # msg['Subject'] = 'send mail by twisted' if 'sj' not in self.request.args else self.request.args['sj'][0]
        msg['From'] = self.account.username
        msg['To'] = 'luegg701@163.com'
        # ret = yield sendmail(self.account.smtp_host,
        #                      msg['From'],
        #                      [msg['To']],
        #                       msg.as_string(),
        #                      username=msg['From'],
        #                      password=self.account.password
        #                      )
        # returnValue(ret)
        data = "From: coal <215731713@qq.com>\r\nTo: =?GBK?B?0KG1trLL?= <boss_coal@163.com>\r\nSubject: image for you\r\nContent-Type: multipart/related; \r\n\tboundary=\"----=_Part_24276_7267963.1541800511585\"\r\nMIME-Version: 1.0\r\n\r\n------=_Part_24276_7267963.1541800511585\r\nContent-Type: multipart/alternative; \r\n\tboundary=\"----=_Part_24277_726350752.1541800511585\"\r\n\r\n------=_Part_24277_726350752.1541800511585\r\nContent-Type: text/plain; charset=GBK\r\nContent-Transfer-Encoding: base64\r\n\r\naGVpIQo=\r\n------=_Part_24277_726350752.1541800511585\r\nContent-Type: text/html; charset=GBK\r\nContent-Transfer-Encoding: base64\r\n\r\nPGRpdiBzdHlsZT0ibGluZS1oZWlnaHQ6MS43O2NvbG9yOiMwMDAwMDA7Zm9udC1zaXplOjE0cHg7\r\nZm9udC1mYW1pbHk6QXJpYWwiPjxkaXY+aGVpITxicj48aW1nIHNyYz0iY2lkOjJjZDc4ZmU0JDEk\r\nMTY2ZmE3OGM4NjEkQ29yZW1haWwkYm9zc19jb2FsJDE2My5jb20iIHN0eWxlPSJ3aWR0aDogMTI4\r\ncHg7IGhlaWdodDogMTI4cHg7IiBvcmd3aWR0aD0iMTI4IiBvcmdoZWlnaHQ9IjEyOCIgZGF0YS1p\r\nbWFnZT0iMSI+PC9kaXY+PC9kaXY+PGJyPjxicj48c3BhbiB0aXRsZT0ibmV0ZWFzZWZvb3RlciI+\r\nPGRpdiBpZD0ibmV0ZWFzZV9tYWlsX2Zvb3RlciI+PGRpdiBzdHlsZT0iYm9yZGVyLXRvcDojQ0ND\r\nIDFweCBzb2xpZDtwYWRkaW5nOjEwcHggNXB4O2ZvbnQtc2l6ZToxNnB4O2NvbG9yOiM3Nzc7bGlu\r\nZS1oZWlnaHQ6MjJweCI+PGEgaHJlZj0iaHR0cDovL2FjdC55b3UuMTYzLmNvbS9hY3QvcHViLzNX\r\nWjhBSlVsRUsuaHRtbD9mcm9tPXdlYl9nZ19tYWlsX2ppYW9iaWFvXzkiIHRhcmdldD0iX2JsYW5r\r\nIiBzdHlsZT0iY29sb3I6IzMzNjZGRjt0ZXh0LWRlY29yYXRpb246bm9uZSI+ob7M4dDRob/E49PQ\r\n0ru49s340tfRz9GhNDUw1KrP1r3wwPGw/LT9wezIoaOhPC9hPgogJm5ic3A7ICZuYnNwOzwvZGl2\r\nPjwvZGl2Pjwvc3Bhbj4=\r\n------=_Part_24277_726350752.1541800511585--\r\n\r\n------=_Part_24276_7267963.1541800511585\r\nContent-Type: image/png; name=\"music.png\"\r\nContent-Transfer-Encoding: base64\r\nContent-Disposition: inline; filename=\"music.png\"\r\nContent-ID: <2cd78fe4$1$166fa78c861$Coremail$boss_coal$163.com>\r\n\r\n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\r\n------=_Part_24276_7267963.1541800511585--\r\n"
        ret = yield sendmail('smtp.qq.com',
                             '215731713@qq.com',
                             ['boss_coal@163.com'],
                             data,
                             username='215731713@qq.com',
                             password='vkcjffgagicnbhhd'
                             )
        returnValue(ret)


