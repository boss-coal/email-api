# -*- coding: utf-8 -*-
from base import inlineCallbacks, returnValue, defer
from mail_base_handler import MailBaseHandler
from twisted.mail.smtp import sendmail
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
import json
import logging
import base64

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
        mailbox = self.getArg('mailbox')
        result = yield self.mail_proxy.queryMailDetail(mailbox, message_uid)
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

    def getMimeArg(self, mime_arg, key, necessary=True, default=None):
        if necessary and key not in mime_arg:
            self.finishWithError(errmsg='mime must contain key \'%s\'' % key)
        return mime_arg.get(key, default)

    @inlineCallbacks
    def task(self):
        mime_arg = self.getArg('mime')
        mime_arg = json.loads(mime_arg)
        headers = self.getMimeArg(mime_arg, 'headers')
        parts = self.getMimeArg(mime_arg, 'parts')
        message_parts = []
        multi_type = 'mixed'
        for part in parts:
            if part['type'] in ('plain', 'html'):
                msg_part = MIMEText(part['content'].encode('utf-8'), part['type'], 'utf-8')
            elif part['type'] == 'attachment':
                msg_part = MIMEText(open(part['file_path'], 'rb').read(), 'base64', 'utf-8')
                msg_part['Content-Type'] = 'application/octet-stream'
                msg_part['Content-Disposition'] = 'attachment; filename="%s"' % part['filename'].encode('utf-8')
            elif part['type'] == 'html-img':
                multi_type = 'related'
                content_child = MIMEText(part['content'].encode('utf-8'), 'html', 'utf-8')
                msg_part = MIMEMultipart('alternative')
                msg_part.attach(content_child)
            elif part['type'] == 'img':
                msg_part = MIMEImage(open(part['img_path'], 'rb').read())
                msg_part.add_header('Content-ID', '<%s>' % part['img_cid'].encode('utf-8'))
                msg_part.add_header('Content-Disposition', 'inline', filename='music.png')
                msg_part.set_param('name', 'music.png')
            else:
                self.finishWithError()
            message_parts.append(msg_part)
        if len(message_parts) == 1:
            message = message_parts[0]
        else:
            message = MIMEMultipart(_subtype=multi_type)
            for part in message_parts:
                message.attach(part)
        for k, v in headers.iteritems():
            message[k] = v.encode('utf-8')

        logging.debug(message.as_string())
        receivers = self.getMimeArg(mime_arg, 'receivers')
        if len(receivers) > 1 and self.getMimeArg(mime_arg, 'mode',necessary=False) == 'single':
            self.rest = len(receivers)
            self.res = []
            self.all_deferred = defer.Deferred().addCallback(self.onCheckAll)
            to = headers['To'].split(', ')
            for i, rec in enumerate(receivers):
                message.replace_header('To', to[i])
                deferred = self.sendMail(message, [rec])
                deferred.addCallback(self.onSingleSendSuccess, rec)
                deferred.addErrback(self.onSingleSendFailed, rec)
            yield self.all_deferred
        else:
            yield self.sendMail(message, receivers)
            self.res = {'msg': 'sent successfully'}
        returnValue(self.res)

    def getMessageString(self, message):
        string = message.as_string()
        string = string.replace('\r\n boundary', ' boundary')
        return string

    def sendMail(self, message, receivers):
        return sendmail(self.account.smtp_host, self.account.username, receivers, self.getMessageString(message),
                 username=self.account.username, password=self.account.password)

    def onSingleSendSuccess(self, result, rec):
        self.res.append((rec, 0, result))
        self.checkedOne()

    def onSingleSendFailed(self, err, rec):
        self.res.append((rec, -1, '%s' % err.value))
        self.checkedOne()

    def checkedOne(self):
        self.rest -= 1
        if self.rest == 0:
            self.all_deferred.callback(None)
            self.all_deferred = None

    def onCheckAll(self, useless):
        logging.debug('check all')


