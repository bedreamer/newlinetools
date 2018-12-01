# -*- coding: UTF-8 -*-
__author__ = 'lijie'
import sys
import os
sys.path.append(os.path.dirname(os.getcwd()))
import settings
import codecs
import json
import hashlib
import http.cookies as cookies
import path
import auth.user as user
import auth.session as session
from response import *
from template import render


@path.route(path='/login/', method=['GET'])
def login_get(request):
    try:
        sid = request.cookie['sid'].value
    except KeyError:
        return render(request, "auth/login.html")

    try:
        username = session.query(sid)
    except:
        # 登录失效

        cookie = cookies.SimpleCookie()
        cookie['sid'] = sid
        cookie['sid']['max-age'] = 0
        cookie['sid']['path'] = '/'

        return render(request, "auth/login.html", cookie=cookie)

    return HttpResponseRedirect('/')


@path.route(path='/login/', method=['POST'])
def login_post(request):
    try:
        name = request.POST['username']
        passwd = request.POST['password']
        login_user = user.get_user_by_name(name)

        accept = login_user.check_password(passwd)
        if accept is False:
            raise ValueError
    except:
        return HttpResponseRedirect(request.path)

    sid = session.create_login_token(login_user)

    cookie = cookies.SimpleCookie()
    cookie['sid'] = sid
    cookie['sid']['path'] = '/'

    try:
        next_path = request.GET['next']
    except:
        next_path = '/'

    return HttpResponseRedirect(next_path, cookie=cookie, headers=[('Cache-Control', 'max-age=0')])


@path.route(path='/logout/')
def login_post(request):
    try:
        sid = request.cookie['sid'].value
    except KeyError:
        return HttpResponseRedirect('/')

    try:
        session.destroy(sid)
    except:
        pass

    cookie = cookies.SimpleCookie()
    cookie['sid'] = sid
    cookie['sid']['max-age'] = 0
    cookie['sid']['path'] = '/'

    return HttpResponseRedirect('/login/', cookie=cookie, headers=[('Cache-Control', 'max-age=0')])

