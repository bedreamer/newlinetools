# -*- coding: UTF-8 -*-
__author__ = 'lijie'
from . import driver
import zlg.can


class Driver(driver.BMSDevice):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.id = 0
        self.frame = zlg.can.CANFrame(1, 0, [1, 2, 3, 4, 5, 6])

    def run_step_forward(self):
        pass

    def pack_all(self):
        co = driver.CANFrameObject(self.value_item_list, self.frame)
        return co

