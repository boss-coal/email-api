#!/usr/bin/python

import sqlite3
import config
import logging

class MailDao:
    def __init__(self):
        try:
            self.conn = sqlite3.connect(config.db_name)
        except Exception, ex:
            logging.info("create db error %s", ex)
    
    def close(self):
        if self.conn:
            self.conn.close()

    def insert_into_table_return_id(self, table_name, **kwargs):
        sql = "insert into %s (" % table_name
        values = " values( "
        i = 0
        length = len(kwargs)
        for (k, v) in kwargs.items():
            sql += "`%s`" % k
            values += "%s"
            if i != length - 1:
                sql += ","
                values += ","
            i += 1

        sql += ")"
        values += ")"

        sql += values

        with self.con as cur:
            cur.execute(sql, kwargs.values())
            return self.con.insert_id()

        return 0

    def update_table_values(self, union_id, table_name, **kwargs):
        sql = "update %s set " % table_name
        i = 0
        for (k, v) in kwargs.items():
            sql += "`%s`=%%s" % (k,)
            if i != len(kwargs) - 1:
                sql += ","
            i += 1
        # kwargs[k] = self._convert_str(v)
        if union_id is not None:
            sql += " where id=%s" % union_id

        with self.con as cur:
            cur.execute(sql, kwargs.values())
            return self.con.affected_rows()

        return 0

    def delete_from_table(self, table_name, **kwargs):
        sql = "delete from %s " % table_name
        if kwargs and len(kwargs) > 0:
            sql += "where "
        i = 0
        for (k, v) in kwargs.items():
            sql += " `%s`=%%s " % (k,)
            if i != len(kwargs) - 1:
                sql += " and "
            i += 1

        with self.con as cur:
            cur.execute(sql, kwargs.values())
            return self.con.affected_rows()

        return 0

    def select_from_table(self, table_name, filter=None, **kwargs):
        sql = "select * from %s " % table_name
        if kwargs and len(kwargs) > 0:
            sql += "where "
        values = []
        i = 0
        for (k, v) in kwargs.items():
            if isinstance(v, list) or isinstance(v, tuple):
                if not v:
                    return []
                seq = ','.join(['%s'] * len(v))
                sql += " `%s` in (%s) " % (k, seq)
                values += v
            else:
                sql += " `%s`=%%s " % (k,)
                values.append(v)
            if i != len(kwargs) - 1:
                sql += " and "
            i += 1

        if filter:
            sql += " " + filter

        with self.con as cur:
            cur.execute(sql, values)
            return cur.fetchall()

        return []

    def add_setting(self, data_json):
        c = self.conn.cursor()
        self.conn.commit()


    def query_setting(self, filter=None):
        c = self.conn.cursor()
        return c.execute("")

    def update_setting(self, setting_id, data_json):
        c = self.conn.cursor()
        self.conn.commit()

    def add_mail_account(self, account_json):
        c = self.conn.cursor()
        self.conn.commit()

    def del_mail_account(self, uid):
        c = self.conn.cursor()
        self.conn.commit()

    def update_account(self, uid, update_data_json):
        c = self.conn.cursor()
        self.conn.commit()

    def query_account(self, filter_data):
        c = self.conn.cursor()
        return c.execute("")

    def add_mail_title(self, mail_title):
        c = self.conn.cursor()
        self.conn.commit()

    def update_mail_title(self, mid, mail_title):
        c = self.conn.cursor()
        self.conn.commit()

    def del_mail_title(self, mid):
        c = self.conn.cursor()
        self.conn.commit()

    def query_mail_title(self, filter_data):
        c = self.conn.cursor()
        return c.execute("")

    def add_mail_content(self, mid, content):
        c = self.conn.cursor()
        self.conn.commit()

    def update_mail_content(self, mid, content):
        c = self.conn.cursor()
        self.conn.commit()

    def query_mail_content(self, uid, filter_data):
        c = self.conn.cursor()
        return c.execute("")
