# -*- coding: UTF-8 -*-
__author__ = 'lijie'
import time
from .driver import NewLineDeviceDriver


class NewLineModbusDevice:
    def __init__(self, driver, address, registers_list):
        self.driver = driver
        self.address = address
        self.registers_list = registers_list[::]

        for register in self.registers_list:
            setattr(self, register.key, None)

    def read_all_data_registers(self):
        for register in self.registers_list:
            v = self.driver.read_register(self.address, register.addr)
            value = eval(register.to_display)
            setattr(self, register.key, value)

    def write_liuliang(self, liuliang):
        pass

    def write_wendu(self, wendu):
        pass

    def write_loop_mode(self, mode):
        pass

    def __str__(self):
        pairs = list()
        for register in self.registers_list:
            pair = '='.join([register.key, str(getattr(self, register.key))])
            pairs.append(pair)

        return ' '.join(pairs)


class Driver(NewLineDeviceDriver):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.id = 0

        self.newline_devices_list = [
            NewLineModbusDevice(self, addr, self.registers_list)
            for addr in range(1, 2)
        ]

        self.last_comm_tsp = 0

    def run_step_forward(self):
        now = time.time()
        if now - self.last_comm_tsp < 1:
            return
        self.last_comm_tsp = now

        for device in self.newline_devices_list:
            device.read_all_data_registers()

    def pack_all(self):
        return self.newline_devices_list[0]
