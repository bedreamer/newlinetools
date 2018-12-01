# -*- coding: UTF-8 -*-
from __future__ import print_function
import sys
import os
sys.path.append(os.path.dirname(__file__))
import datetime
import channel
__author__ = 'lijie'


DATETIME_STR_FMT = "%Y-%m-%d %H:%M:%S"
DATE_STR_FMT = "%Y-%m-%d"
TIME_STR_FMT = "%H:%M:%S"


class Field(object):
    """字段对象基类"""
    def __init__(self, **kwargs):
        self.value = None
        self.primary = False
        self.uniq = False
        self.not_null = False
        self.blank = True

        # 助记符
        try:
            if isinstance(kwargs['help_text'], str) is True:
                self.help_text = kwargs['help_text']
            else:
                self.help_text = ''
        except KeyError:
            self.help_text = ''

    def set(self, value):
        """设置当前值"""
        if self.primary is True and self.value is not None:
            raise ValueError("primary value could set once only.")
        self.value = value


class PrimaryField(Field):
    """主键字段"""
    def __init__(self, **kwargs):
        super(self.__class__, self).__init__(**kwargs)

        # 主键只能是整形
        self.primary = True

    def compile_define_sql_string(self):
        """返回字段定义字符串"""
        define_str_list = list()
        define_str_list.append('INT')
        define_str_list.append('AUTO_INCREMENT')
        define_str_list.append('PRIMARY KEY')

        return " ".join(define_str_list)

    def compile_insert_sql_string(self):
        """返回插入值的字符串形式"""
        if isinstance(self.value, int) is True or isinstance(self.value, long):
            return str(self.value)

        if self.primary is True:
            raise ValueError("primary not assigned.")

        raise ValueError("value not set yet.")

    def __str__(self):
        """返回当前值的字符串形式"""
        return self.compile_insert_sql_string()


class IntegerField(Field):
    """整形字段"""
    def __init__(self, **kwargs):
        super(self.__class__, self).__init__(**kwargs)

        # 处理默认值
        try:
            if isinstance(kwargs['default'], int) is True:
                self.default = kwargs['default']
            else:
                raise TypeError("default must be integer type.")
        except KeyError:
            self.default = None

    def compile_define_sql_string(self):
        """返回字段定义字符串"""
        define_str_list = list()

        define_str_list.append('INT')

        if isinstance(self.default, int) is True:
            default = "".join(["DEFAULT ", str(self.default)])
            define_str_list.append(default)

        return " ".join(define_str_list)

    def compile_insert_sql_string(self):
        """返回插入值的字符串形式"""
        if isinstance(self.value, int) is True or isinstance(self.value, long):
            return str(self.value)

        if isinstance(self.default, int) is True or isinstance(self.value, long):
            return str(self.default)

        raise ValueError("value not set yet.")

    def __str__(self):
        """返回当前值的字符串形式"""
        return self.compile_insert_sql_string()


class VarCharField(Field):
    """变长字符串字段"""
    def __init__(self, **kwargs):
        super(self.__class__, self).__init__(**kwargs)

        # 必须指定最大长度
        try:
            if isinstance(kwargs['max_length'], int) is True:
                self.max_length = kwargs['max_length']
            else:
                raise ValueError("max_length param must be a integer number.")
        except KeyError:
            raise ValueError("need give a max_length param.")

        # 处理默认值
        try:
            if isinstance(kwargs['default'], str) is True:
                length = len(kwargs['default'])
                if length > self.max_length:
                    print("** warning: default will be cut into %d bytes du to max_length limited." % self.max_length)
                    self.default = kwargs['default'][:self.max_length]
                elif length == 0:
                    self.default = None
                else:
                    self.default = kwargs['default']
            else:
                raise TypeError("default must be str type.")
        except KeyError:
            self.default = None

    def compile_define_sql_string(self):
        """返回字段定义字符串"""
        define_str_list = list()

        define_str_list.append('VARCHAR(%d)' % self.max_length)

        if isinstance(self.default, str) is True:
            default = "".join(["DEFAULT '", self.default, "'"])
            define_str_list.append(default)

        return " ".join(define_str_list)

    def compile_insert_sql_string(self):
        """返回插入值的字符串形式"""
        if isinstance(self.value, str) is True:
            return "".join(["'", self.value, "'"])

        if isinstance(self.default, str) is True:
            return "".join(["'", self.default, "'"])

        if self.blank is True:
            return "''"

        raise ValueError("value not set yet.")

    def __str__(self):
        """返回当前值的字符串形式"""
        return self.compile_insert_sql_string()

    def set(self, value):
        """设置值"""
        if isinstance(value, str):
            self.value = value
        elif isinstance(value, unicode):
            self.value = value.encode('utf8')
        else:
            self.value = str(value)

        if len(self.value) > self.max_length:
            self.value = self.max_length[: self.max_length]


