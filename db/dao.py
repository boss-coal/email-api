#!/usr/bin/python

import sqlite3
import config
import logging

class MailDao:
    def __init__(self):
        try:
            self.conn = sqlite3.connect(config.db_name)
        except Exception, ex
            logging.info("create db error %s", ex)
    
    def close(self):
        if self.conn:
            self.conn.close()

    def create_database(self):
        c = self.conn.cursor()
        c.execute('''CREATE TABLE Setting 
            (ID INT PRIMARY KEY     NOT NULL,
            SALARY         REAL);''')
        self.conn.commit()

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

    def add_mail_content(self, mid, content)
        c = self.conn.cursor()
        self.conn.commit()

    def update_mail_content(self, mid, content):
        c = self.conn.cursor()
        self.conn.commit()

    def query_mail_content(self, uid, filter_data)
        c = self.conn.cursor()
        return c.execute("")
