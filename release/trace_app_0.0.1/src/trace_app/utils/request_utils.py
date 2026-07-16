import json
import string
import urllib.parse

import tornado.httpclient as http_lib
from mg_app_framework import get_logger, MesCode, log_exception, HttpClient


async def send_url_request(url, method="POST", params=None, headers=None, previous_client=None):
    client = HttpClient(http_lib.AsyncHTTPClient(max_clients=1000))
    url = urllib.parse.quote(url, safe=string.printable)
    try:
        headers = headers or {}
        headers["Content-Type"] = "application/json"
        if method == "POST":
            res = await client.post(url=url, data=params, headers=headers, client_self=previous_client,
                                    request_timeout=60)
        else:
            res = await client.get(url=url, data=params, headers=headers, client_self=previous_client,
                                   request_timeout=60)
        data, code, msg = res.body, res.code, res.info
        client.close()
    except Exception as e:
        data, code, msg = '', MesCode.fail, e
    return data, code, msg


async def send_in_url_request(url, method="POST", params=None, headers=None, previous_client=None):
    client = HttpClient(http_lib.AsyncHTTPClient(max_clients=1000))
    url = urllib.parse.quote(url, safe=string.printable)
    get_logger().info('request url:%s', url)
    get_logger().info('request data:%s', params)
    try:
        headers = headers or {}
        headers["Content-Type"] = "application/json"
        if method == "POST":
            res = await client.post(url=url, data=params, headers=headers, client_self=previous_client,
                                    request_timeout=50)
        else:
            res = await client.get(url=url, data=params, headers=headers, client_self=previous_client,
                                   request_timeout=50)
        data, code, info = res.data, res.code, res.info
        client.close()
    except Exception as e:
        data, code, info = '', MesCode.fail, e
        get_logger().error(e)
    return data, code, info
