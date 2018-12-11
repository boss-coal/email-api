# -*- coding: utf-8 -*-
from base import inlineCallbacks, returnValue, defer, reactor
from mail_base_handler import MailBaseHandler
from twisted.mail.smtp import sendmail
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
import json
import logging
from db.dao import MailDao
from util import toRemoteOrDbFormat, gmTimestampFromAscTime, gmTimestapFromIsoDate
from flanker import mime

mail_header_map = (
    # (db_name, remote_name, default_value)
    ('msg_id', 'message-id', ''),
    ('uuid', 'uid', ''),
    ('subject', 'subject', ''),
    ('to', 'to', ''),
    ('cc', 'cc', ''),
    ('bcc', 'bcc', ''),
    ('from', 'from', ''),
    ('date', 'date', ''),
)

def mailHeader2DbFormat(mail, mailbox="", account_id=-1):
    result = toRemoteOrDbFormat(mail, mail_header_map, (1, 0))
    result['mail_box'] = mailbox
    result['tag'] = json.dumps(mail.get('flags', ''))
    result['mail_uid_id'] = account_id
    result['gm_time'] = gmTimestampFromAscTime(result['date'])
    return result

def mailHeader2RemoteFormat(mail):
    result = toRemoteOrDbFormat(mail, mail_header_map, (0, 1))
    result['flags'] = json.loads(mail['tag'])
    return result

mail_content_map = (
    ('uuid', 'UID', ''),
    ('content', 'RFC822', ''),
)

def mailContent2DbFormat(mail, mailbox="", account_id=-1):
    result = toRemoteOrDbFormat(mail, mail_content_map, (1, 0))
    result['mail_box'] = mailbox
    result['mail_uid_id'] = account_id
    return result

def mailContent2RemoteFormat(mail):
    result = toRemoteOrDbFormat(mail, mail_content_map, (0, 1))
    return result


@inlineCallbacks
def syncMailListToDb(mail_list, mailbox, account, sync_content=True):
    logging.debug('syncDb %s' % mail_list)
    if mail_list:
        mail_dao = MailDao()
        for mail in mail_list:
            exist = yield mail_dao.query_mail_title(uuid=mail['uid'], mail_box=mailbox, mail_uid_id=account.id)
            if not exist:
                new_mail = mailHeader2DbFormat(mail, mailbox, account.id)
                new_mail['_without_id_'] = True  # after insert to db, would not query the newest id
                yield mail_dao.add_mail_title(new_mail)
            if sync_content:
                content_exist = yield mail_dao.query_mail_content(uuid=mail['uid'], mail_box=mailbox, mail_uid_id=account.id)
                if not content_exist:
                    content = yield account.mail_proxy.queryMailDetail(mailbox, mail['uid'])
                    content = content.values()
                    reactor.callLater(0, syncMailDetailToDb, content, mailbox, account)



@inlineCallbacks
def syncMailDetailToDb(mail_content_list, mailbox, account):
    mail_dao = MailDao()
    for mail_content in mail_content_list:
        exist = yield mail_dao.query_mail_content(uuid=mail_content['UID'], mail_box=mailbox, mail_uid_id=account.id)
        if not exist:
            new_mail = mailContent2DbFormat(mail_content, mailbox, account.id)
            new_mail['_without_id_'] = True
            new_mail['content'] = new_mail['content'].decode('utf-8')
            msg = mime.from_string(new_mail['content'])
            if msg.content_type.is_multipart():
                for part in msg.parts:
                    if part.content_type[0] == 'text/plain':
                        new_mail['plain'] = part.body
            else:
                if msg.content_type[0] == 'text/plain':
                    new_mail['plain'] = msg.body
            try:
                yield mail_dao.add_mail_content(new_mail)
            except Exception, e:
                logging.error(e)



class GetMailBoxListHandler(MailBaseHandler):

    @inlineCallbacks
    def task(self):
        result = yield self.mail_proxy.queryBoxList()
        returnValue({'data': result})



class GetLocalMailListHandler(MailBaseHandler):

    @inlineCallbacks
    def task(self):
        mailbox = self.getArg('mailbox')
        count = int(self.getArg('count', necessary=False, default=0))
        if count:
            offset = int(self.getArg('offset', necessary=False, default=0))
            filter = 'order by uuid desc limit %s, %s' % (offset, count)
        else:
            filter = ''
            start = self.getArg('start', necessary=False)
            if start:
                filter += ' and uuid >= "%s"' % start
            end = self.getArg('end', necessary=False)
            if end:
                filter += ' and uuid <= "%s"' % end
            filter +=' order by uuid desc'
        result = yield self.mail_dao.query_mail_title(filter=filter, mail_box=mailbox, mail_uid_id=self.account.id)
        result = [mailHeader2RemoteFormat(item) for item in result]
        returnValue(result)



class FetchMailListHandler(MailBaseHandler):

    @inlineCallbacks
    def task(self):
        mailbox = self.getArg('mailbox')
        start = self.getArg('start', necessary=False)
        end = self.getArg('end', necessary=False)
        use_uid = int(self.getArg('use_uid', necessary=False, default=1))
        result = yield self.mail_proxy.queryMailList(mailbox, start, end, not not use_uid)
        reactor.callLater(0, syncMailListToDb, result, mailbox, self.account)
        returnValue({'data': result, 'count': len(result)})