class CharField(Field):
    """固定长度字符串字段"""
    def __init__(self, **kwargs):
        super(self.__class__, self).__init__(**kwargs)

        # 必须指定最大长度
        try:
            if isinstance(kwargs['max_length'], int) is True:
                self.max_length = kwargs['max_length']
            else:
                raise ValueError("max_length param must be a integer number.")
        except KeyError:
            raise ValueError("need give a max_length param.")

        # 处理默认值
        try:
            if isinstance(kwargs['default'], str) is True:
                length = len(kwargs['default'])
                if length > self.max_length:
                    print("** warning: default will be cut into %d bytes du to max_length limited." % self.max_length)
                    self.default = kwargs['default'][:self.max_length]
                elif length == 0:
                    self.default = None
                else:
                    self.default = kwargs['default']
            else:
                raise TypeError("default must be str type.")
        except KeyError:
            self.default = None

    def compile_define_sql_string(self):
        """返回字段定义字符串"""
        define_str_list = list()

        define_str_list.append('CHAR(%d)' % self.max_length)

        if isinstance(self.default, str) is True:
            default = "".join(["DEFAULT '", self.default, "'"])
            define_str_list.append(default)

        return " ".join(define_str_list)

    def compile_insert_sql_string(self):
        """返回插入值的字符串形式"""
        if isinstance(self.value, str) is True:
            return "".join(["'", self.value, "'"])

        if isinstance(self.default, str) is True:
            return "".join(["'", self.default, "'"])

        if self.blank is True:
            return "''"

        raise ValueError("value not set yet.")

    def set(self, value):
        """设置值"""
        if isinstance(value, str):
            self.value = value
        elif isinstance(value, unicode):
            self.value = value.encode('utf8')
        else:
            self.value = str(value)

        if len(self.value) > self.max_length:
            self.value = self.max_length[: self.max_length]

    def __str__(self):
        """返回当前值的字符串形式"""
        return self.compile_insert_sql_string()


class TextField(Field):
    """文本字段"""
    def __init__(self, **kwargs):
        super(self.__class__, self).__init__(**kwargs)

        # 处理默认值
        if 'default' in kwargs:
            print("** warning: TextField does not supported default value.")

    @staticmethod
    def compile_define_sql_string():
        """返回字段定义字符串"""
        return "TEXT"

    def compile_insert_sql_string(self):
        """返回插入值的字符串形式"""
        if isinstance(self.value, str) is True:
            return "".join(["'", self.value, "'"])

        if self.blank is True:
            return "''"

        raise ValueError("value not set yet.")

    def set(self, value):
        """设置值"""
        if isinstance(value, str):
            self.value = value
        elif isinstance(value, unicode):
            self.value = value.encode('utf8')
        else:
            self.value = str(value)

    def __str__(self):
        """返回当前值的字符串形式"""
        return self.compile_insert_sql_string()


class DateTimeField(Field):
    """日期时间字段"""
    def __init__(self, **kwargs):
        super(self.__class__, self).__init__(**kwargs)

        # 处理默认值
        try:
            if isinstance(kwargs['default'], datetime.datetime) is True:
                self.default = kwargs['default']
            elif isinstance(kwargs['default'], str) is True:
                self.default = datetime.datetime.strptime(kwargs['default'], DATETIME_STR_FMT)
            else:
                raise TypeError("default must be integer type.")
        except KeyError:
            self.default = None

    def compile_define_sql_string(self):
        """返回字段定义字符串"""
        define_str_list = list()

        define_str_list.append('DATETIME')

        if isinstance(self.default, datetime.datetime) is True:
            default = self.default.strftime(DATETIME_STR_FMT)
            define_str_list.append("DEFAULT '%s'" % default)

        return " ".join(define_str_list)

    def compile_insert_sql_string(self):
        """返回插入值的字符串形式"""
        if isinstance(self.value, datetime.datetime) is True:
            return "".join(["'", self.value.strftime(DATETIME_STR_FMT), "'"])

        if isinstance(self.default, datetime.datetime) is True:
            return "".join(["'", self.default.strftime(DATETIME_STR_FMT), "'"])

        raise ValueError("value not set yet.")

    def __str__(self):
        """返回当前值的字符串形式"""
        return self.compile_insert_sql_string()

    def set(self, value):
        """设置当前值"""
        if isinstance(value, datetime.datetime) is False:
            value = datetime.datetime.strptime(value, DATETIME_STR_FMT)
        super(self.__class__, self).set(value)


