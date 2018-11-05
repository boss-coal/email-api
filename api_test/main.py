# -*- coding: utf-8 -*-
import setproctitle
import logging
import time
import os
import json
from tornado.web import Application

import tornado.options
from tornado.options import define, options
from tornado.web import asynchronous
from tornado import gen
import handlers

define("port", 35000, int, "Listen port")
define("address", "0.0.0.0", str, "Bind address")
define("psname", "mail_local_srv_d", str, "Back run process name")
define("localversion", 0, int, "local version")
define("autoreload", 0, int, "Enable autoreload, 0 is disable")

# Parse commandline
tornado.options.parse_command_line()
# Set process title
setproctitle.setproctitle(options.psname)

webapp = Application(
    [
        (r"/setting/get_setting_list", handlers.GetMailSettingHandler),
        (r"/setting/add_setting", handlers.OpMailSettingHandler),
        (r"/setting/edit_setting", handlers.OpMailSettingHandler),
        (r"/setting/del_setting", handlers.DelMailSettingHandler),
        (r"/auth/logined_account", handlers.AuthLoginedHandler),
        (r"/auth/login", handlers.AuthLoginHandler),
        (r"/auth/logout", handlers.AuthLogoutHandler),
        (r"/mail/get_mail_list", handlers.GetMailListHandler),
        (r"/mail/get_send_mail_list", handlers.GetMailListHandler),
        (r"/mail/get_mail_content", handlers.GetMailContentHandler),
        (r"/mail/tag", handlers.TagMailListHandler),
        (r"/mail/save_mail", handlers.EditMailContentHandler),
        (r"/mail/edit_mail", handlers.EditMailContentHandler),
        (r"/mail/send_mail", handlers.SendMailHandler),
    ],
    autoreload=bool(options.autoreload),
)

# Run web app webapp.listen(options.port, options.address, xheaders=True)
tornado.ioloop.IOLoop.current().start()
