# -*- coding: UTF-8 -*-
__author__ = 'lijie'
import select
import socket
import sys
import os

sys.path.append('.')

import settings
from selector import Selector
from request import HttpRequest


socket.socket.write = socket.socket.send


class TCPServerBasic(object):
    """
    TCP服务器
    usage:
        server = TCPServer('0.0.0.0', 8000)
        server.run_forever()
    """
    def __init__(self, ip, port, ReqeustHandle, **kwargs):
        self.loop = Selector()

        self.ip = ip
        self.port = port
        self.RequestHandle = ReqeustHandle
        self.kwargs = kwargs

        self.server = socket.socket()
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)

    def file(self):
        return self.server

    def setup(self, selector):
        selector.register(self, Selector.EVREADABLE)

    def on_readable(self):
        """
        服务器句柄可读
        """
        conn, addr = self.server.accept()

        connection = self.RequestHandle(conn, addr, **self.kwargs)

        hold = connection.begin()
        if hold is False:
            print("new connection aborted by", self.RequestHandle.__name__)
            connection.end()
        else:
            #print("new connection accepted.")
            connection.setup(self.loop)

    def on_writable(self):
        raise NotImplemented

    def startup(self):
        self.server.bind((self.ip, self.port))
        self.server.listen(15)
        self.setup(self.loop)

    def run_step_forward(self, ttl=None):
        self.loop.run_step_forward(ttl)

    def run_forever(self):
        self.startup()
        while True:
            self.run_step_forward()


def simple_server(server_iface=None, server_port=None, **kwargs):
    print("load configuration from settings.py")
    print("you can access this site by: http://%s:%d/"%(settings.server_iface, settings.server_port))
    return TCPServerBasic(settings.server_iface, settings.server_port, HttpRequest, **kwargs)


if __name__ == '__main__':
    server = simple_server()
    server.run_forever()
