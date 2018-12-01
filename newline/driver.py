# -*- coding: UTF-8 -*-
__author__ = 'lijie'
import os
import codecs
import csv
from drivers import can
from drivers import modbus


class NewLineDeviceDriver(can.CANModbus):
    def __init__(self, model, can_dev_idx, can_ch_idx, bps, filter_list):
        super().__init__('USBCAN-2E-U', can_dev_idx, can_ch_idx, bps, filter_list)
        self.model = model
        default_csv_file_path = self.get_default_registers_csv_file_full_path()
        self.registers_list = list()
        self.load_registers_from_csv_file(default_csv_file_path)

    def get_default_registers_csv_file_full_path(self):
        dir_name = os.path.dirname(__file__)
        if dir_name[-1] == '/':
            return ''.join([dir_name, self.model, '-registers.csv'])
        else:
            return ''.join([dir_name, '/', self.model, '-registers.csv'])

    def load_registers_from_csv_file(self, csv_file_full_path):
        with codecs.open(csv_file_full_path) as file:
            lines = csv.DictReader(file)
            for line in lines:
                register = modbus.Register(**dict(line))
                self.registers_list.append(register)

    def read_all_data_registers(self, device):
        pass

    def run_step_forward(self):
        raise NotImplementedError

    def pack_all(self):
        raise NotImplementedError

    def get_conditions_map(self):
        obj_name = 'newline.'
        return {obj_name + register.name: obj_name + register.key for register in self.registers_list}

    def set_liuliang(self, liuliang, address_list=None):
        """
        设置流量
        :param liuliang:
        :return:
        """
        pass

    def set_wendu(self, wendu, address_list=None):
        """
        设置温度
        :param wendu:
        :return:
        """
        pass

    def set_xunhuan(self, xunhuan, address_list=None):
        """
        设置循环方式
        :param xunhuan:
        :return:
        """
        pass
