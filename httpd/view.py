# -*- coding: UTF-8 -*-
__author__ = 'lijie'
import path
from response import *
from template import render
import wsapi
import auth
import service
import codecs
import json


@path.route(path='/', method=['GET'])
def index(request):
    return render(request, "启动页/main.html", {})


@path.route(path='/steps/editor/', method=['GET'])
def index(request):
    return render(request, "工步/main.html", {})


class WebSocketEcho(HttpResponseWebSocket):
    def __init__(self, request):
        super().__init__(request)

    def on_text_frame(self, data):
        """
            called while receive a text frame
            return None
        """
        self.send_text(data)

    def on_bin_frame(self, data):
        """
            called while receive a binary frame
            return None
        """
        self.send_bin(data)

    def on_close_frame(self, data):
        """
            called while receive a close frame
            return None
        """
        self.close()

    def on_connection_down(self, request):
        """
            called while the connection is lost
            return None
        """
        print(request.path, "websocket is down.")


class WebSocketNewLine(wsapi.WsApiGateWay):
    def __init__(self, request):
        self.wsapi_path = '/newline/'
        super().__init__(request)
        self.bms, self.newline, self.solution = self.request.kwargs['request_ext_param']
        self.solution.register_ui(self.wsapi_path, self)

    def on_connection_down(self, request):
        self.solution.unregister_ui(self.wsapi_path, self)
        super().on_connection_down(request)

    def on_query_request(self, remote_request):
        if remote_request.data['path'] == '/steps/all/':
            return self.on_query_all_steps(remote_request)
        elif remote_request.data['path'] == '/steps/single/':
            return self.on_query_single_step(remote_request, remote_request.data['name'])
        elif remote_request.data['path'] == '/conditions/all/':
            return self.on_query_all_conditions_list(remote_request)
        else:
            default_response = self.make_response_without_error(remote_request, None)
            self.do_response(remote_request, default_response)
            return default_response

    def on_push_request(self, remote_request):
        if remote_request.data['path'] == '/step/save/':
            return self.on_save_step(remote_request, remote_request.data['name'], remote_request.data['data'])
        else:
            default_response = self.make_response_without_error(remote_request, None)
            self.do_response(remote_request, default_response)
            return default_response

    def push_step_changed(self, old, new):
        data = {
            'path': '/newline/step/changed/',
            'old': old,
            'new': new
        }
        self.do_push_request(data)

    def on_query_all_steps(self, request):
        """
        查询全部工步 /steps/all/
        :param request: wsapi request对象
        :return: 全部工步对象
        """
        solution_step = self.solution.get_solution_steps_as_json(name=None)
        default_response = self.make_response_without_error(request, solution_step)
        self.do_response(request, default_response)
        return default_response

    def on_query_single_step(self, request, name):
        """
        查询单步工步 /steps/single/
        :param request: wsapi request对象
        :return: 单步工步对象
        """
        solution_step = self.solution.get_solution_steps_as_json(name=name)
        default_response = self.make_response_without_error(request, solution_step)
        self.do_response(request, default_response)
        return default_response

    def on_query_all_conditions_list(self, request):
        """
        查询全部可用的判断条件 /conditions/all/
        :param request: wsapi request对象
        :return: 全部可用判断条件
        """
        bms_conditions_map = self.bms.get_conditions_map()
        newline_conditions_map = self.newline.get_conditions_map()
        step_conditions_map = {'self.loop': 'self.loop'}

        conditions_map = dict(bms_conditions_map, **newline_conditions_map, **step_conditions_map)
        default_response = self.make_response_without_error(request, conditions_map)
        self.do_response(request, default_response)
        return default_response

    def on_save_step(self, request, name, step):
        """
        保存单步工步 /step/save/
        :param request: wsapi request对象
        :param name: 工步名称, eg. step1, step2, ..., stepn
        :param step: 工步对象
        :return: 全部工步对象
        """
        self.solution.save_solution_single_step(name, step)
        solution_step = self.solution.get_solution_steps_as_json()
        default_response = self.make_response_without_error(request, solution_step)
        self.do_response(request, default_response)
        return default_response


@path.route(path='/conditions/all/', method=['GET'])
def all_conditions_json(request):
    bms, newline, solution = request.kwargs['request_ext_param']
    bms_conditions_map = bms.get_conditions_map()
    newline_conditions_map = newline.get_conditions_map()
    step_condistions_map = {'self.loop': 'self.loop'}
    conditions_map = dict(bms_conditions_map, **newline_conditions_map, **step_condistions_map)
    return HttpResponseJson(conditions_map)


@path.route(path='/live/', method=['GET'])
def live(request):
    try:
        if request.headers['Upgrade'] != 'websocket':
            raise TypeError
        if request.headers['Connection'] != 'Upgrade':
            raise TypeError
    except:
        return HttpResponseBadRequest()

    return WebSocketEcho(request)


@path.route(path='/newline/', method=['GET'])
def live(request):
    try:
        if request.headers['Upgrade'] != 'websocket':
            raise TypeError
        if request.headers['Connection'] != 'Upgrade':
            raise TypeError
    except:
        return HttpResponseBadRequest()

    return WebSocketNewLine(request)

