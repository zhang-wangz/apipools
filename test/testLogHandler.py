# -*- coding: utf-8 -*-

from handler.logHandler import LogHandler


def testLogHandler():
    log = LogHandler('test')
    log.info('this is info')
    log.error('this is error')


if __name__ == '__main__':
    testLogHandler()
