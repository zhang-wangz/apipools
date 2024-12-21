# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   Change Activity:
                   2023/03/10: 支持带用户认证的代理格式 username:password@ip:port
-------------------------------------------------
"""

import re
import socket
from requests import head
from util.six import withMetaclass
from util.singleton import Singleton
from handler.configHandler import ConfigHandler
from util.user_agent import UserAgent

conf = ConfigHandler()

HEADER = {'User-Agent': UserAgent.get_random_ua(),
          'Accept': '*/*',
          'Connection': 'keep-alive',
          'Accept-Language': 'zh-CN,zh;q=0.8'}

IP_REGEX = re.compile(r"(.*:.*@)?\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{1,5}")


class ProxyValidator(withMetaclass(Singleton)):
    pre_validator = []
    http_validator = []
    https_validator = []
    socket4_validator = []
    socket5_validator = []

    @classmethod
    def addPreValidator(cls, func):
        cls.pre_validator.append(func)
        return func

    @classmethod
    def addHttpValidator(cls, func):
        cls.http_validator.append(func)
        return func

    @classmethod
    def addHttpsValidator(cls, func):
        cls.https_validator.append(func)
        return func

    @classmethod
    def addSocker4Validator(cls, func):
        cls.socket4_validator.append(func)
        return func

    @classmethod
    def addSocker5Validator(cls, func):
        cls.socket5_validator.append(func)
        return func


@ProxyValidator.addPreValidator
def formatValidator(proxy):
    """检查代理格式"""
    return True if IP_REGEX.fullmatch(proxy) else False


@ProxyValidator.addHttpValidator
def httpTimeOutValidator(proxy):
    """ http检测超时 """

    proxies = {"http": "http://{proxy}".format(proxy=proxy), "https": "https://{proxy}".format(proxy=proxy)}

    try:
        r = head(conf.httpUrl, headers=HEADER, proxies=proxies, timeout=conf.verifyTimeout)
        return True if r.status_code == 200 else False
    except Exception as e:
        return False


@ProxyValidator.addHttpsValidator
def httpsTimeOutValidator(proxy):
    """https检测超时"""

    proxies = {"http": "http://{proxy}".format(proxy=proxy), "https": "https://{proxy}".format(proxy=proxy)}
    try:
        r = head(conf.httpsUrl, headers=HEADER, proxies=proxies, timeout=conf.verifyTimeout, verify=False)
        return True if r.status_code == 200 else False
    except Exception as e:
        return False


def create_socket(proxy_host, proxy_port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(conf.verifyTimeout)
    sock.connect((proxy_host, proxy_port))
    return sock


@ProxyValidator.addSocker4Validator
def socket4TimeOutValidator(proxy):
    """socket4检测超时"""
    proxy = proxy.strip()
    host, port = proxy.split(":")
    try:
        with create_socket(host, port) as sock:
            request = b'\x04\x01\x00\x00\x00\x00\x00\x00\x00'  # SOCKS4 握手请求
            sock.sendall(request)
            response = sock.recv(8)
            if len(response) >= 8 and response[0] == 0x00:  # 0x00 表示成功
                return True
    except Exception as e:
        return False

@ProxyValidator.addSocker5Validator
def socket5TimeOutValidator(proxy):
    """socket5检测超时"""

    proxy = proxy.strip()
    host, port = proxy.split(":")
    try:
        with create_socket(host, port) as sock:
            sock.sendall(b'\x05\x01\x00')  # SOCKS5: 版本号 5，支持 0 个认证方法
            response = sock.recv(2)
            if response == b'\x05\x00':  # 服务器同意使用无认证
                return True
    except Exception as e:
        return False

@ProxyValidator.addHttpValidator
def customValidatorExample(proxy):
    """自定义validator函数，校验代理是否可用, 返回True/False"""
    return True


