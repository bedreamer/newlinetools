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

    def get_register(self, name):
        for register in self.registers_list:
            if name == register.name:
                return register
        return None

    def write_liuliang(self, display_liuliang):
        register = self.get_register('流量')
        if register is None:
            return

        v = display_liuliang
        modbus_value = eval(register.to_modbus)
        self.driver.write_register(self.address, register.addr, modbus_value)

    def write_wendu(self, display_wendu):
        pass

    def write_loop_mode(self, display_mode):
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

    def sync_value_immediately(self, step):
        """
        立即下发工步设定的输出值
        :param step:
        :return:
        """
        if isinstance(step.liuliang, float) or isinstance(step.liuliang, int):
            liuliang = float(step.liuliang)
        else:
            liuliang = None

        if isinstance(step.wendu, float) or isinstance(step.wendu, int):
            wendu = float(step.wendu)
        else:
            wendu = None

        if step.xunhuan == '内循环':
            xunhuan = 0
        elif step.xunhuan == '外循环':
            xunhuan = 1
        else:
            xunhuan = None

        newline_device = self.newline_devices_list[0]
        if liuliang is not None:
            newline_device.write_liuliang(liuliang)

        if wendu is not None:
            newline_device.write_wendu(wendu)

        if xunhuan is not None:
            newline_device.write_loop_mode(xunhuan)

    def sync_value_period(self, step):
        """
        周期下发工步设置值
        :param step:
        :return:
        """
        print(step)
