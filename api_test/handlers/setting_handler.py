# -*- coding: utf-8 -*-
import tornado.web
import json
import random
import time
import logging
import traceback
from tornado.web import asynchronous
from tornado import gen

class GetMailSettingHandler(tornado.web.RequestHandler):
    @asynchronous
    @gen.coroutine
    def _deal_request(self):
        logging.debug("get mail setting request")
        mail_server_setting = {
            "id":1,
            "host":"163.com",
            "type":"POP3",
            "send_server_host":"pop3.163.com",
            "send_server_port":"433",
            "enable_send_server_ssl":"true",
            "smtp_server_host":"smtp.163.com",
            "smtp_server_port":"433",
            "enable_smtp_server_ssl":"",
            "enable_starttls":"true",
            "exchange_server":""
        }

        res = {"status": 0, "server_settings":[mail_server_setting], "errmsg":""}
        self.set_header("Content-Type", "application/json; charset=utf-8")
        self.write(json.dumps(res, encoding='utf8'))
        self.finish()

    def get(self):
        return self._deal_request()
    def post(self):
        self.send_error(400)

class OpMailSettingHandler(tornado.web.RequestHandler):
    @asynchronous
    @gen.coroutine 
    def _deal_request(self):
        logging.debug("add mail setting request")
        res = {"status": 0, "id":1, "errmsg":""}
        self.set_header("Content-Type", "application/json; charset=utf-8")
        try:
            data = json.loads(self.request.body)
            setting = data.get("setting")
        except Exception,e:
            res["status"] = 1
            res["errmsg"] = "param error"
            self.write(json.dumps(res, encoding='utf8'))
            self.finish()
            return

        self.write(json.dumps(res, encoding='utf8'))
        self.finish()

    def get(self):
        self.send_error(400)

    def post(self):
        return self._deal_request()

class DelMailSettingHandler(tornado.web.RequestHandler):
    @asynchronous
    @gen.coroutine 
    def _deal_request(self):
        logging.debug("del mail setting request")
        res = {"status": 0, "id":1, "errmsg":""}
        self.set_header("Content-Type", "application/json; charset=utf-8")
        try:
            data = json.loads(self.request.body)
            id_setting = data.get("id")
        except Exception,e:
            res["status"] = 1
            res["errmsg"] = "param error"
            self.write(json.dumps(res, encoding='utf8'))
            self.finish()
            return

        self.write(json.dumps(res, encoding='utf8'))
        self.finish()

    def get(self):
        self.send_error(400)

    def post(self):
        return self._deal_request()
