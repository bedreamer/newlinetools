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


service_config_json = 'serivices.json'


class Obj(object):
    pass


def list_all_services_use_json_format():
    """列出全部的服务"""
    try:
        with codecs.open(service_config_json) as file:
            services = json.load(file)
    except:
        services = list()

    services_list = list()
    for key, service in services.items():
        obj = Obj()
        for key, value in service.items():
            setattr(obj, key, value)
        services_list.append(obj)

    return services_list


def insert_service(name, short_name, executable, params_string, description, enable):
    """新增服务"""
    try:
        with codecs.open(service_config_json) as file:
            services = json.load(file)
    except:
        services = dict()

    if name in services:
        return services[name]

    serivce = {
        'name': name,
        'short_name': short_name,
        'executable': executable,
        'params_string': params_string,
        'description': description,
        'enable': enable
    }

    try:
        services[name] = serivce
        with codecs.open(service_config_json, 'w') as file:
            json.dump(services, file, ensure_ascii=False)

        return serivce
    except:
        return None


def query_service_by_name(name):
    """查询服务"""
    with codecs.open(service_config_json) as file:
        services = json.load(file)

    service = Obj()
    for key, value in services[name].items():
        setattr(service, key, value)

    return service


def update_service_by_name(name, **kwargs):
    """更新服务"""
    try:
        with codecs.open(service_config_json) as file:
            services = json.load(file)
    except:
        return None

    if name not in services:
        return None

    try:
        for key, value in kwargs.items():
            services[name][key] = value

        with codecs.open(service_config_json, 'w') as file:
            json.dump(services, file, ensure_ascii=False)

        return services[name]
    except:
        return None


def delete_service(name):
    """删除服务"""
    try:
        with codecs.open(service_config_json) as file:
            services = json.load(file)
    except:
        return None

    if name not in services:
        return None

    try:
        del services[name]

        with codecs.open(service_config_json, 'w') as file:
            json.dump(services, file, ensure_ascii=False, indent=2)

        return name
    except:
        return None


@path.route(path='/service/', method=['GET'])
def list_all_services(request):
    try:
        if request.user.is_staff is False:
            raise ValueError
    except:
        print("登录失效....")
        return HttpResponseRedirect('/login/?next=' + request.path)

    context = dict()
    context['services_list'] = list_all_services_use_json_format()
    return render(request, "service/all-services.html", ctx=context)


@path.route(path='/service/new/', method=['GET'])
def login_post(request):
    try:
        if request.user.is_staff is False:
            raise ValueError
    except:
        print("还未登录....")
        return HttpResponseRedirect('/login/?next=' + request.path)

    return render(request, "service/new-service.html")


@path.route(path='/service/new/', method=['POST'])
def login_post(request):
    try:
        if request.user.is_staff is False:
            raise ValueError
    except:
        print("还未登录....")
        return HttpResponseRedirect('/login/?next=' + request.path)

    name = request.POST['name']
    short_name = request.POST['short_name']
    executable = request.POST['executable']
    params_string = request.POST['params_string']
    description = request.POST['description']
    enable = request.POST['enable']

    insert_service(name, short_name, executable, params_string, description, enable)

    return HttpResponseRedirect('/service/')


@path.route(path='/service/show/<str:name>/', method=['GET'])
def show_service_script(request, name):
    try:
        if request.user.is_staff is False:
            raise ValueError
    except:
        print("还未登录....")
        return HttpResponseRedirect('/login/?next=' + request.path)

    service = query_service_by_name(name)
    context = dict(service=service)

    return render(request, "service/show-services-script.html", ctx=context)
