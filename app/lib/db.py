#!/usr/bin/env python3

"""Database connector and methods for interaction with db."""

__version__ = '0.0.1'
__author__ = 'hharutyunyan'
__copyright__ = 'Copyright 2018, hharutyunyan'
__license__ = 'All Rights Reserved'
__maintainer__ = 'hharutyunyan'
__status__ = "Production"

import pymysql.cursors


class DB(object):

    insert = "INSERT INTO %s(%s) VALUES (%s) %s"
    update = "UPDATE %s SET %s WHERE %s %s"
    select = "SELECT %s FROM %s %s WHERE %s %s"
    select_count = "SELECT SUM(src.count) AS count FROM (%s) AS src"
    delete = "DELETE FROM %s WHERE %s"

    def __init__(self, host: str, user: str, pwd: str, dbname: str):
        self.host = host
        self.user = user
        self.pwd = pwd
        self.dbname = dbname
        self.transaction = False
        self.conn = pymysql.connect(
            host=self.host,
            user=self.user,
            password=self.pwd,
            db=self.dbname,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )

        super().__init__()

    def reconnect(self):
        """ Close the current connection and reconnect to the DB

        """
        self.conn.close()
        self.conn = pymysql.connect(
            host=self.host,
            user=self.user,
            password=self.pwd,
            db=self.dbname,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )

    def execute(self, query: str, args: dict = {}) -> pymysql.cursors.DictCursor:
        """ Execute the query

        """

        if self.conn.open:
            self.reconnect()

        cur = self.conn.cursor()

        try:
            cur.execute(query, args)
            if not self.transaction:
                self.conn.commit()
        except Exception as ex:
            self.conn.rollback()
            raise Exception(ex)
        return cur

    def commit(self):
        """ Commits the open transaction if any found """
        if self.transaction:
            self.conn.commit()
            self.transaction = False

    def rollback(self):
        """ Rallbacks current transaction """
        self.conn.rollback()
        self.transaction = False
