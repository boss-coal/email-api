from base import inlineCallbacks, returnValue, defer
from mail_base_handler import MailBaseHandler
from twisted.mail.smtp import sendmail
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
import json
import logging

class GetMailBoxListHandler(MailBaseHandler):

    @inlineCallbacks
    def task(self):
        result = yield self.mail_proxy.queryBoxList()
        returnValue({'data': result})



class GetMailListHandler(MailBaseHandler):

    @inlineCallbacks
    def task(self):
        mailbox = self.getArg('mailbox')
        result = yield self.mail_proxy.queryMailList(mailbox)
        returnValue(result)


class GetMailContentHandler(MailBaseHandler):

    @inlineCallbacks
    def task(self):
        message_uid = self.getArg('message_uid')
        result = yield self.mail_proxy.queryMailDetail(message_uid)
        # todo: to be confirmed, result should be parsed by client or server
        returnValue(result)


class TagMailListHandler(MailBaseHandler):

    @inlineCallbacks
    def task(self):
        message_uid = self.getArg('message_uid')
        mailbox = self.getArg('mailbox')
        op = self.getArg('op', arg_range=('read', 'unread', 'del'))
        if op == 'read':
            yield self.mail_proxy.readMail(mailbox, message_uid)
        elif op == 'unread':
            yield self.mail_proxy.readMail(mailbox, message_uid, False)
        elif op == 'del':
            yield self.mail_proxy.deleteMessage(mailbox, message_uid)
        else:
            self.finishWithError()

        returnValue({'msg': 'operation success'})


class SendMailHandler(MailBaseHandler):

    @inlineCallbacks
    def task(self):
        headers = self.getArg('headers')
        headers = json.loads(headers, encoding='utf-8')
        parts = self.getArg('parts')
        parts = json.loads(parts, encoding='utf-8')
        if not isinstance(parts, list):
            parts = [parts]
        message_parts = []
        for part in parts:
            if part['type'] in ('plain', 'html'):
                msg_part = MIMEText(part['content'], part['type'], 'utf-8')
            elif part['type'] == 'attachment':
                msg_part = MIMEText(open(part['file_path'], 'rb').read(), 'base64', 'utf-8')
                msg_part['Content-Type'] = 'application/octet-stream'
                msg_part['Content-Disposition'] = 'attachment; filename="%s"' % part['filename']
            elif part['type'] == 'html-img':
                msg_part = MIMEMultipart('alternative')
                content_child = MIMEText(part['content'], 'html', 'utf-8')
                msg_part.attach(content_child)
                for img in part['img_path']:
                    img_child = MIMEText(open(img, 'rb').read())
                    img_child.add_header('Content-ID', '<%s>' % part['img_cid'])
                    msg_part.attach(img_child)
            else:
                self.finishWithError()
            message_parts.append(msg_part)
        if len(message_parts) == 1:
            message = message_parts[0]
        else:
            message = MIMEMultipart()
            for part in message_parts:
                message.attach(part)
        for k, v in headers:
            message[k] = v

        receivers = self.getArg('receivers')
        if not isinstance(receivers, list):
            receivers = [receivers]
        if len(receivers) > 1 and self.getArg('mode',necessary=False) == 'single':
            self.rest = len(receivers)
            self.res = []
            self.all_deferred = defer.Deferred().addCallback(self.onCheckAll)
            for rec in receivers:
                deferred = self.sendMail(message, [rec])
                deferred.addCallback(self.onSingleSendSuccess, rec)
                deferred.addErrback(self.onSingleSendFailed, rec)
            yield self.all_deferred
        else:
            yield self.sendMail(message, receivers)
            self.res = {'msg': 'sent successfully'}
        returnValue(self.res)


    def sendMail(self, message, receivers):
        return sendmail(self.account.smtp_host, self.account.username, receivers, message.as_string(),
                 username=self.account.username, password=self.account.password)

    def onSingleSendSuccess(self, rec):
        self.res.append((rec, 0, 'success'))
        self.checkedOne()

    def onSingleSendFailed(self, err, rec):
        self.res.append((rec, -1, err.value))
        self.checkedOne()

    def checkedOne(self):
        self.rest -= 1
        if self.rest == 0:
            self.all_deferred.callback(None)
            self.all_deferred = None

    def onCheckAll(self, useless):
        logging.debug('check all')


