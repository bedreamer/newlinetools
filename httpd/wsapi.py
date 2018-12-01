# -*- coding: UTF-8 -*-
__author__ = 'lijie'
import time
import json
from response import *


class WsApiLocalRequestPackage:
    def __init__(self, cmd, rid, level, data):
        self.cmd = cmd
        self.rid = rid
        self.level = level
        self.data = data

        self.on_error = None
        self.on_success = None

    @property
    def __dict__(self):
        return dict(cmd=self.cmd, rid=self.rid, level=self.level, data=self.data)

    def success(self, callback):
        self.on_success = callback
        return self

    def error(self, callback):
        self.on_error = callback
        return self


class WsApiRemoteRequestPackage:
    pass


class WsApiResponsePackage:
    pass


class WsApiGateWay(HttpResponseWebSocket):
    def __init__(self, request):
        self.request_id_seq = 81192
        self.local_request_list = list()
        super().__init__(request)

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

    def disconnect(self, close_code):
        self.on_disconnect(close_code)

    # 以下函数为web socket相关性函数
    def on_text_frame(self, text_data):
        obj = json.loads(text_data)

        if 'status' not in obj:
            remote_request = self.compile_remote_request_from_dict(obj)
            setattr(remote_request, 'atsp', self.get_datetime_string())

            remote_request_function_name = ''.join(['on_', remote_request.cmd, '_request'])
            callback = getattr(self, remote_request_function_name, self.on_default_request)
            callback(remote_request)
        else:
            response = self.compile_response_from_dict(obj)
            local_request = self.get_response_pair(response)

            if response.status != 'ok':
                local_request.on_error(local_request, response)
            else:
                local_request.on_success(local_request, response)

    def on_connect(self):
        return True

    def on_disconnect(self, close_code):
        pass

    # 以下为功能支持性函数
    @classmethod
    def get_datetime_string(cls):
        return time.strftime("%Y-%m-%d %H:%M:%S")

    def get_response_pair(self, response):
        local_request_idx = None
        for idx, request in enumerate(self.local_request_list):
            if request.rid == response.rid:
                local_request_idx = idx
                break

        if local_request_idx is None:
            return None

        return self.local_request_list.pop(local_request_idx)

    def get_request_id(self):
        if self.request_id_seq > 100000:
            self.request_id_seq = 81192

        rid = self.request_id_seq
        self.request_id_seq += 1
        return rid

    def make_local_request_package(self, cmd, level, data, **kwargs):
        request = WsApiLocalRequestPackage(cmd, self.get_request_id(), level, data)

        for key, value in kwargs.items():
            setattr(request, key, value)

        return request

    @classmethod
    def make_response_with_error(cls, request, code, reason, data, **kwargs):
        response = WsApiResponsePackage()

        setattr(response, 'cmd', request.cmd)
        setattr(response, 'rid', request.rid)
        setattr(response, 'level', request.level)

        setattr(response, 'code', code)
        setattr(response, 'status', 'error')
        setattr(response, 'reason', reason)

        setattr(response, 'data', data)

        for key, value in kwargs.items():
            setattr(response, key, value)

        return response

    @classmethod
    def make_response_without_error(cls, request, data, **kwargs):
        response = WsApiResponsePackage()

        setattr(response, 'cmd', request.cmd)
        setattr(response, 'rid', request.rid)
        setattr(response, 'level', request.level)

        setattr(response, 'code', 0)
        setattr(response, 'status', 'ok')
        setattr(response, 'reason', '')

        setattr(response, 'data', data)

        for key, value in kwargs.items():
            setattr(response, key, value)

        return response

    @classmethod
    def compile_remote_request_from_dict(cls, obj):
        remote_request = WsApiRemoteRequestPackage()
        for key, value in obj.items():
            setattr(remote_request, key, value)
        return remote_request

    @classmethod
    def compile_response_from_dict(cls, obj):
        response = WsApiResponsePackage()
        for key, value in obj.items():
            setattr(response, key, value)
        return response

    # 异常应答函数
    # 服务未就绪
    def make_out_of_service_response(self, remote_request, data, **kwargs):
        return self.make_response_with_error(remote_request, 100, "out of service", data, **kwargs)

    # 无效的请求
    def make_invalid_request_response(self, remote_request, data, **kwargs):
        return self.make_response_with_error(remote_request, 100, "request invalid", data, **kwargs)

    # 未登录
    def make_not_login_response(self, remote_request, data, **kwargs):
        return self.make_response_with_error(remote_request, 100, "not login", data, **kwargs)

    # 登录过期
    def make_login_expired_response(self, remote_request, data, **kwargs):
        return self.make_response_with_error(remote_request, 100, "login expired", data, **kwargs)

    # 未知异常
    def make_unknown_exception_response(self, remote_request, data, **kwargs):
        return self.make_response_with_error(remote_request, 100, "unknown exception", data, **kwargs)

    # 未实现
    def make_not_implement_response(self, remote_request, data, **kwargs):
        return self.make_response_with_error(remote_request, 100, "not implement", data, **kwargs)

    # 以下函数为业务相关性函数
    def on_default_request(self, remote_request):
        default_response = self.make_not_implement_response(remote_request, None)
        self.do_response(remote_request, default_response)
        return default_response

    def on_default_response_with_error(self, local_request, response):
        pass

    def on_default_response_without_error(self, local_request, response):
        pass

    def do_request(self, request):
        self.local_request_list.append(request)
        self.send(text_data=json.dumps(request.__dict__))

    def do_response(self, remote_request, response):
        setattr(response, 'atsp', remote_request.atsp)
        setattr(response, 'btsp', self.get_datetime_string())
        self.send(text_data=json.dumps(response.__dict__))

    # init 业务处理
    def on_init_request(self, remote_request):
        return self.on_default_request(remote_request)

    def do_init_request(self, data):
        local_request = self.make_local_request_package(cmd='init', level=1, data=data)
        local_request.success(self.on_init_response_without_error)
        local_request.error(self.on_init_response_with_error)
        self.do_request(local_request)
        return local_request

    def on_init_response_with_error(self, local_request, response):
        pass

    def on_init_response_without_error(self, local_request, response):
        pass

    # ping 业务处理
    def on_ping_request(self, remote_request):
        return self.on_default_request(remote_request)

    def do_ping_request(self, data):
        local_request = self.make_local_request_package(cmd='ping', level=5, data=data)
        local_request.success(self.on_ping_response_without_error)
        local_request.error(self.on_ping_response_with_error)
        self.do_request(local_request)
        return local_request

    def on_ping_response_with_error(self, local_request, response):
        pass

    def on_ping_response_without_error(self, local_request, response):
        pass

    # print 业务处理
    def on_print_request(self, remote_request):
        head = ''.join(['[', self.get_datetime_string(), '@', self.client[0], ':', str(self.client[1]), ']'])

        try:
            print(head, remote_request.data)
        except:
            print(head, None)

        response = self.make_response_without_error(remote_request, None)
        return self.do_response(remote_request, response)

    def do_print_request(self, data):
        local_request = self.make_local_request_package(cmd='print', level=99, data=data)
        local_request.success(self.on_print_response_without_error)
        local_request.error(self.on_print_response_with_error)
        self.do_request(local_request)
        return local_request

    def on_print_response_with_error(self, local_request, response):
        pass

    def on_print_response_without_error(self, local_request, response):
        pass

    # href 业务处理
    def on_href_request(self, remote_request):
        return self.make_invalid_request_response(remote_request, None)

    def do_href_request(self, data):
        local_request = self.make_local_request_package(cmd='href', level=6, data=data)
        local_request.success(self.on_href_response_without_error)
        local_request.error(self.on_href_response_with_error)
        self.do_request(local_request)
        return local_request

    def on_href_response_with_error(self, local_request, response):
        pass

    def on_href_response_without_error(self, local_request, response):
        pass

    # push 业务处理
    def on_push_request(self, remote_request):
        return self.on_default_request(remote_request)

    def do_push_request(self, data):
        local_request = self.make_local_request_package(cmd='push', level=7, data=data)
        local_request.success(self.on_push_response_without_error)
        local_request.error(self.on_push_response_with_error)
        self.do_request(local_request)
        return local_request

    def on_push_response_with_error(self, local_request, response):
        pass

    def on_push_response_without_error(self, local_request, response):
        pass

    # query 业务处理
    def on_query_request(self, remote_request):
        return self.on_default_request(remote_request)

    def do_query_request(self, data):
        local_request = self.make_local_request_package(cmd='query', level=8, data=data)
        local_request.success(self.on_query_response_without_error)
        local_request.error(self.on_query_response_with_error)
        self.do_request(local_request)
        return local_request

    def on_query_response_with_error(self, local_request, response):
        pass

    def on_query_response_without_error(self, local_request, response):
        pass

    # rebase 业务处理
    def on_rebase_request(self, remote_request):
        if not self.user.is_authenticated:
            response = self.make_not_login_response(remote_request, data='login first', repair='/login/')
            return self.do_response(remote_request, response)

        return self.on_default_request(remote_request)

    def do_rebase_request(self, data):
        local_request = self.make_local_request_package(cmd='rebase', level=6, data=data)
        local_request.success(self.on_rebase_response_without_error)
        local_request.error(self.on_rebase_response_with_error)
        self.do_request(local_request)
        return local_request

    def on_rebase_response_with_error(self, local_request, response):
        pass

    def on_rebase_response_without_error(self, local_request, response):
        pass

    # debug 业务处理
    def on_debug_request(self, remote_request):
        return self.on_default_request(remote_request)

    def do_debug_request(self, data):
        local_request = self.make_local_request_package(cmd='debug', level=0, data=data)
        local_request.success(self.on_debug_response_without_error)
        local_request.error(self.on_debug_response_with_error)
        self.do_request(local_request)
        return local_request

    def on_debug_response_with_error(self, local_request, response):
        pass

    def on_debug_response_without_error(self, local_request, response):
        pass

    # yt 业务处理
    def on_yt_request(self, remote_request):
        if not self.user.is_authenticated:
            response = self.make_not_login_response(remote_request, 'login first', repair='/login/')
            return self.do_response(remote_request, response)

        return self.on_default_request(remote_request)

    def do_yt_request(self, data):
        local_request = self.make_local_request_package(cmd='yt', level=7, data=data)
        local_request.success(self.on_yt_response_without_error)
        local_request.error(self.on_yt_response_with_error)
        self.do_request(local_request)
        return local_request

    def on_yt_response_with_error(self, local_request, response):
        pass

    def on_yt_response_without_error(self, local_request, response):
        pass

    # yk 业务处理
    def on_yk_request(self, remote_request):
        if not self.user.is_authenticated:
            response = self.make_not_login_response(remote_request, 'login first', repair='/login/')
            return self.do_response(remote_request, response)

        return self.on_default_request(remote_request)

    def do_yk_request(self, data):
        local_request = self.make_local_request_package(cmd='yk', level=7, data=data)
        local_request.success(self.on_yk_response_without_error)
        local_request.error(self.on_yk_response_with_error)
        self.do_request(local_request)
        return local_request

    def on_yk_response_with_error(self, local_request, response):
        pass

    def on_yk_response_without_error(self, local_request, response):
        pass
