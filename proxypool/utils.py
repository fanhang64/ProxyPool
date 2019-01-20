import json
import functools

import requests
from requests.exceptions import ConnectionError

from proxypool.db import RedisClient

base_headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36',
    'Accept-Encoding': 'gzip, deflate, sdch',
    'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7'
}

_db = RedisClient()

def retry(attempt):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            att = 0
            while att < attempt:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    try:
                        proxies = _db.random()
                        return func(proxies=proxies, *args, **options)
                    except Exception as e:
                        att += 1
        return wrapper
    return decorator


@retry(2)
def get_page(url, proxies=None, **headers):
    """
    抓取代理
    :param url:
    :param headers:
    :return:
    """
    headers = dict(base_headers, **headers)
    print('正在抓取', url)
    try:
        response = requests.get(url, headers=headers, proxies=proxies)
        print('抓取成功', url, response.status_code)
        if response.status_code == 200:
            return response.text
    except ConnectionError:
        print('抓取失败', url)
        raise 


@retry(2)
def get_json(url, **headers):
    """
    抓取代理接口
    :param url:
    :param headers:
    :return:
    """
    headers = dict(base_headers, **headers)
    print(headers)
    print('正在抓取', url)
    try:
        response = requests.get(url, headers=headers)
        print('抓取成功', url, response.status_code)
        if response.status_code == 200:
            return response.json()
    except ConnectionError:
        print('抓取失败', url)
        raise
    except json.decoder.JSONDecodeError:
        print("解析错误", url)
        raise
