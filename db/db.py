# -*- coding: utf-8 -*-

import sqlite3
import conf.config as config
import logging
import os

from fields import parseQueryList
from base import defer, inlineCallbacks, returnValue
from twisted.enterprise import adbapi

class DB:
    def __init__(self):
        logging.debug('init db')
        try:
            dirname, filename = os.path.split(os.path.abspath(__file__))
            db_path = os.path.join(dirname, config.db_name)
            # self.conn = sqlite3.connect(db_path)
            self.conn = adbapi.ConnectionPool('sqlite3', db_path, check_same_thread=False, cp_openfun=self.set_text_factory)
        except Exception, ex:
            logging.info("create db error %s", ex)
            
    def set_text_factory(self, conn):
        conn.text_factory = str
        
    def close(self):
        if self.conn:
            self.conn.close()

    @inlineCallbacks
    def insert_into_table(self, table_name, **kwargs):
        return_id = True
        if '_without_id_' in kwargs:
            return_id = False
            kwargs.pop('_without_id_')
        sql = 'insert into %s (`%s`) values (%s)' % \
              (table_name, '`, `'.join(kwargs.keys()), ', '.join(('?',)*len(kwargs)))
        logging.debug(sql)
        ret = yield self.conn.runOperation(sql, kwargs.values())
        if return_id:
            ret = yield self.conn.runQuery('select id from %s order by id desc limit 1' % table_name)
            ret = ret[0][0]
        returnValue(ret)

    def update_table_values(self, union_id, table_name, **kwargs):
        if 'id' in kwargs:
            kwargs.pop('id')
        conditions = ['`%s`=?' % key for key in kwargs]
        sql = "update %s set %s" % (table_name, ', '.join(conditions))
        if union_id is not None:
            sql += " where id=%s" % union_id
        logging.debug(sql)
        return self.conn.runOperation(sql, kwargs.values())

    def delete_from_table(self, table_name, **kwargs):
        sql = "delete from %s " % table_name
        if kwargs and len(kwargs) > 0:
            conditions = ['`%s`=?' % key for key in kwargs]
            sql += " where %s" % ' and '.join(conditions)
        logging.debug(sql)
        return self.conn.runOperation(sql, kwargs.values())

    @inlineCallbacks
    def select_from_table(self, table_name, filter=None, **kwargs):
        sql = "select * from %s " % table_name
        values = []
        if kwargs and len(kwargs) > 0:
            conditions = []
            if '_like_' in kwargs:
                like = kwargs['_like_']
                kwargs.pop('_like_')
                if isinstance(like, dict):
                    _or_ = not not like.get('_or_')
                    if _or_:
                        like.pop('_or_')
                    _likes_ = ['`%s` like "%%%s%%"' % kv for kv in like.items()]
                    if _or_:
                        conditions.append('(%s)' % ' or '.join(_likes_))
                    else:
                        conditions.extend(_likes_)
            for (k, v) in kwargs.items():
                if isinstance(v, list) or isinstance(v, tuple):
                    conditions.append('`%s` in (%s)' % (k, ', '.join(('?',)*len(v))))
                    values.extend(v)
                else:
                    conditions.append('`%s`=?' % k)
                    values.append(v)
            sql += ' where %s' % ' and '.join(conditions)

        if filter:
            sql += " " + filter

        logging.debug(sql)
        data = yield self.conn.runQuery(sql, values)
        if data:
            data = parseQueryList(data, table_name)
        returnValue(data)

    def add_setting(self, data_json):
        return self.insert_into_table("mail_setting", **data_json)

    def query_setting(self, filter):
        return self.select_from_table("mail_setting", **filter)

    def update_setting(self, setting_id, data_json):
        return self.update_table_values(setting_id, "mail_setting", **data_json)

    def del_setting(self, setting_id):
        return self.delete_from_table('mail_setting', **{'id': setting_id})

    def add_mail_account(self, account_json):
        return self.insert_into_table("mail_account", **account_json)

    def update_account(self, uid, update_data_json):
        return self.update_table_values(uid, "mail_account", **update_data_json)

    def query_account(self, filter_data):
        return self.select_from_table("mail_account", **filter_data)

    def add_mail_title(self, mail_title):
        return self.insert_into_table("mail_title", **mail_title)

    def update_mail_title(self, mid, mail_title):
        return self.update_table_values(mid, "mail_title", **mail_title)

    def del_mail_title(self, mid):
        return self.delete_from_table("mail_title" , **{"id": mid})

    def query_mail_title(self, filter_data):
        return self.select_from_table("mail_title", **filter_data)

    def add_mail_content(self, content):
        return self.insert_into_table("mail_content", **content)

    def update_mail_content(self, mid, content):
        return self.update_table_values(mid, "mail_content", **content)

    def query_mail_content(self, filter_data):
        return self.select_from_table("mail_content", **filter_data)

    def del_mail_content(self, cid):
        return self.delete_from_table("mail_content", cid)