class DateField(Field):
    """日期字段"""
    def __init__(self, **kwargs):
        super(self.__class__, self).__init__(**kwargs)

        # 处理默认值
        try:
            if isinstance(kwargs['default'], datetime.datetime) is True:
                self.default = kwargs['default']
            elif isinstance(kwargs['default'], str) is True:
                self.default = datetime.datetime.strptime(kwargs['default'], DATE_STR_FMT)
            else:
                raise TypeError("default must be integer type.")
        except KeyError:
            self.default = None

    def compile_define_sql_string(self):
        """返回字段定义字符串"""
        define_str_list = list()

        define_str_list.append('DATE')

        if isinstance(self.default, datetime.datetime) is True:
            default = self.default.strftime(DATE_STR_FMT)
            define_str_list.append("DEFAULT '%s'" % default)

        return " ".join(define_str_list)

    def compile_insert_sql_string(self):
        """返回插入值的字符串形式"""
        if isinstance(self.value, datetime.datetime) is True:
            return "".join(["'", self.value.strftime(DATE_STR_FMT), "'"])

        if isinstance(self.default, datetime.datetime) is True:
            return "".join(["'", self.default.strftime(DATE_STR_FMT), "'"])

        raise ValueError("value not set yet.")

    def __str__(self):
        """返回当前值的字符串形式"""
        return self.compile_insert_sql_string()

    def set(self, value):
        """设置当前值"""
        if isinstance(value, datetime.datetime) is False:
            value = datetime.datetime.strptime(value, DATE_STR_FMT)
        super(self.__class__, self).set(value)


class TimeField(Field):
    """时间字段"""
    def __init__(self, **kwargs):
        super(self.__class__, self).__init__(**kwargs)

        # 处理默认值
        try:
            if isinstance(kwargs['default'], datetime.datetime) is True:
                self.default = kwargs['default']
            elif isinstance(kwargs['default'], str) is True:
                self.default = datetime.datetime.strptime(kwargs['default'], TIME_STR_FMT)
            else:
                raise TypeError("default must be integer type.")
        except KeyError:
            self.default = None

    def compile_define_sql_string(self):
        """返回字段定义字符串"""
        define_str_list = list()

        define_str_list.append('TIME')

        if isinstance(self.default, datetime.datetime) is True:
            default = self.default.strftime(TIME_STR_FMT)
            define_str_list.append("DEFAULT '%s'" % default)

        return " ".join(define_str_list)

    def compile_insert_sql_string(self):
        """返回插入值的字符串形式"""
        if isinstance(self.value, datetime.datetime) is True:
            return "".join(["'", self.value.strftime(TIME_STR_FMT), "'"])

        if isinstance(self.default, datetime.datetime) is True:
            return "".join(["'", self.default.strftime(TIME_STR_FMT), "'"])

        raise ValueError("value not set yet.")

    def __str__(self):
        """返回当前值的字符串形式"""
        return self.compile_insert_sql_string()

    def set(self, value):
        """设置当前值"""
        if isinstance(value, datetime.datetime) is False:
            value = datetime.datetime.strptime(value, TIME_STR_FMT)
        super(self.__class__, self).set(value)


