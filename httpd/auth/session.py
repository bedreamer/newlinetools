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
import view
import time
import auth.user


session_database_file = settings.data_root_directory + 'session.json'


def reset():
    try:
        with codecs.open(session_database_file) as file:
            pass
    except:
        with codecs.open(session_database_file, 'w', encoding='utf8') as file:
            json.dump({}, file, ensure_ascii=False, indent=2)
reset()


def query(sid):
    """
        根据sid查询用户，返回username或None
    """
    with codecs.open(session_database_file) as file:
        sessions = json.load(file)
        if sid not in sessions:
            raise ValueError

        now = time.time()
        user_session = sessions[sid]
        if now - user_session['tsp'] > settings.max_seconds_hold_by_session:
            destroy(sid)
            raise settings.SessionExpired
        else:
            return user_session['name']


def create_login_token(user):
    """
        根据user创建会话
        返回sid
    """
    try:
        with codecs.open(session_database_file) as file:
            sessions = json.load(file)
    except:
        sessions = dict()

    with codecs.open(session_database_file, 'w') as file:
        md5 = hashlib.md5()
        now = int(time.time())
        seed = ''.join([user.name, str(now)])
        md5.update(seed.encode())
        sid = md5.hexdigest()
        sessions[sid] = {'name': user.name, 'tsp': now}
        json.dump(sessions, file, ensure_ascii=False, indent=2)

    return sid


def destroy(sid):
    """
        关闭会话
    """
    with codecs.open(session_database_file) as file:
        sessions = json.load(file)

    if sid not in sessions:
        return

    del sessions[sid]

    with codecs.open(session_database_file, 'w') as file:
        json.dump(sessions, file, ensure_ascii=False, indent=2)


def load_from_session(sid):
    try:
        username = query(sid)
    except:
        return auth.user.UserUnkown()

    try:
        return auth.user.get_user_by_name(username)
    except:
        return auth.user.UserUnkown()

