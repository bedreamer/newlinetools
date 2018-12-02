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
    return HttpResponseRedirect("/steps/editor/")


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
        self.wsapi_path = '/newline/step/'
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
            return self.on_step_save(remote_request, remote_request.data['name'], remote_request.data['data'])
        elif remote_request.data['path'] == '/step/delete/':
            return self.on_step_delete(remote_request, remote_request.data['name'])
        elif remote_request.data['path'] == '/step/check/':
            return self.on_step_check(remote_request)
        elif remote_request.data['path'] == '/step/status/':
            return self.on_step_status(remote_request)
        elif remote_request.data['path'] == '/step/start/':
            return self.on_step_start(remote_request, remote_request.data['entry'])
        elif remote_request.data['path'] == '/step/stop/':
            return self.on_step_stop(remote_request)
        elif remote_request.data['path'] == '/step/pause/':
            return self.on_step_pause(remote_request)
        elif remote_request.data['path'] == '/step/resume/':
            return self.on_step_resume(remote_request)
        elif remote_request.data['path'] == '/step/reboot/':
            return self.on_step_reboot(remote_request, remote_request.data['entry'])
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

    def on_step_save(self, request, name, step):
        """
        保存单步工步 /step/save/
        :param request: wsapi request对象
        :param name: 工步名称, eg. step1, step2, ..., stepn
        :param step: 工步对象
        :return: 全部工步对象
        """
        if self.solution.is_stopped() is False:
            default_response = self.make_response_with_error(request, code=1001, reason="工步未停止", data=None)
            self.do_response(request, default_response)
            return default_response

        self.solution.save_solution_single_step(name, step)

        solution_step = self.solution.get_solution_steps_as_json()
        default_response = self.make_response_without_error(request, solution_step)
        self.do_response(request, default_response)
        return default_response

    def on_step_delete(self, request, step_name):
        """
        删除指定的工步 /steps/delete/
        :param request: wsapi request对象
        :return: 全部工步对象
        """
        if self.solution.is_stopped() is False:
            default_response = self.make_response_with_error(request, code=1001, reason="工步未停止", data=None)
            self.do_response(request, default_response)
            return default_response

        self.solution.step_delete(step_name)

        solution_step = self.solution.get_solution_steps_as_json(name=None)
        default_response = self.make_response_without_error(request, solution_step)
        self.do_response(request, default_response)
        return default_response

    def on_step_check(self, request):
        """
        检查现有工步是否正确
        :param request: wsapi request对象
        :return: 返回全部工步列表
        """
        result_or_reason, step_name_if_error = self.solution.steps_check()
        if result_or_reason in {'', None, True}:
            solution_step = self.solution.get_solution_steps_as_json(name=None)
            default_response = self.make_response_without_error(request, solution_step)
        else:
            default_response = self.make_response_with_error(request, code=1001, reason=result_or_reason, data=step_name_if_error)

        self.do_response(request, default_response)
        return default_response

    def on_step_status(self, request):
        """
        获取工步状态数据
        :param request: wsapi request对象
        :return: 返回全部工步状态数据
        """
        steps_status = self.solution.steps_status()
        default_response = self.make_response_without_error(request, steps_status)
        self.do_response(request, default_response)
        return default_response

    def on_step_start(self, request, entry):
        """
        启动工步
        :param request: wsapi request对象
        :return: 返回全部工步状态数据
        """
        if self.solution.is_running():
            default_response = self.make_response_with_error(request, code=1002, reason="工步已经启动", data=None)
            self.do_response(request, default_response)
            return default_response

        steps_status = self.solution.steps_start(entry)
        default_response = self.make_response_without_error(request, steps_status)
        self.do_response(request, default_response)
        return default_response

    def on_step_stop(self, request):
        """
        停止工步
        :param request: wsapi request对象
        :return: 返回全部工步状态数据
        """
        steps_status = self.solution.steps_stop()
        default_response = self.make_response_without_error(request, steps_status)
        self.do_response(request, default_response)
        return default_response

    def on_step_pause(self, request):
        """
        暂停工步
        :param request: wsapi request对象
        :return: 返回全部工步状态数据
        """
        steps_status = self.solution.steps_pause()
        default_response = self.make_response_without_error(request, steps_status)
        self.do_response(request, default_response)
        return default_response

    def on_step_resume(self, request):
        """
        恢复工步
        :param request: wsapi request对象
        :return: 返回全部工步状态数据
        """
        steps_status = self.solution.steps_resume()
        default_response = self.make_response_without_error(request, steps_status)
        self.do_response(request, default_response)
        return default_response

    def on_step_reboot(self, request, entry):
        """
        重启工步
        :param request: wsapi request对象
        :return: 返回全部工步状态数据
        """
        steps_status = self.solution.steps_reboot(entry)
        default_response = self.make_response_without_error(request, steps_status)
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


@path.route(path='/newline/step/', method=['GET'])
def live(request):
    try:
        if request.headers['Upgrade'] != 'websocket':
            raise TypeError
        if request.headers['Connection'] != 'Upgrade':
            raise TypeError
    except:
        return HttpResponseBadRequest()

    return WebSocketNewLine(request)

