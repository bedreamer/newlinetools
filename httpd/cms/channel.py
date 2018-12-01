# -*- coding: utf8 -*-
from __future__ import print_function
import MySQLdb as mysql
import time


class DBQuery(object):
    def __init__(self, sql, callback):
        self.sql = sql
        self.callback = callback
        self.born = time.time()

    def __str__(self):
        return '<' + self.sql + '>'


class DBChannel:
    def __init__(self, host, db, user, password):
        self.host, self.db, self.user, self.password = host, db, user, password
        self.query_sql_stack = list()
        self.conn = mysql.connect(host=self.host, user=self.user, passwd=self.password, db=self.db, charset="utf8")
        self.autoincreamt_id_table = dict()

    def run(self):
        if len(self.query_sql_stack) == 0:
            return

        need_commit = 0
        begin = time.time()
        now = begin
        # 最大执行500ms
        while now - begin < 0.5 and len(self.query_sql_stack):
            subbegin = time.time()
            query = self.query_sql_stack.pop(0)
            commit, cursor = self.execute(query)
            need_commit += commit
            now = time.time()
            delta_ms = (now - subbegin) * 1000
            print(query, delta_ms, "ms")

        if need_commit > 0:
            self.conn.commit()

    def close(self):
        global channle
        channle = None
        if self.conn:
            while len(self.query_sql_stack):
                query = self.query_sql_stack.pop(0)
                _, _ = self.execute(query)

            self.conn.commit()
            self.conn.close()
            print("*** data base connection closed!")

    def execute(self, query):
        """执行SQL，返回数据集光标"""
        commit = 0
        cursor = self.conn.cursor()
        try:
            nr = cursor.execute(query.sql)
        except Exception as e:
            print(e)
            return 0, None

        # 如果SQL是写入性质的，则执行完成后提交一次
        sql = query.sql.upper()
        if sql.find('SELECT') == 0:
            pass
        else:
            commit = 1

        return commit, cursor

    def last(self, table_name, nr=None):
        """
        返回末尾指定个数的记录
        返回字典
        """
        sql = 'SELECT * FROM %s LIMIT %d' % (table_name, nr)
        cursor = self.conn.cursor()
        try:
            count = cursor.execute(sql)
        except Exception as e:
            print(e)
            pass

    def first(self, table_name, nr=None):
        """
        返回头部指定个数的记录
        返回字典
        """
        pass

    def count(self, table_name):
        """
        统计记录总数
        返回整形
        """
        sql = 'SELECT COUNT(*) FROM %s' % table_name
        cursor = self.conn.cursor()
        nr = cursor.execute(sql)
        if nr == 1:
            all = cursor.fetchone()
        else:
            return 0
        return all[0]

    def fetch_auto_increment_id(self, table_name):
        """返回自增ID"""
        if table_name not in self.autoincreamt_id_table:
            sql = "SELECT auto_increment FROM information_schema.TABLES WHERE TABLE_SCHEMA='%s' AND TABLE_NAME='%s'" % \
                  (self.db, table_name)
            cursor = self.conn.cursor()
            nr = cursor.execute(sql)
            if nr > 0:
                results = cursor.fetchall()
                x = results[0][0]
            else:
                x = 0
                self.autoincreamt_id_table[ table_name ] = x
            return x
        else:
            self.autoincreamt_id_table[table_name] += 1
            return self.autoincreamt_id_table[ table_name ]

    def execute_now(self, sql):
        """立即执行，返回光标"""
        cursor = self.conn.cursor()
        nr = cursor.execute(sql)
        return cursor

    def load_user_table(self, table_name, fields_list, InitClass):
        """从数据表中加载对象"""
        fields_string = ",".join(fields_list)
        sql_sub_list = ['SELECT ', fields_string, " FROM ", table_name]
        sql = "".join(sql_sub_list)
        cursor = self.conn.cursor()
        nr = cursor.execute(sql)

        if nr <= 0:
            return list()

        obj_list = list()
        while nr > 0:
            nr -= 1
            r = cursor.fetchone()
            o = dict()
            for idx, key in enumerate(fields_list):
                o[key] = r[idx]

            obj = InitClass(**o)
            obj_list.append(obj)

        return obj_list


channle = None
def connect(host, db, user, password):
    global channle
    channle = DBChannel(host, db, user, password)
    return channle


def excute(sql, callback):
    """执行sql"""
    if channle is None:
        raise ValueError("database not connected yet!")

    query = DBQuery(sql, callback)
    channle.query_sql_stack.append(query)


def execute_now(sql):
    """立即执行SQL"""
    global channle
    if channle is None:
        raise ValueError("database not connected yet!")

    return channle.execute_now(sql)


def last(table_name, nr=None):
    """返回指定个数的末位记录"""
    global channle
    if channle is None:
        raise ValueError("database not connected yet!")

    nr = 1 if nr is None else nr

    return channle.last(table_name, nr)


def first(table_name, nr=None):
    """返回指定个数的头部记录"""
    global channle
    if channle is None:
        raise ValueError("database not connected yet!")

    nr = 1 if nr is None else nr

    return channle.last(table_name, nr)


def count(table_name):
    """
    统计记录总数
    返回整形
    """
    global channle
    if channle is None:
        raise ValueError("database not connected yet!")

    return channle.count(table_name)


def fetch_auto_increment_id(table_name):
    """返回自增ID"""
    global channle
    if channle is None:
        raise ValueError("database not connected yet!")

    return channle.fetch_auto_increment_id(table_name)
