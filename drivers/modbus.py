# -*- coding: UTF-8 -*-
__author__ = 'lijie'
import zlg.can as usbcan


class CANModbus(object):
    pass


class Register(object):
    def __init__(self, **kwargs):
        self.id = 0
        self.name = None
        self.key = None
        self.addr = 0
        self.to_display = None
        self.to_modbus = None

        for key, value in kwargs.items():
            setattr(self, key, value)

        self.id = int(self.id)
        self.addr = int(self.addr)

    def set_id(self, id):
        self.id = int(id)

    def set_name(self, name):
        self.name = name

    def set_address(self, address):
        self.addr = int(address)

    def set_default(self, default):
        self.v = int(default)

    def set_k(self, k):
        self.k = int(k)

    def set_b(self, b):
        self.b = int(b)
