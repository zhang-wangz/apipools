# -*- coding: utf-8 -*-

from helper.validator import ProxyValidator


def testProxyValidator():
    for _ in ProxyValidator.pre_validator:
        print(_)
    for _ in ProxyValidator.http_validator:
        print(_)
    for _ in ProxyValidator.https_validator:
        print(_)


if __name__ == '__main__':
    testProxyValidator()