class GetLocalContactMailListHandler(MailBaseHandler):

    @inlineCallbacks
    def task(self):
        contact = self.getArg('contact')
        mailbox = self.getArg('mailbox', necessary=False, default=('INBOX', 'Sent Messages'))
        order = ' order by gm_time desc'
        filter = ''
        query = {
            '_like_': {
                'from': contact,
                'to': contact,
                '_or_': True
            },
            'mail_uid_id': self.account.id
        }
        if mailbox == 'all':
            mailbox = None
        elif not isinstance(mailbox, tuple):
            try:
                box_list = json.loads(mailbox)
                mailbox = box_list
            except:
                pass
            finally:
                query['mail_box'] = mailbox
        else:
            query['mail_box'] = mailbox

        time_zone = int(self.getArg('zone', necessary=False, default=8))
        after = self.getArg('after', necessary=False)
        if after:
            after = gmTimestapFromIsoDate(after, time_zone)
            filter += ' and gm_time>=%s' % after
        before = self.getArg('before', necessary=False)
        if before:
            before = gmTimestapFromIsoDate(before, time_zone)
            filter += ' and gm_time<%s' % before

        filter += order
        mail_list = yield self.mail_dao.query_mail_title(filter=filter, **query)
        returnValue({'data': mail_list, 'count': len(mail_list)})


class FetchContactMailListHandler(MailBaseHandler):

    @inlineCallbacks
    def task(self):
        contact = self.getArg('contact')
        mailbox = self.getArg('mailbox', necessary=False, default=('INBOX', 'Sent Messages'))
        if not isinstance(mailbox, tuple):
            mailbox = tuple(mailbox)
        result = []
        for box in mailbox:
            mail_list = yield self.mail_proxy.searchContactMailList(box, contact)
            result.append({box: mail_list})
        returnValue({'data': result})


class GetMailContentHandler(MailBaseHandler):

    @inlineCallbacks
    def task(self):
        # todo: to be confirmed, result should be parsed by client or server
        message_uid = self.getArg('message_uid')
        mailbox = self.getArg('mailbox')
        # query from local database, if not exist, fetch it from remote server
        result = yield self.mail_dao.query_mail_content(uuid=message_uid, mail_box=mailbox, mail_uid_id=self.account.id)
        if result:
            logging.debug('fetch %s\' message "%s" from db success' % (self.account.username, message_uid))
            result = [mailContent2RemoteFormat(item) for item in result]
            returnValue(result)
        result = yield self.mail_proxy.queryMailDetail(mailbox, message_uid)
        result = result.values()
        reactor.callLater(0, syncMailDetailToDb, result, mailbox, self.account)
        returnValue({'data': result})


class TagMailListHandler(MailBaseHandler):

    @inlineCallbacks
    def task(self):
        message_uid = self.getArg('message_uid')
        mailbox = self.getArg('mailbox')
        op = self.getArg('op', arg_range=('read', 'unread', 'trash', 'del'))

        mail = yield self.mail_dao.query_mail_title(uuid=message_uid, mail_box=mailbox, mail_uid_id=self.account.id)
        if not mail:
            remote_mail = yield self.mail_proxy.queryMailList(mailbox,start=message_uid,end=message_uid)
            yield syncMailListToDb(remote_mail, mailbox, self.account)
            mail = yield self.mail_dao.query_mail_title(uuid=message_uid, mail_box=mailbox, mail_uid_id=self.account.id)
        mail = mail[0]
        flags = json.loads(mail['tag'])
        mail = {
            'id': mail['id'],
        }
        if not flags:
            flags = []
        if op == 'read':
            ret = yield self.mail_proxy.readMail(mailbox, message_uid)
            flags.extend(ret)
            mail['tag'] = json.dumps(flags)
            yield self.mail_dao.update_mail_title(mail)
        elif op == 'unread':
            ret = yield self.mail_proxy.readMail(mailbox, message_uid, False)
            [flags.remove(tag) for tag in ret]
            mail['tag'] = json.dumps(flags)
            yield self.mail_dao.update_mail_title(mail)
        elif op == 'trash':
            trash_box = 'Deleted Messages'
            if mailbox == trash_box:
                self.finishWithError(errmsg='the message has been in trash box')
            yield self.mail_proxy.moveToTrash(mailbox, message_uid)
            last_trash_mail = yield self.mail_dao.query_mail_title(mail_box=trash_box, mail_uid_id=self.account.id,
                                                                   filter='order by uuid desc limit 1')
            start = int(last_trash_mail[0]['uuid']) + 1 if last_trash_mail else 1
            trash_mail = yield self.mail_proxy.queryMailList(trash_box, start)
            if trash_mail:
                reactor.callLater(0, syncMailListToDb, trash_mail, trash_box, self.account)
                returnValue({'data': trash_mail, 'msg': 'new messages in trash'})
        elif op == 'del':
            yield self.mail_proxy.deleteMessage(mailbox, message_uid)
            yield self.mail_dao.del_mail_title(mail)

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
        sent_box = 'Sent Messages'
        last_sent_mail = yield self.mail_dao.query_mail_title(mail_box=sent_box,
                                                              mail_uid_id=self.account.id,
                                                              filter='order by uuid desc limit 1')
        start = int(last_sent_mail[0]['uuid']) + 1 if last_sent_mail else 1
        sent_mail = yield self.mail_proxy.queryMailList(sent_box, start)
        if sent_mail:
                reactor.callLater(0, syncMailListToDb, sent_mail, sent_box, self.account)
                returnValue({'data': sent_mail, 'msg': 'new messages in sent box'})
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


