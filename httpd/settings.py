# -*- coding: UTF-8 -*-
__author__ = 'lijie'
import os
from mgexception import *


# 服务器参数
server_iface = '0.0.0.0'
server_port = 8888


# 模板目录位置
template_dirs = [
    os.path.abspath(__file__).strip(os.path.basename(__file__)) + 'templates/templates',
    os.path.abspath(__file__).strip(os.path.basename(__file__)) + 'templates',
]

# 用户定义的过滤器模块映射
template_user_filters = {
    'userfileter': 'userfilter'
}

# 静态文件存放目录
www_dir = os.path.abspath(__file__).strip(os.path.basename(__file__)) + 'www'


# 最大传输块大小
max_transport_unit_size = 32 * 1024

# 文件缓存目录
cache_directory = os.path.abspath(__file__).strip(os.path.basename(__file__)) + 'cache/'


# 系统运行数据根目录
data_root_directory = os.path.abspath(__file__).strip(os.path.basename(__file__)) + 'data/'


# 登录最大允许时间
max_seconds_hold_by_session = 3600
