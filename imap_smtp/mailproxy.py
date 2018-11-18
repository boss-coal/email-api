from imap import IMAP4Client
from base import returnValue, inlineCallbacks, defer
from twisted.mail.imap4 import MessageSet
import logging
from flanker import mime

basic_mailbox_map = {
    "INBOX": "INBOX",
    "&g0l6P3ux-": "Drafts",
    "&XfJT0ZAB-": "Sent Messages",
    "&XfJSIJZk-": "Deleted Messages",
    "&V4NXPpCuTvY-": "Junk",
    "Deleted Messages": "Deleted Messages",
    "Archive": "Archive",
    "Junk": "Junk",
    "Sent Messages": "Sent Messages"
}

class MailProxy:

    def __init__(self, client):
        assert isinstance(client, IMAP4Client)
        self.client = client
        self.boxes = None

    @inlineCallbacks
    def queryBoxList(self):
        self.boxes = {}
        box_list = yield self.client.list('', '*')
        logging.debug(box_list)
        for box in box_list:
            if box[2] not in basic_mailbox_map:
                continue
            mailbox = basic_mailbox_map[box[2]]
            logging.debug('examine box: "%s"' % mailbox)
            try:
                box_info = yield self.client.examine(mailbox)
                self.boxes[mailbox] = box_info
            except Exception, e:
                logging.warn('examine mailbox "%s" exception: %s' % (mailbox, e))
        returnValue(self.boxes)


    @inlineCallbacks
    def queryMailList(self, mailbox, start, end=None, use_uid=True):
        if not self.boxes:
            yield self.queryBoxList()
        if mailbox not in self.boxes:
            ret = yield defer.succeed({'errmsg': 'mailbox not exist', 'status': -1})
            returnValue(ret)
        yield self.client.select(mailbox)

        if start is None:
            if end is None:
                msg_set = MessageSet(None)
            else:
                msg_set = MessageSet(1, int(end))
        else:
            msg_set = MessageSet(int(start), int(end) if end else None)

        header_args = ['Message-Id', 'From', 'To', 'Subject', 'Date', 'Cc', 'Bcc']
        mail_list = yield self.client.fetchSpecific(msg_set, headerType='HEADER.FIELDS',
                                                    headerArgs=header_args,
                                                    uid=use_uid
                                                    )
        if mail_list:
            mail_flags_list = yield self.client.fetchFlags(msg_set, uid=use_uid)
            args = {}
            for k, v in mail_flags_list.items():
                args[k] = [v]
            if not use_uid:
                mail_uid_list = yield self.client.fetchUID(msg_set)
                for k, v in mail_uid_list.items():
                    args[k].append(v)
            keys = sorted(mail_list, reverse=True)
            mail_list = [self.parseHeader(k, mail_list[k][0],  *args[k]) for k in keys]
        else:
            mail_list = []
        returnValue(mail_list)

    def parseHeader(self, index, header, *args):
        result = {'index': index}
        for arg in args:
            for k, v in arg.items():
                result[k.lower()] = v
        header = mime.from_string(header[-1])
        for h in header.headers.items():
            result[h[0].lower()] = h[1]
        return result


    @inlineCallbacks
    def queryMailDetail(self, mailbox, message_uid):
        self.client.select(mailbox)
        msg = yield self.client.fetchMessage(message_uid, True)
        returnValue(msg)


    # if read = False, unread the mail
    @inlineCallbacks
    def readMail(self, mailbox, message_uid, read=True):
        yield self.client.select(mailbox)
        yield self.editFlag(message_uid, ['\\Seen'], read)
        returnValue(['\\Seen'])

    @inlineCallbacks
    def moveToTrash(self, mailbox, message_uid):
        yield self.client.select(mailbox)
        yield self.client.copy(message_uid, 'Deleted Messages', True)
        yield self.deleteMessage(mailbox, message_uid)

    @inlineCallbacks
    def deleteMessage(self, mailbox, message_uid):
        yield self.client.select(mailbox)
        yield self.editFlag(message_uid, ['\\Deleted'])
        yield self.client.expunge()


    def editFlag(self, message_uid, flag, add=True):
        op = self.client.addFlags if add else self.client.removeFlags
        return op(message_uid, flag, silent=1, uid=True)