class Model(object):
    """数据库表对象"""
    def __init__(self, **kwargs):
        self.id = None
        self.do_field_check()
        self.update_field_value(**kwargs)

    def __str__(self):
        """返回表名称"""
        return self.get_table_name()

    def do_field_check(self):
        """字段检查，不允许出现多个主键"""
        var_dict = self.get_field_dict()
        primary = list()

        for col, field in var_dict.items():
            if field is None:
                continue

            if field.primary is False:
                continue

            if isinstance(field.primary, bool) is False:
                raise TypeError("primary must be True or False.")

            primary.append({'name': col, 'field': field})

        if len(primary) > 1:
            raise ValueError("too many primary key.")

        if primary == 1:
            return True

        if 'id' in var_dict and var_dict['id'] is not None:
            raise TypeError("the `id` field must be used as primary key.")

        self.id = PrimaryField(help_text="自动添加的主键")

    def update_field_value(self, **kwargs):
        """通过参数更改字段的值"""
        var_dict = self.get_field_dict()

        for col, value in kwargs.items():
            if col not in var_dict:
                raise ValueError("there is no field named", col)
            field = var_dict[col]
            field.set(value)

    def get_sub_class(self):
        """返回子类型"""
        sub_class_list = Model.__subclasses__()
        for SubClass in sub_class_list:
            if isinstance(self, SubClass):
                return SubClass
        return None

    def get_table_name(self):
        """返回当前对象对应的表名称"""
        subclass = self.get_sub_class()
        if subclass is None:
            raise TypeError("could not match a table name.")
        else:
            return subclass.__name__

    def get_primary(self):
        """返回主键名及字段"""
        field_map = self.get_field_dict()
        for col, field in field_map.items():
            if field.primary is False:
                continue
            return col, field

        raise ValueError("not set a primary key.")

    def get_primary_key_value(self):
        """返回一个新主键的值"""
        return channel.fetch_auto_increment_id(self.get_table_name())

    def get_field_dict(self):
        """返回字段映射字典"""
        return vars(self)

    def compile_field_define_sql(self):
        """返回字段定义SQL字符串"""
        field_map = self.get_field_dict()
        field_define_list = list()

        for col, define in field_map.items():
            field_define = " ".join([col, define.compile_define_sql_string()])
            field_define_list.append(field_define)

        return ",".join(field_define_list)

    def compile_record_insert_sql(self):
        """返回插入记录SQL字符串"""
        table_name = str(self)
        field_map = self.get_field_dict()
        _, primary = self.get_primary()

        # 首先处理主键，否则在进行数据处理时会抛出主键未设置异常
        if primary.value is None:
            primary.value = self.get_primary_key_value()

        field_name_string = ",".join(field_map.keys())
        field_value_string = ",".join([str(x) for x in field_map.values()])

        sql_sub_list = ["INSERT INTO ", table_name, ' (', field_name_string, ') VALUES(', field_value_string, ')']
        sql = "".join(sql_sub_list)
        # print(sql)
        return sql

    def compile_table_create_sql(self):
        """返回创建表SQL字符串"""
        table_name = str(self)
        field_define_string = self.compile_field_define_sql()
        sql_sub_list = ["CREATE TABLE IF NOT EXISTS ", table_name, '(', field_define_string, ')']
        sql = "".join(sql_sub_list)
        # print(sql)
        return sql

    def compile_table_drop_sql(self):
        """返回删除表SQL字符串"""
        table_name = str(self)
        sql_sub_list = ["DROP TABLE IF EXISTS ", table_name]
        sql = "".join(sql_sub_list)
        # print(sql)
        return sql

    def insert(self, **kwargs):
        """向表中插入新的值"""
        self.update_field_value(**kwargs)
        sql = self.compile_record_insert_sql()
        # print(sql)
        channel.excute(sql, None)

    def count(self):
        """返回表中记录的条数"""
        table_name = str(self)
        return channel.count(table_name=table_name)

    def purge(self):
        """清空表格中的全部数据"""
        table_name = str(self)
        sql_sub_list = ["DELETE FROM ", table_name]
        sql = "".join(sql_sub_list)
        # print(sql)
        channel.excute(sql, None)

    def delete(self):
        """删除当前保持的对象"""
        table_name = str(self)
        col, primary = self.get_primary()

        sql_sub_list = ["DELETE FROM ", table_name, " WHERE %s=%d" % (col, primary.value)]
        sql = "".join(sql_sub_list)
        # print(sql)
        channel.excute(sql, None)


if __name__ == '__main__':
    class People(Model):
        def __init__(self, **kwargs):
            self.name = VarCharField(max_length=20, default="<填写名称>", help_text="人物名称")
            self.sex = CharField(max_length=16, default="M", help_text="性别")
            self.abstract = TextField(help_text="人物简介")
            self.birth = DateField(help_text="出生日期")
            self.mail = TimeField(default="12:00:00", help_text="发邮件时间")
            super(self.__class__, self).__init__(**kwargs)

    ch = channel.connect('127.0.0.1', db='mg', user='root', password='8989889')

    somebody = People()
    print(somebody.compile_table_create_sql())
    somebody.insert(name="李斯", abstract="丞相", birth="1921-12-23")
