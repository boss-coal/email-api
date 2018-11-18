# -*- coding: utf-8 -*-
from base_handler import BaseHandler
from base import inlineCallbacks, returnValue
import json

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
            setting['id'] = yield self.mail_dao.add_server_setting(setting)
        returnValue({'msg': '%s success' % op, 'id': setting['id']})


class DelMailSettingHandler(BaseHandler):

    @inlineCallbacks
    def post(self):
        setting_id = self.getArg('id')
        yield self.mail_dao.del_server_setting(setting_id)
        returnValue({'msg': 'delete success'})
