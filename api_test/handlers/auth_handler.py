# -*- coding: utf-8 -*-
import tornado.web
import json
import random
import time
import logging
import traceback
from tornado.web import asynchronous
import pdb


class AuthLoginedHandler(tornado.web.RequestHandler):
    @asynchronous
    def _deal_request(self):
        logging.debug("auth logined request")
        logined_account = {"uid":1, "mail_account_name":"sss@ss.com"}
        res = {"status": 0, "account_info":[logined_account], "errmsg":""}
        self.set_header("Content-Type", "application/json; charset=utf-8")
        self.write(json.dumps(res, encoding='utf8'))
        return self.finish()

    def get(self):
        return self._deal_request()



class AuthLoginHandler(tornado.web.RequestHandler):
    @asynchronous
    def _deal_request(self):
        logging.debug("auth login request")
        res = {"status": 0, "id":1, "mail_account_name":"", "errmsg":""}
        self.set_header("Content-Type", "application/json; charset=utf-8")
        try:
            data = json.loads(self.request.body)
            res["mail_account_name"] = data.get("mail_account_name")
            account_psd = data.get("mail_account_psd")
        except Exception,e:
            res["status"] = 1
            res["errmsg"] = "param error"
            self.write(json.dumps(res, encoding='utf8'))
            self.finish()
            return

        self.write(json.dumps(res, encoding='utf8'))
        self.finish()

    def post(self):
        return self._deal_request()

class AuthLogoutHandler(tornado.web.RequestHandler):
    @asynchronous
    def _deal_request(self):
        logging.debug("auth login request")
        res = {"status": 0, "uid":1, "errmsg":""}
        self.set_header("Content-Type", "application/json; charset=utf-8")
        try:
            data = json.loads(self.request.body)
            res["mail_account_name"] = data.get("mail_account_name")
        except Exception,e:
            res["status"] = 1
            res["errmsg"] = "param error"
            self.write(json.dumps(res, encoding='utf8'))
            self.finish()
            return

        self.write(json.dumps(res, encoding='utf8'))
        self.finish()

    def post(self):
        return self._deal_request()
