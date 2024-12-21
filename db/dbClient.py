# -*- coding: utf-8 -*-
# !/usr/bin/env python
"""
-------------------------------------------------
   Change Activity:
                   2016/12/02:   DB工厂类
                   2020/07/03:   取消raw_proxy储存
-------------------------------------------------
"""

import os
import sys

from handler.configHandler import ConfigHandler
from util.six import urlparse, withMetaclass
from util.singleton import Singleton
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
class DbClient(withMetaclass(Singleton)):
    """
    DbClient DB工厂类 提供get/put/update/pop/delete/exists/getAll/clean/getCount/changeTable方法


    抽象方法定义：
        get(): 随机返回一个proxy;
        put(proxy): 存入一个proxy;
        pop(): 顺序返回并删除一个proxy;
        update(proxy): 更新指定proxy信息;
        delete(proxy): 删除指定proxy;
        exists(proxy): 判断指定proxy是否存在;
        getAll(): 返回所有代理;
        clean(): 清除所有proxy信息;
        getCount(): 返回proxy统计信息;
        changeTable(name): 切换操作对象


        所有方法需要相应类去具体实现：
            ssdb: ssdbClient.py
            redis: redisClient.py
            mongodb: mongodbClient.py

    """

    def __init__(self, db_conn):
        """
        init
        :return:
        """
        self.parseDbConn(db_conn)
        self.__initDbClient()

    @classmethod
    def parseDbConn(cls, db_conn):
        # 暂时只使用sqlite进行读取数据
        if "sqlite" in db_conn:
            # sqlite只需要链接
            cls.db_url = db_conn
            # 暂时没啥用
            cls.db_type = "SQLITE"
            cls.db_host = ""
            cls.db_port = ""
            cls.db_user = ""
            cls.db_pwd = ""
            cls.db_name = ""
            return cls
        db_conf = urlparse(db_conn)
        cls.db_type = db_conf.scheme.upper().strip()
        cls.db_host = db_conf.hostname
        cls.db_port = db_conf.port
        cls.db_user = db_conf.username
        cls.db_pwd = db_conf.password
        cls.db_name = db_conf.path[1:]
        return cls

    def __initDbClient(self):
        """
        init DB Client
        :return:
        """
        __type = None
        if "SQLITE" == self.db_type:
            __type = "sqliteClient"
        else:
            pass
        assert __type, 'type error, Not support DB type: {}'.format(self.db_type)
        self.client = getattr(__import__(__type), "%sClient" % self.db_type.title())(host=self.db_host,
                                                                                     port=self.db_port,
                                                                                     username=self.db_user,
                                                                                     password=self.db_pwd,
                                                                                     db=self.db_name,
                                                                                     db_url=self.db_url)

    def get(self, https, **kwargs):
        return self.client.get(https, **kwargs)

    def put(self, key, **kwargs):
        return self.client.put(key, **kwargs)

    def update(self, key, value, **kwargs):
        return self.client.update(key, value, **kwargs)

    def delete(self, key, **kwargs):
        return self.client.delete(key, **kwargs)

    def exists(self, key, **kwargs):
        return self.client.exists(key, **kwargs)

    def pop(self, https, **kwargs):
        return self.client.pop(https, **kwargs)

    def getAll(self, https, **kwargs):
        return self.client.getAll(https, **kwargs)

    def clear(self, **kwargs):
        return self.client.clear(**kwargs)

    def changeTable(self, name, **kwargs):
        self.client.changeTable(name, **kwargs)

    def getCount(self, **kwargs):
        return self.client.getCount(**kwargs)

    def test(self, **kwargs):
        return self.client.test(**kwargs)
