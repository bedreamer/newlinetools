# -*- coding: UTF-8 -*-
__author__ = 'lijie'
import view
import path
import time
import http.cookies as cookies
import auth.session
from selector import Selector


class PostData:
    def __init__(self, body, context_type):
        super().__init__()
        self.all = dict()

        body = body.decode()
        if context_type == 'application/x-www-form-urlencoded':
            pairs_list = body.split('&')
            for pair in pairs_list:
                try:
                    key, value = pair.split('=')
                except:
                    key, value = pair, ''

                try:
                    self.all[key].append(value)
                except:
                    self.all[key] = list((value,))

    def __getitem__(self, item):
        if item not in self.all:
            return None

        values = self.all[item]
        if len(values) == 1:
            return values[0]
        else:
            return values


class GetData:
    def __init__(self, query_string):
        super().__init__()
        self.all = dict()
        body = query_string
        pairs_list = body.split('&')
        for pair in pairs_list:
            try:
                key, value = pair.split('=')
            except:
                key, value = pair, ''

            try:
                self.all[key].append(value)
            except:
                self.all[key] = list((value,))

    def __getitem__(self, item):
        if item not in self.all:
            return None

        values = self.all[item]
        if len(values) == 1:
            return values[0]
        else:
            return values


class Uri:
    """URI 参数列表"""
    def __init__(self, url, **kwargs):
        self.url = url
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __str__(self):
        return self.url


class HttpRequest:
    def __init__(self, conn, addr, **kwargs):
        self.conn = conn

        self.kwargs = kwargs

        self.addr = addr
        self.down = False

        self.receive_bytes = b''

        self.request_head_lines = None
        self.method, self.url, self.version, self.headers = None, None, None, None
        self.path, self.query_string = None, None

        # HTTP 请求header接收完成
        self.headers_ready = False
        # HTTP 请求body长度
        self.body_length = 0
        # HTTP 请求body格式
        self.body_format = ''
        # HTTP 请求body接收完成
        self.body_ready = False
        # HTTP body data.
        self.body = b''

        # 用于存储URL参数
        self.uri = None
        self.GET = None
        self.POST = None
        self.cookie = None
        self.user = None

        self.response = None
        self.reused = 0

    def ready_for_next_request(self):
        self.request_head_lines = None
        self.method, self.url, self.version, self.headers = None, None, None, None
        self.path, self.query_string = None, None

        # HTTP 请求header接收完成
        self.headers_ready = False
        # HTTP 请求body长度
        self.body_length = 0
        # HTTP 请求body格式
        self.body_format = ''
        # HTTP 请求body接收完成
        self.body_ready = False
        # HTTP body data.
        self.body = b''

        # 用于存储URL参数
        self.uri = None
        self.GET = None
        self.POST = None
        self.cookie = None
        self.user = None

        self.response = None
        self.reused += 1

    def file(self):
        return self.conn

    def mark_down(self):
        self.down = True

    def setup(self, selector):
        """
        called by selector while every single loop head
        :param selector:
        :return:
        """
        if not self.down:
            selector.register(self, Selector.EVREADABLE)
            if self.response is not None:
                selector.register(self, Selector.EVWRITABLE)
        else:
            selector.unregister(self, Selector.EVREADABLE)
            selector.unregister(self, Selector.EVWRITABLE)
            self.end()

    def read(self, n):
        try:
            return self.conn.recv(n)
        except:
            self.mark_down()
            return b''

    def write(self, data):
        try:
            if isinstance(data, str):
                return self.conn.send(data.encode())
            else:
                return self.conn.send(data)
        except Exception as e:
            print(__file__, e)
            self.mark_down()
            return None

    def on_readable(self):
        """
        called while self.file() is readable
        :return:
        """
        data = self.read(2048)
        if len(data) == 0:
            print(self.path, "closed", self.addr)
            self.mark_down()
            if self.response is None:
                return
            else:
                self.response.on_connection_down(self)
                return

        # 用于处理重复利用的连接
        #if self.response is not None and self.response.is_body_sent() is True:
        #    if self.headers['Connection'].lower() == 'keep-alive':
        #        self.ready_for_next_request()
        #    else:
        #        self.mark_down()
        #        return

        # 接收header
        if self.headers_ready is False:
            self.receive_bytes = b''.join([self.receive_bytes, data])
            data = b''
            terminal_idx = self.receive_bytes.find(b'\r\n\r\n')
            if terminal_idx < 0:
                return

            header_bytes = self.receive_bytes[:terminal_idx]
            remain_bytes = self.receive_bytes[terminal_idx + 4:]

            self.request_head_lines = header_bytes.decode().split('\r\n')

            self.method, self.url, self.version = self.request_head_lines.pop(0).split(' ')
            self.headers = {line.split(':')[0]: line.split(':')[1].strip() for line in self.request_head_lines}
            if 'Connection' not in self.headers:
                self.headers['Connection'] = 'closed'

            if '?' in self.url:
                self.path, self.query_string = self.url.split('?')
            else:
                self.path, self.query_string = self.url, ''

            self.headers_ready = True
            if 'Content-Length' not in self.headers:
                self.body_ready = True
            else:
                self.body_length = int(self.headers['Content-Length'])

            self.body = remain_bytes

        # body not ready
        if self.body_ready is False:
            self.body = b''.join([self.body, data])
            if len(self.body) < self.body_length:
                return
            else:
                self.body_ready = True

            try:
                self.body_format = self.headers['Content-Type']
            except KeyError:
                self.body_format = ''

        # body ready
        if self.response is None:
            if 'Cookie' in self.headers:
                self.cookie = cookies.SimpleCookie(self.headers['Cookie'])
                if 'sid' in self.cookie:
                    self.user = auth.session.load_from_session(self.cookie['sid'].value)
                else:
                    self.user = auth.user.UserUnkown()
            else:
                self.cookie = cookies.SimpleCookie()
                self.user = auth.user.UserUnkown()

            self.GET = GetData(self.query_string)
            self.POST = PostData(self.body, self.body_format)
            params_dict, processor, kwargs = path.search_route_path(self)
            self.uri = Uri(self.url, **dict(params_dict, **kwargs))

            response = processor(self, **params_dict)
            print(time.strftime("[%Y-%m-%d %H:%M:%S]"), self.method, self.path, len(response), response.code,
                  response.status, self.addr)
            self.response = response
        else:
            self.response.on_body_received(self, data)

    def get_cookie(self):
        if 'Cookie' not in self.headers:
            return dict()
        else:
            pass

    def on_writable(self):
        """
        called while self.file() is writable
        :return:
        """
        if self.down is True:
            return

        if self.response is None:
            return

        if self.reused > 0:
            print("got it", self.path, self.addr)

        if self.response.is_header_sent() is False:
            self.response.response_header(self)
        elif self.response.is_body_sent() is False:
            self.response.response_body(self)
        else:
#            if self.headers['Connection'].lower() == 'closed':
            self.mark_down()

    def begin(self):
        """
        called by Server while a connection is incoming.
        test connection is hold neccessory or not
        :return: False connection will be aborted True will hold.
            if need hold this connection.
        """
        return True

    def end(self):
        """
        called by self while connection down or called by Server while reject a connection incoming.
        :return:
        """
        if self.conn:
            self.conn.close()
            self.conn = None
            #print("closed.")

