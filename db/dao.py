#!/usr/bin/python

from db import DB

class MailDao:
    def __init__(self):
        self.db = DB()
        self.db.conn()

    # setting struct
    '''
    {
        "id" : 0,
        "host" : "",
        "type" : "",
        "send_server_host" : "",
        "send_server_port" : "",
        "enable_send_server_ssl" : "",
        "smtp_server_host" : "",
        "smtp_server_port" : "",
        "enable_smtp_server_ssl" : "",
        "enable_starttls" : "",
        "exchange_server" : ""
    }
    '''
    def get_server_setting(self):
        return self.db.query_setting({})

    def add_server_setting(self, json_data):
        return self.db.add_setting(json_data)

    def update_server_setting(self, setting):
        return self.db.update_setting(setting["id"], setting)

    def get_mail_account(self):
        return self.db.query_account({})

    # mail struct
    '''
     {"mail_setting_id":0, "mail_account_name":name, "mail_account_psd":psd, "status":0}
    '''
    def add_mail_account(self, name, psd):
        data = {"mail_setting_id":0, "mail_account_name":name, "mail_account_psd":psd, "status":0}
        return self.db.add_mail_account(data)

    def update_mail_account(self, account_json):
        return self.db.update_account(account_json["id"], account_json)

    def del_mail_account(self, account_json):
        return self.del_mail_account(account_json["id"])

    #Mail Title json struct
    '''{ 
        "mail_uid": 0, #fk of mail account 
        "msg_id" : "",
        "uuid" : "",
        "mail_box" : "",
        "subject" : "",
        "to" : "",
        "cc" : "",
        "From" : "",
        "date" : "",
        "tag" : "", 
        }
        '''
    def add_mail_title(self, title_json):
        return self.db.add_mail_title(title_json)

    def update_mail_title(self, title_json):
        return self.update_mail_title(title_json["id"], title_json)

    def del_mail_title(self, title_json):
        return self.del_mail_title(title_json["id"])

    def add_mail_content(self, title_id, uuid, content):
        data = {"mail_id":title_id, "uuid":uuid , "content":content}
        return self.db.add_mail_account(data)

    #content struct
    '''
    {
        "id":0
        "mail_id" : 0,  #fk of mail title
        "uuid" : "",
        "content" : ""}
        
    '''
    def get_mail_content_by_uuid(self, uuid):
        return self.db.query_mail_content({"uuid":uuid})

    def update_mail_content(self, mid, content):
        return self.db.update_mail_content(mid, {"content":content})

    def del_mail_content(self, cid):
        return self.db.del_mail_content(cid)