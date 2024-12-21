# -*- coding: utf-8 -*-

from helper.proxy import Proxy
from db.dbClient import DbClient
from handler.configHandler import ConfigHandler


class ProxyHandler(object):
    """ Proxy CRUD operator"""

    def __init__(self):
        self.conf = ConfigHandler()
        self.db = DbClient(self.conf.dbConn)
        self.db.changeTable(self.conf.tableName)

    def get(self, https=False, **kwargs):
        """
        return a proxy
        Args:
            https: True/False
        Returns:
        """
        proxy = self.db.get(https, **kwargs)
        return Proxy.createFromJson(proxy) if proxy else None

    def pop(self, https, **kwargs):
        """
        return and delete a useful proxy
        :return:
        """
        proxy = self.db.pop(https, **kwargs)
        if proxy:
            return Proxy.createFromJson(proxy)
        return None

    def put(self, proxy, **kwargs):
        """
        put proxy into use proxy
        :return:
        """
        self.db.put(proxy, **kwargs)

    def delete(self, proxy, **kwargs):
        """
        delete useful proxy
        :param proxy:
        :return:
        """
        return self.db.delete(proxy.proxy, **kwargs)

    def getAll(self, https=False, **kwargs):
        """
        get all proxy from pool as Proxy list
        :return:
        """
        proxies = self.db.getAll(https, **kwargs)
        return [Proxy.createFromJson(_) for _ in proxies]

    def exists(self, proxy, **kwargs):
        """
        check proxy exists
        :param proxy:
        :return:
        """
        return self.db.exists(proxy.proxy, **kwargs)

    def getCount(self, **kwargs):
        """
        return raw_proxy and use_proxy count
        :return:
        """
        total_use_proxy = self.db.getCount(**kwargs)
        return {'count': total_use_proxy}
