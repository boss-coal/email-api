# -*- coding: utf-8 -*-
import tornado.web
import json
import random
import time
import logging
import traceback
from tornado.web import asynchronous
from tornado import gen
import pdb


class GetMailListHandler(tornado.web.RequestHandler):
    @asynchronous
    @gen.coroutine 
    def _deal_request(self):
        logging.debug("get mail list request")
        self.set_header("Content-Type", "application/json; charset=utf-8")
        mail_list = []

        res = {"result":0, "errmsg":""}
        try:
            uid = int(self.get_argument("uid"))
            if "index" in self.request.arguments:
                index = int(self.get_argument("index"))
                count = int(self.get_argument("count"))
        except Exception, ex:
            res["result"] = 1
            res["errmsg"] = "param error"
            self.write(json.dumps(res, encoding='utf8'))
            return self.finish()

        mail_list.append({"id":1,"title":"hello", "sender":"xxx@mail.com", "time":"2018-11-04 12:22:22", "readed":"true","sended":"false"})
        mail_list.append({"id":2,"title":"hello1", "sender":"xxx@mail.com", "time":"2018-11-04 12:22:22", "readed":"true","sended":"false"})
        mail_list.append({"id":3,"title":"hello2", "sender":"xxx@mail.com", "time":"2018-11-04 12:22:22", "readed":"true","sended":"false"})
        mail_list.append({"id":4,"title":"hello3", "sender":"xxx@mail.com", "time":"2018-11-04 12:22:22", "readed":"true","sended":"false"})
        res = {"result":0, "count":len(mail_list), "mail_list":mail_list, "total_count":300}
        self.write(json.dumps(res, encoding='utf8'))
        return self.finish()

    def get(self):
        return self._deal_request()

class GetMailContentHandler(tornado.web.RequestHandler):
    @asynchronous
    @gen.coroutine 
    def _deal_request(self):
        logging.debug("get mail content request")
        res = {"result":0, "errmsg":""}
        self.set_header("Content-Type", "application/json; charset=utf-8")

        try:
            mail_id = int(self.get_argument("id"))
        except Exception,e:
            res["result"] = 1
            res["errmsg"] = "param error"
            self.write(json.dumps(res, encoding='utf8'))
            self.finish()
            return

        res = {"result": 0, "id":1, "title":"hello", "sender":"xxxx@ss.com", "cc":"", "to":"ssss@ss.com", "content":"<xml>ssssssssssss</xml>", "attach_list":[], "errmsg":""}
        self.write(json.dumps(res, encoding='utf8'))
        self.finish()

    def get(self):
        return self._deal_request()

class TagMailListHandler(tornado.web.RequestHandler):
    @asynchronous
    @gen.coroutine 
    def _deal_request(self):
        logging.debug("tag operator mail request")
        res = {"result": 0, "uid":1, "errmsg":""}
        self.set_header("Content-Type", "application/json; charset=utf-8")
        try:
            data = json.loads(self.request.body)
            op_list = data.get("op_list")
        except Exception,e:
            res["result"] = 1
            res["errmsg"] = "param error"
            self.write(json.dumps(res, encoding='utf8'))
            self.finish()
            return

        self.write(json.dumps(res, encoding='utf8'))
        self.finish()

    def post(self):
        return self._deal_request()

class EditMailContentHandler(tornado.web.RequestHandler):
    @asynchronous
    @gen.coroutine 
    def _deal_request(self):
        logging.debug("edit operator mail request")
        res = {"result": 0, "id":1, "errmsg":""}
        self.set_header("Content-Type", "application/json; charset=utf-8")
        try:
            data = json.loads(self.request.body)
            mail_id = data.get("id")
            mail_info = data.get("mail_info")
        except Exception,e:
            res["result"] = 1
            res["errmsg"] = "param error"
            self.write(json.dumps(res, encoding='utf8'))
            self.finish()
            return

        self.write(json.dumps(res, encoding='utf8'))
        self.finish()

    def post(self):
        return self._deal_request()

class SendMailHandler(tornado.web.RequestHandler):
    @asynchronous
    @gen.coroutine
    def _deal_request(self):
        logging.debug("send mail request")
        res = {"result": 0, "id":0, "errmsg":""}
        try:
            mail_id = self.get_argument("id")
            res["id"] = int(mail_id)
        except Exception,e:
            res["result"] = 1
            res["errmsg"] = "param error"
            self.write(json.dumps(res, encoding='utf8'))
            return self.finish()

        self.write(json.dumps(res, encoding='utf8'))
        return self.finish()

    def get(self):
        self._deal_request()
