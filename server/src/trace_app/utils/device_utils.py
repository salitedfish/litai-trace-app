#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""设备相关工具"""


def normalize_device_codes(raw):
    """设备编码列表归一化：转字符串、去空白、丢空项、去重保序

    服务于看板配置里的「未使用的设备」：设置页让用户填逗号分隔的编码，
    前端已拆成数组，此处不信任客户端、按同口径再收一遍。

    去重是必要的——名单语义上就是个集合，重复项没有意义，还会让落库内容变脏。
    """
    if not isinstance(raw, (list, tuple, set)):
        return []
    result = []
    for item in raw:
        code = str(item).strip() if item is not None else ''
        if code and code not in result:
            result.append(code)
    return result
