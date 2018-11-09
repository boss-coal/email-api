from twisted.web.resource import Resource
from base_handler import BaseHandler
from test_handler import TestHandler
from auth_handler import AuthLoginHandler, AuthoLoginedHandler
import mail_handler

class Root(BaseHandler):
    isLeaf = False

class Branch(BaseHandler):
    isLeaf = False

def generate_tree():
    root = Root()
    # add children
    root.putChild('test', TestHandler())

    setting = Branch()
    root.putChild('setting', setting)

    auth = Branch()
    root.putChild('auth', auth)
    auth.putChild('login', AuthLoginHandler())
    auth.putChild('logined_account', AuthoLoginedHandler())

    mail = Branch()
    root.putChild('mail', mail)
    mail.putChild('get_mail_box_list', mail_handler.GetMailBoxListHandler())
    mail.putChild('get_mail_list', mail_handler.GetMailListHandler())
    mail.putChild('get_mail_content', mail_handler.GetMailContentHandler())
    mail.putChild('tag', mail_handler.TagMailListHandler())
    mail.putChild('send_mail', mail_handler.SendMailHandler())

    return root

