# -*- coding: utf8 -*-
from ._types import _VCI_CAN_OBJ
from ctypes import *
import random
import time


def VCI_OpenDevice(a, b, c):
    return 1


def VCI_ReadBoardInfo(a):
    return 1


def VCI_CloseDevice(a, b):
    return 0


def VCI_SetReference(a, b, c, d, e):
    return 1


def VCI_InitCAN(a, b, c, d):
    return 1


def VCI_StartCAN(a, b, c):
    return 1


def VCI_ClearBuffer(a, b, c):
    return 1


def VCI_GetReceiveNum(a, b, c):
    return 1


def VCI_Receive(a, b, c, l, count, e):
    l[0][0].ID = 1
    l[0][0].DataLen = 8
    l[0][0].Data = tuple((0, 3, 2, random.randrange(0, 255), random.randrange(0, 255), 6, 7, 8))
    time.sleep(0.05)
    return count


def VCI_Transmit(a, b, c, d, count):
    time.sleep(0.05)
    return count