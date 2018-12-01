# -*- coding: UTF-8 -*-
__author__ = 'lijie'


class UserProfileNotFound(Exception):
    """用户参数文件未找到"""
    pass


class SessionExpired(Exception):
    """会话过期"""
    pass


class UserNotFound(Exception):
    """用户未找到"""
    pass


class UserNameOrPasswordIncorrect(Exception):
    """用户名或密码错误"""
    pass

