# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   Change Activity:
                   2021/11/18: 多线程采集
-------------------------------------------------
"""

from threading import Thread
from helper.proxy import Proxy
from helper.check import DoValidator
from handler.logHandler import LogHandler
from handler.proxyHandler import ProxyHandler
from fetcher.proxyFetcher import ProxyFetcher
from handler.configHandler import ConfigHandler
from util.fetch import can_fetch, save_json_data


class _ThreadFetcher(Thread):

    def __init__(self, fetch_source, proxy_dict):
        Thread.__init__(self)
        self.fetch_source = fetch_source
        self.proxy_dict = proxy_dict
        self.fetcher = getattr(ProxyFetcher, fetch_source, None)
        self.log = LogHandler("fetcher")
        self.conf = ConfigHandler()
        self.proxy_handler = ProxyHandler()

    def run(self):
        self.log.info("ProxyFetch - {func}: start".format(func=self.fetch_source))
        try:
            for proxy in self.fetcher():
                self.log.info('ProxyFetch - %s: %s ok' % (self.fetch_source, proxy.ljust(23)))
                proxy = proxy.strip()
                if proxy in self.proxy_dict:
                    self.proxy_dict[proxy].add_source(self.fetch_source)
                else:
                    self.proxy_dict[proxy] = Proxy(
                        proxy, source=self.fetch_source)
        except Exception as e:
            self.log.error("ProxyFetch - {func}: error".format(func=self.fetch_source))
            self.log.error(str(e))


class Fetcher(object):
    name = "fetcher"

    def __init__(self):
        self.log = LogHandler(self.name)
        self.conf = ConfigHandler()

    def run(self):
        """
        fetch proxy with proxyFetcher
        :return:
        """
        proxy_dict = dict()
        thread_list = list()
        self.log.info("ProxyFetch : start")
        d_ = []
        for idx, fetch_source in enumerate(self.conf.fetchers):
            func_name = fetch_source.get("name", "fetch_{}".format(idx))
            can_, func_ = can_fetch(fetch_source)
            d_.append(func_)
            if not can_:
                self.log.error("ProxyFetch - {func}: not cd，please wait".format(func=fetch_source))
                continue
            self.log.info("ProxyFetch - {func}: start".format(func=func_name))
            fetcher = getattr(ProxyFetcher, func_name, None)
            if not fetcher:
                self.log.error("ProxyFetch - {func}: class method not exists!".format(func=fetch_source))
                continue
            if not callable(fetcher):
                self.log.error("ProxyFetch - {func}: must be class method".format(func=fetch_source))
                continue
            thread_list.append(_ThreadFetcher(func_name, proxy_dict))
        save_json_data(d_, self.conf.fetchersPath)
        for thread in thread_list:
            thread.setDaemon(True)
            thread.start()

        for thread in thread_list:
            thread.join()

        self.log.info("ProxyFetch - all complete!")
        for _ in proxy_dict.values():
            if DoValidator.preValidator(_.proxy):
                yield _
