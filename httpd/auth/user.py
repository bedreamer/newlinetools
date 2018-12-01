# -*- coding: UTF-8 -*-
__author__ = 'lijie'
import sys
import os
sys.path.append(os.path.dirname(os.getcwd()))
import settings
import codecs
import json
import hashlib
import path
from template import render


class UserBasic(object):
    def __init__(self, id, name, alias):
        # id=-1 未知
        # id=0 root
        # id=1 default admin
        # id > 1 admin or staff
        self.id = id
        self.name = name
        self.alias = alias

        # 根用户
        self.is_root = False
        # 管理员
        self.is_admin = False
        # 职员
        self.is_staff = False

        # 拒绝登录
        self.login_refuse = False

        #
        #md5 = hashlib.md5()
        # 默认密码
        #md5.update('123456'.encode())
        #self.passwd = md5.hexdigest()
        self.passwd = '123456'

    def disable_login(self):
        self.login_refuse = True if self.id not in {0, 1} else False

    def enable_login(self):
        self.login_refuse = False if self.id >= 0 else True

    def load(self):
        pass

    def check_password(self, passwd):
        if self.passwd != passwd:
            return False
        else:
            return True

    def save(self):
        if self.id < 0:
            return

        user_json = "".join([settings.data_root_directory, 'user/', self.name, '.txt'])
        with codecs.open(user_json, mode='w', encoding='utf8') as file:
            json.dump(vars(self), file, ensure_ascii=False, indent=2)

    def __str__(self):
        return self.name


class UserRoot(UserBasic):
    def __init__(self):
        super().__init__(0, 'root', '超级管理员')
        # 根用户
        self.is_root = True
        # 管理员
        self.is_admin = True
        # 职员
        self.is_staff = True


class UserAdmin(UserBasic):
    def __init__(self, id):
        super().__init__(id, 'admin', '系统管理员')
        # 管理员
        self.is_admin = True
        # 职员
        self.is_staff = True


class UserUnkown(UserBasic):
    def __init__(self):
        super().__init__(-1, '未登录', '未登录')


def get_user_by_name(name):
    user_json = "".join([settings.data_root_directory, 'user/', name, '.txt'])
    with codecs.open(user_json, mode='r', encoding='utf8') as file:
        user_cfg = json.load(file)

    user = UserBasic(-1, '未登录', '未登录')
    for key, value in user_cfg.items():
        setattr(user, key, value)

    return user
