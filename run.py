# -*- coding: UTF-8 -*-
__author__ = 'lijie'
import importlib
import solution
import httpd


def open_bms_device(model, can_dev_idx, can_ch_idx, bps, filter_list):
    # 打开bms设备
    m = importlib.import_module(''.join(['bms.', model]))
    return m.Driver(model, can_dev_idx, can_ch_idx, bps, filter_list)


def open_newline_device(model, can_dev_idx, can_ch_idx, bps, filter_list):
    # 打开newline设备
    m = importlib.import_module(''.join(['newline.', model]))
    return m.Driver(model, can_dev_idx, can_ch_idx, bps, filter_list)


def load_control_solution_from_file(bms, newline, control_solution_file_name):
    # 加载工步逻辑核心
    return solution.Solution(bms, newline, control_solution_file_name)


if __name__ == '__main__':
    bms_model = 'BXT12'
    newline_model = 'NCT100'

    bms = open_bms_device(model=bms_model, can_dev_idx=0, can_ch_idx=0, bps='125Kbps', filter_list=list())
    newline = open_newline_device(model=newline_model, can_dev_idx=0, can_ch_idx=1, bps='50Kbps', filter_list=list())

    control_solution_file_name = '_'.join([bms_model, newline_model, '.steps'])
    control_solution = load_control_solution_from_file(bms, newline, control_solution_file_name)

    web_server = httpd.httpd.simple_server(request_ext_param=(bms, newline, control_solution, ))
    web_server.startup()

    hold = True
    while hold is True:
        bms.run_step_forward()
        newline.run_step_forward()
        hold = control_solution.run_step_forward()
        web_server.run_step_forward(ttl=0.01)

