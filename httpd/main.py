# -*- coding: UTF-8 -*-
__author__ = 'lijie'
import socket
import select


class HttpServer:
    def __init__(self, address, basedir):
        self.fds = socket.socket()
        self.fds.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
        self.fds.bind(address)
        self.fds.listen(15)

    def run_step_forward(self, ttl=None):
        if ttl is None:
            # 50 ms
            ttl = 0.05

        r, w, _ = select.select([], [], [], ttl)
