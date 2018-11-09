from imap import IMAP4Client
from base import returnValue, inlineCallbacks, defer
from twisted.mail.imap4 import MessageSet
import logging

basic_mailbox_map = {
  "INBOX": "INBOX",
  "&g0l6P3ux-": "Drafts",
  "&XfJT0ZAB-": "Sent Messages",
  "&XfJSIJZk-": "Deleted Messages",
  "&V4NXPpCuTvY-": "Junk",
  "Deleted Messages": "Deleted Messages",
  "Archive": "Archive",
  "Junk": "Junk"
}

class MailProxy:

    def __init__(self, client):
        assert isinstance(client, IMAP4Client)
        self.client = client
        self.boxes = None

    @inlineCallbacks
    def queryBoxList(self):
        self.boxes = []
        box_list = yield self.client.list('', '*')
        for box in box_list:
            if box[2] not in basic_mailbox_map:
                continue
            self.boxes.append(basic_mailbox_map[box[2]])
        returnValue(self.boxes)


    @inlineCallbacks
    def queryMailList(self, mailbox, start_index=1):
        if not self.boxes:
            yield self.queryBoxList()
        if mailbox not in self.boxes:
            ret = yield defer.succeed({'errmsg': 'mailbox not exist', 'status': -1})
            returnValue(ret)
        yield self.client.select(mailbox)

        msg_set = '%s:*' % start_index
        # mail_list = yield self.client.fetchHeaders('1:*')
        # if mail_list:
        #     keys = sorted(mail_list)
        #     mail_list = [{'index': k, 'header': mail_list[k]} for k in keys]
        mail_list = yield self.client.fetchSpecific(msg_set, headerType='HEADER.FIELDS',
                                                    headerArgs=['Message-Id', 'From', 'SUBJECT', 'Date'],
        )
        mail_uid_list = yield self.client.fetchUID(msg_set)
        mail_flags_list = yield self.client.fetchFlags(msg_set)
        logging.debug(mail_flags_list)

        if mail_list:
            keys = sorted(mail_list)
            mail_list = [self.parseHeader(k, mail_list[k][0][2], mail_uid_list[k], mail_flags_list[k]) for k in keys]
        else:
            mail_list = []
        returnValue(mail_list)

    def parseHeader(self, index, header, *args):
        result = {'index': index}
        for arg in args:
            result.update(arg)
        for item in header.split('\r\n'):
            if item:
                i = item.index(':')
                result[item[:i]] = item[i+2:]
        return result


    @inlineCallbacks
    def queryMailDetail(self,  message_uid):
        msg = yield self.client.fetchMessage(message_uid, True)
        returnValue(msg)


    # if read = False, unread the mail
    @inlineCallbacks
    def readMail(self, mailbox, message_uid, read=True):
        yield self.client.select(mailbox)
        yield self.editFlag(message_uid, ['\\Seen'], read)

    @inlineCallbacks
    def deleteMessage(self, mailbox, message_uid):
        yield self.client.select(mailbox)
        yield self.editFlag(message_uid, ['\\Deleted'])
        yield self.client.expunge()


    def editFlag(self, message_uid, flag, add=True):
        op = self.client.addFlags if add else self.client.removeFlags
        return op(message_uid, flag, silent=1, uid=True)









