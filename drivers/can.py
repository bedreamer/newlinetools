# -*- coding: UTF-8 -*-
__author__ = 'lijie'
import zlg.can as usbcan
import zlg.comcan.modbus as modbus


class CANChannel(object):
    def __init__(self, model, can_dev_idx, can_ch_idx, bps, filter_list):
        self.device_handle = usbcan.open_device_by_model(model, can_dev_idx)
        self.channel_handle = usbcan.open_channel(self.device_handle, can_ch_idx, bps)


class CANModbus(object):
    def __init__(self, model, can_dev_idx, can_ch_idx, bps, filter_list):
        self.device_handle = usbcan.open_device_by_model(model, can_dev_idx)
        self.channel_handle = usbcan.open_channel(self.device_handle, can_ch_idx, bps)

    def read_register(self, server_address, register_address):
        return modbus.read_register(self.channel_handle, server_address, register_address)

    def write_register(self, server_address, register_address, short_value):
        return modbus.write_register(self.channel_handle, server_address, register_address, short_value)