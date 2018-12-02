from twisted.web.resource import Resource
from base_handler import BaseHandler
from auth_handler import AuthLoginHandler, AuthLoginedHandler
import mail_handler
import setting_handler

class Branch(BaseHandler):
    isLeaf = False

def generate_tree():
    root = Branch()
    # add children

    setting = Branch()
    root.putChild('setting', setting)
    setting.putChild('get_setting_list', setting_handler.GetMailSettingHandler())
    setting.putChild('add_setting', setting_handler.OpMailSettingHandler())
    setting.putChild('edit_setting', setting_handler.OpMailSettingHandler())
    setting.putChild('del_setting', setting_handler.DelMailSettingHandler())

    auth = Branch()
    root.putChild('auth', auth)
    auth.putChild('login', AuthLoginHandler())
    auth.putChild('logined_account', AuthLoginedHandler())

    mail = Branch()
    root.putChild('mail', mail)
    mail.putChild('get_mail_box_list', mail_handler.GetMailBoxListHandler())
    mail.putChild('get_local_mail_list', mail_handler.GetLocalMailListHandler())
    mail.putChild('get_remote_mail_list', mail_handler.FetchMailListHandler())
    mail.putChild('get_mail_content', mail_handler.GetMailContentHandler())
    mail.putChild('tag', mail_handler.TagMailListHandler())
    mail.putChild('send_mail', mail_handler.SendMailHandler())
    mail.putChild('search_local_contact_mail_list', mail_handler.GetLocalContactMailListHandler())
    mail.putChild('search_remote_contact_mail_list', mail_handler.FetchContactMailListHandler())

    return root

