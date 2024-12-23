# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   Change Activity:
                   2019/08/05: proxyScheduler
                   2021/02/23: runProxyCheck时,剩余代理少于POOL_SIZE_MIN时执行抓取
-------------------------------------------------
"""

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.executors.pool import ProcessPoolExecutor

from util.six import Queue
from helper.fetch import Fetcher
from helper.check import Checker
from handler.logHandler import LogHandler
from handler.proxyHandler import ProxyHandler
from handler.configHandler import ConfigHandler


def __runProxyFetch():
    proxy_queue = Queue()
    proxy_fetcher = Fetcher()

    for proxy in proxy_fetcher.run():
        proxy_queue.put(proxy)

    Checker("raw", proxy_queue)


def __runProxyCheck():
    proxy_handler = ProxyHandler()
    proxy_queue = Queue()
    if proxy_handler.db.getCount() < proxy_handler.conf.poolSizeMin:
        __runProxyFetch()
    for proxy in proxy_handler.getAll():
        proxy_queue.put(proxy)
    Checker("use", proxy_queue)


def runScheduler():
    __runProxyCheck()
    __runProxyFetch()

    timezone = ConfigHandler().timezone
    scheduler_log = LogHandler("scheduler")
    scheduler = BlockingScheduler(logger=scheduler_log, timezone=timezone)

    # 为不同的任务分配不同的执行器
    executors = {
        'fetch_executor': {'type': 'threadpool', 'max_workers': 20},  # 为 __runProxyFetch 配置更多线程
        'check_executor': {'type': 'processpool', 'max_workers': 20},  # 为 __runProxyCheck 配置进程池（适合 CPU 密集型任务）
        'processpool': ProcessPoolExecutor(max_workers=5)
    }

    # 配置任务的默认参数
    job_defaults = {
        'coalesce': False,
        'max_instances': 15
    }
    # 配置调度器
    scheduler.configure(executors=executors, job_defaults=job_defaults, timezone=timezone)

    # 为每个任务指定不同的执行器，确保互不干扰
    scheduler.add_job(__runProxyFetch, 'interval', minutes=5, id="proxy_fetch", name="proxy采集",
                      executor='fetch_executor')
    scheduler.add_job(__runProxyCheck, 'interval', minutes=2, id="proxy_check", name="proxy检查",
                      executor='check_executor')
    # 启动调度器
    scheduler.start()



if __name__ == '__main__':
    runScheduler()
