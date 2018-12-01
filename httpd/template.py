# -*- coding: UTF-8 -*-
__author__ = 'lijie'
import django.template as dj
import settings
from response import *


def render(request, template_file_path, ctx=None, cookie=None):
    if ctx is None:
        ctx = dict()

    # 初始化模板环境
    env = dj.Engine(dirs=settings.template_dirs, libraries=settings.template_user_filters)
    template = env.get_template(template_file_path)
    context = dj.Context()
    for key, value in ctx.items():
        context[key] = value
    context['request'] = request

    body = template.render(context)
    respons = HttpResponseHtml(body, cookie=cookie, headers=[('Cache-Control', 'max-age=0')])
    return respons


