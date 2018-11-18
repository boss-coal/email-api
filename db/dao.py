# -*- coding: utf-8 -*-

from singleton import singleton
from db import DB

@singleton
class MailDao:
    def __init__(self):
        self.db = DB()

    # setting struct
    '''
    {
        "id" : 0,
        "host" : "",
        "type" : "", #default 'imap4'
        "imap_server_host" : "",
        "imap_server_port" : 0, #default 143
        "smtp_server_host" : "",
        "smtp_server_port" : 0, #default 25
        "enable_smtp_server_ssl" : 0,
        "enable_starttls" : 0,
        "exchange_server" : '' #default None
    }
    '''

    def query_server_setting(self, **kwargs):
        return self.db.query_setting(kwargs)

    def add_server_setting(self, json_data):
        return self.db.add_setting(json_data)

    def update_server_setting(self, setting):
        return self.db.update_setting(setting["id"], setting)

    def del_server_setting(self, setting_id):
        return self.db.del_setting(setting_id)

    # mail account struct
    '''
     {"mail_setting_id":0, "mail_account_name":name, "mail_account_psd":psd, "status":0}
    '''
    def query_mail_account(self, **kwargs):
        return self.db.query_account(kwargs)

    def add_mail_account(self, name, psd, setting_id):
        data = {"mail_setting_id": setting_id, "mail_account_name":name, "mail_account_psd":psd, "status":0}
        return self.db.add_mail_account(data)

    def update_mail_account(self, account_json):
        return self.db.update_account(account_json["id"], account_json)

    def del_mail_account(self, account_json):
        return self.del_mail_account(account_json["id"])

    # Mail Title json struct
    '''{ 
        "mail_uid": 0, #fk of mail account 
        "msg_id" : "",
        "uuid" : 0,
        "mail_box" : "",
        "subject" : "",
        "to" : "",
        "cc" : "",
        "From" : "",
        "date" : "",
        "tag" : "", 
        }
        '''

    def query_mail_title(self, **kwargs):
        return self.db.query_mail_title(kwargs)

    def add_mail_title(self, title_json):
        return self.db.add_mail_title(title_json)

    def update_mail_title(self, title_json):
        return self.db.update_mail_title(title_json["id"], title_json)

    def del_mail_title(self, title_json):
        return self.db.del_mail_title(title_json["id"])

    #content struct
    '''
    {
        "id":0,
        "mailbox": "",
        "uuid" : "",
        "content" : "",
        "mail_uid_id": 0, # fk mail_account(id)
        }
        
    '''
    def add_mail_content(self, data):
        return self.db.add_mail_content(data)

    def query_mail_content(self, **kwargs):
        return self.db.query_mail_content(kwargs)

    def update_mail_content(self, mid, content):
        return self.db.update_mail_content(mid, {"content":content})

    def del_mail_content(self, cid):
        return self.db.del_mail_content(cid)