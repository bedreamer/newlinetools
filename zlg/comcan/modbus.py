# -*- coding: utf8 -*-
# 使用CAN卡的MODBUS转发功能进行数据通讯
import sys
import os
sys.path.append(os.path.dirname(__file__))

from ..can import CANFrame
from ..can import send_frame as api_send_frame
from ..can import get_frame as api_get_frame
import time
import struct


def read_register(usbcan_channel_handle, server_address, register_address):
    """
    读取寄存器的值
    :param usbcan_channel_handle: USBCAN的句柄
    :param server_address: MODBUS服务器地址
    :param register_register: 寄存器地址
    :return:
    """
    data = [0x00, 0x03, ((register_address>>8) & 0xff), (register_address & 0xff), 0x00, 0x01]
    frame_to_be_send = CANFrame(id=server_address, tsp=time.strftime("%Y-%m-%d %H:%M:%S"), data=data)
    count = api_send_frame(usbcan_channel_handle, [frame_to_be_send])
    if count != 1:
        raise ValueError("send frame failed.")

    #print("send", frame_to_be_send)

    retry = 0
    while retry < 3:
        frames = api_get_frame(usbcan_channel_handle, count=1, wait_ms=800)
        if len(frames) == 0:
            retry += 1
            if retry == 3:
                raise ValueError("recv frame failed.")
        else:
            break

    frame = frames[0]
    #print("recv", frame)

    if frame.id == 0x83:
        raise ValueError("MODBUS返回异常", str(frame))

    if frame.data[2] != 2:
        raise ValueError("MODBUS返回数据长度不符", str(frame))

    s_data = struct.pack("BB", frame.data[3], frame.data[4])
    s_short = struct.unpack(">h", s_data)
    #print(server_address, register_address, s_short[0])
    return s_short[0]


def write_register(usbcan_channel_handle, server_address, register_address, short_value):
    """
    写寄存器的值
    :param usbcan_channel_handle: USBCAN的句柄
    :param server_address: MODBUS服务器地址
    :param register_register: 寄存器地址
    :return:
    """
    data = [0x00, 0x03, ((register_address>>8) & 0xff), (register_address & 0xff), 0x00, 0x01]
    frame_to_be_send = CANFrame(id=server_address, tsp=time.strftime("%Y-%m-%d %H:%M:%S"), data=data)
    count = api_send_frame(usbcan_channel_handle, [frame_to_be_send])
    if count != 1:
        raise ValueError("send frame failed.")

    #print("send", frame_to_be_send)

    retry = 0
    while retry < 3:
        frames = api_get_frame(usbcan_channel_handle, count=1, wait_ms=800)
        if len(frames) == 0:
            retry += 1
            if retry == 3:
                raise ValueError("recv frame failed.")
        else:
            break

    frame = frames[0]
    #print("recv", frame)

    if frame.id == 0x83:
        raise ValueError("MODBUS返回异常", str(frame))

    if frame.data[2] != 2:
        raise ValueError("MODBUS返回数据长度不符", str(frame))

    s_data = struct.pack("BB", frame.data[3], frame.data[4])
    s_short = struct.unpack(">h", s_data)
    #print(server_address, register_address, s_short[0])
    return s_short[0]
