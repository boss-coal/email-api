# -*- coding: utf-8 -*-
from base_handler import BaseHandler
from base import inlineCallbacks, returnValue
import json
from db.dao import MailDao
from util import getLocalFilePath

@inlineCallbacks
def initProviders():
    mail_dao = MailDao()
    settings = yield mail_dao.query_server_setting()
    if not settings:
        fid = open(getLocalFilePath('conf/provider.json'), 'r')
        data = fid.read()
        fid.close()
        settings = json.loads(data)
        for setting in settings:
            yield mail_dao.add_server_setting(setting)


class GetMailSettingHandler(BaseHandler):

    @inlineCallbacks
    def post(self):
        settings = yield self.mail_dao.query_server_setting()
        returnValue({'data': settings, 'count': len(settings)})


class OpMailSettingHandler(BaseHandler):

    @inlineCallbacks
    def post(self):
        setting = self.getArg('setting')
        setting = json.loads(setting)
        if 'id' in setting:
            op = 'update'
            yield self.mail_dao.update_server_setting(setting)
        else:
            if 'host' not in setting or 'imap_server_host' not in setting or 'smtp_server_host' not in setting:
                self.finishWithError(errmsg='setting should contain "host", "imap_server_host" and "smtp_server_host"')
            op = 'add'
            exist = yield self.mail_dao.query_server_setting(host=setting['host'])
            if exist:
                self.finishWithError(errmsg='host{%s} is existed' % setting['host'])
            setting['id'] = yield self.mail_dao.add_server_setting(setting)
        returnValue({'msg': '%s success' % op, 'id': setting['id']})


class DelMailSettingHandler(BaseHandler):

    @inlineCallbacks
    def post(self):
        setting_id = self.getArg('id')
        yield self.mail_dao.del_server_setting(setting_id)
        returnValue({'msg': 'delete success'})
