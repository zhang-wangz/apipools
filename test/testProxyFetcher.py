# -*- coding: utf-8 -*-
import subprocess

from fetcher.proxyFetcher import ProxyFetcher
from handler.configHandler import ConfigHandler


def testProxyFetcher():
    conf = ConfigHandler()
    proxy_getter_functions = conf.fetchers
    proxy_counter = {_["name"]: 0 for _ in proxy_getter_functions}
    for proxyGetter in proxy_getter_functions:
        proxyGetter = proxyGetter["name"]
        count = 10
        for proxy in getattr(ProxyFetcher, proxyGetter.strip())():
            if proxy:
                if count == 0:
                    break
                print('{func}: fetch proxy {proxy}'.format(func=proxyGetter, proxy=proxy))
                proxy_counter[proxyGetter] = proxy_counter.get(proxyGetter) + 1
                count -= 1
    for key, value in proxy_counter.items():
        print(key, value)


if __name__ == '__main__':
    testProxyFetcher()
