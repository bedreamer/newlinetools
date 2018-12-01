# -*- coding: UTF-8 -*-
__author__ = 'lijie'
from drivers import can
import os
import codecs
import csv


class CANFrame(object):
    def __init__(self, id, tsp, data, size=None):
        self.id = id
        self.tsp = tsp
        if isinstance(data, list) or isinstance(data, tuple):
            self.data = data
        else:
            self.data = list(data)[: size]

    def __str__(self):
        data = " ".join(["%02X" % data for data in self.data])
        sid = "%08X:" % self.id
        return "".join([str(self.tsp), " ", sid, ' [', data, ']'])

    def bits(self):
        m_list = [bin(x)[2:] for x in self.data]
        x_list = [('0' * (8-len(x)), x) for x in m_list]
        s_list = [''.join(x)[::-1] for x in x_list]
        return ''.join(s_list)


class CANFrameDBC:
    def __init__(self, path):
        self.path = path


class CANFrameField:
    def __init__(self, key, name, bit_offset, bit_width):
        self.key = key
        self.name = name
        self.bit_offset = bit_offset
        self.bit_width = bit_width

    @classmethod
    def compile(cls, bits):
        return int(bits[::-1], 2)


def make_can_frame_field(**kwargs):
    return CANFrameField(kwargs['key'], kwargs['name'], int(kwargs['bit_offset']), int(kwargs['bit_width']))


class CANFrameObject:
    def __init__(self, can_frame_fields_list, can_frame_object):
        self.can_frame_fields_list = can_frame_fields_list
        self.can_frame = can_frame_object

        self.can_bits = self.can_frame.bits()
        self.field_map = dict()

    def __getattr__(self, item):
        try:
            return self.field_map[item]
        except KeyError:
            for field in self.can_frame_fields_list:
                if field.key != item:
                    continue

                value = self.read_field_value(field)
                self.field_map[item] = value
                return value

            raise ValueError('no value named', item)

    def read_field_value(self, field):
        begin = field.bit_offset
        end = field.bit_offset + field.bit_width

        bits = self.can_bits[begin:end]
        return field.compile(bits)


class BMSDevice(can.CANChannel):
    def __init__(self, model, can_dev_idx, can_ch_idx, bps, filter_list):
        self.model = model
        super().__init__('USBCAN-2E-U', can_dev_idx, can_ch_idx, bps, filter_list)
        default_csv_file_path = self.get_default_registers_csv_file_full_path()
        self.value_item_list = list()
        self.load_value_item_from_csv_file(default_csv_file_path)

    def get_default_registers_csv_file_full_path(self):
        dir_name = os.path.dirname(__file__)
        if dir_name[-1] == '/':
            return ''.join([dir_name, self.model, '-items.csv'])
        else:
            return ''.join([dir_name, '/', self.model, '-items.csv'])

    def load_value_item_from_csv_file(self, csv_file_full_path):
        with codecs.open(csv_file_full_path) as file:
            lines = csv.DictReader(file)
            for line in lines:
                item = make_can_frame_field(**dict(line))
                self.value_item_list.append(item)

    def run_step_forward(self):
        raise NotImplementedError

    def get_frame(self):
        pass

    def pack_all(self):
        raise NotImplementedError

    def get_conditions_map(self):
        return {"bms." + item.name: "bms." + item.key for item in self.value_item_list}


if __name__ == '__main__':
    frame = CANFrame(1, 0, [1, 2, 3, 4, 5, 6])
    f_list = [
        CANFrameField("电压", 'voltage', 0, 8),
        CANFrameField("电流", 'current', 8, 8),
        CANFrameField("温度", 'temp', 16, 8),
    ]

    co = CANFrameObject(f_list, frame)
    print('voltage:', co.voltage)
    print('current:', co.current)
    print('temp:', co.temp)
    print('temp:', co.temp)
