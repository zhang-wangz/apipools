# -*- coding: utf-8 -*-
import re
import urllib
import urllib.parse
from datetime import datetime
from time import sleep, time

from helper.check import DoValidator
from util.webRequest import WebRequest


def preValidator(p_):
    # 抓取的时候就校验
    if DoValidator.preValidator(proxy=p_):
        print("catch is not ip content, skip")
        return True
    return False

class ProxyFetcher(object):
    """
    proxy getter
    """


    @staticmethod
    def curl(url, test_cnt=3):
        import subprocess
        # 定义 curl 命令, 使用 -s 静默模式，避免输出额外信息
        curl_command = ["curl", "-s", url]
        while True:
            try:
                for encoding in ["utf-8", "gbk"]:
                    try:
                        result = subprocess.run(curl_command, stdout=subprocess.PIPE, text=True, check=True, encoding=encoding)
                        response = result.stdout
                        return response
                    except UnicodeDecodeError as e:
                        # print("编码失败，换一种编码进行访问, {}".format(e))
                        continue
            except subprocess.CalledProcessError as e:
                print(f"执行 curl 命令失败: {e}")
                if test_cnt <= 0: return ""
                if test_cnt > 0:
                    test_cnt -= 1
                    sleep(5)


    @staticmethod
    def freeProxy02():
        """ 快代理 https://www.kuaidaili.com """
        # 'inha', 'intr'已经不再更新
        categories = ['dps', 'fps']
        for category in categories:
            max_page = 1
            page = 1
            while page <= max_page:
                url = f'https://www.kuaidaili.com/free/{category}/{page}'
                sleep(5)
                r = WebRequest().get(url, timeout=10)
                proxies = re.findall(
                    r'\"ip\":\s+\"(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\",\s+\"last_check_time\":\s+\"[\d\-\s\:]+\",\s+\"port\"\:\s+\"(\d+)\"',
                    r.text)
                yield from [':'.join(proxy) for proxy in proxies]
                res = re.findall(r'let\s+totalCount\s\=\s+[\'\"](\d+)[\'\"]', r.text)
                if res and type(res) == list and len(res) > 0:
                    total = res[0]
                    max_page = min(int(total) / 12, 2)
                page += 1


    @staticmethod
    def freeProxy03():
        """ 云代理 """
        # 一天更新一次
        stypes = ('1', '2')
        for stype in stypes:
            url = f'http://www.ip3366.net/free/?stype={stype}'
            r = WebRequest().get(url, timeout=10)
            proxies = re.findall(r'<td>(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})</td>[\s\S]*?<td>(\d+)</td>', r.text)
            for proxy in proxies:
                yield ":".join(proxy)

            pages = re.findall(r'<a\s+href=\"\?stype=[12]&page=(\d+)\">\d+</a>', r.text)
            for page in pages:
                url = f'http://www.ip3366.net/free/?stype={stype}&page={page}'
                sleep(1)
                r = WebRequest().get(url, timeout=10)
                proxies = re.findall(r'<td>(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})</td>[\s\S]*?<td>(\d+)</td>', r.text)
                yield from [':'.join(proxy) for proxy in proxies]

    @staticmethod
    def freeProxy04():
        """ 小幻代理 """
        # 一小时一次
        now = datetime.now()
        url = f'https://ip.ihuan.me/today/{now.year}/{now.month:02}/{now.day:02}/{now.hour:02}.html'
        r = WebRequest().get(url, timeout=10, useRequests=False)
        proxies = re.findall(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):(\d+)', r.text)
        yield from [':'.join(proxy) for proxy in proxies]


    @staticmethod
    def freeProxy05():
        """ 89免费代理 """
        urls = ['https://www.89ip.cn/']
        while True:
            try:
                url = urls.pop()
            except IndexError:
                break

            r = WebRequest().get(url, timeout=10)
            proxies = re.findall(
                r'<td.*?>[\s\S]*?(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})[\s\S]*?</td>[\s\S]*?<td.*?>[\s\S]*?(\d+)[\s\S]*?</td>',
                r.text)
            if not proxies or len(proxies) == 0:
                break

            yield from [':'.join(proxy) for proxy in proxies]

            # 下一页
            r = re.findall(
                r'<a\s+href=\"(index_\d+.html)\"\s+class=\"layui-laypage-next\"\s+data-page=\"\d+\">下一页</a>', r.text)
            if r:
                next_url = urllib.parse.urljoin(url, r[0])
                urls.append(next_url)
                sleep(1)

    @staticmethod
    def freeProxy06():
        """ 稻壳代理 https://www.docip.net/ """
        # 3小时抓1次
        r = WebRequest().get("https://www.docip.net/data/free.json", timeout=10)
        try:
            for each in r.json['data']:
                yield each['ip']
        except Exception as e:
            print(e)


    # @staticmethod
    # def freeProxy07():
    #     # https://github.com/proxifly/free-proxy-list
    #     # 支持socket4， socket5
    #     # socks4, socks5
    #     # 暂时宕机了已经
    #     url = 'https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/protocols/{}/data.json'
    #     urls = [url.format(u) for u in ["https", "http", "socks4", "socks5"]]
    #     for url_ in urls:
    #         r = WebRequest().get(url_, timeout=10)
    #         proxies = [f'{proxy["ip"]}:{proxy["port"]}' for proxy in r.json]
    #         if_ip = preValidator(proxies[0] if proxies and len(proxies) > 0 else "**##**")
    #         yield from proxies if if_ip else []

    @staticmethod
    def freeProxy08():
        # https://github.com/TheSpeedX/PROXY-List
        # 支持 socket4， socket5
        url = 'https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/{}.txt'
        urls = [url.format(u) for u in ["http", "socks4", "socks5"]]
        for url_ in urls:
            r = WebRequest().get(url_, timeout=10)
            proxies = [proxy for proxy in r.text.split('\n') if proxy]
            if_ip = preValidator(proxies[0] if proxies and len(proxies) > 0 else "**##**")
            yield from proxies if if_ip else []

    @staticmethod
    def freeProxy09():
        # 3小时1次
        # https://github.com/sunny9577/proxy-scraper
        # 可以分类socket5和http，https,新的结构需要支持socket5结构
        url = 'https://sunny9577.github.io/proxy-scraper/proxies.json'
        r = WebRequest().get(url, timeout=10)
        proxies = [f'{proxy["ip"]}:{proxy["port"]}' for proxy in r.json]
        yield from proxies

    @staticmethod
    def freeProxy10():
        # 10分钟一次
        # https://github.com/zloi-user/hideip.me
        # 支持socket5，socket4
        url = "https://gh-proxy.com/https://raw.githubusercontent.com/zloi-user/hideip.me/main/{}.txt"
        urls = [url.format(u) for u in ["http", "https", "socks4", "socks5"]]
        for url in urls:
            r = WebRequest().get(url, timeout=10)
            proxies = [':'.join(proxy.split(':')[:2]) for proxy in r.text.split('\n') if proxy]
            if_ip = preValidator(proxies[0] if proxies and len(proxies) > 0 else "**##**")
            yield from proxies if if_ip else []

    @staticmethod
    def freeProxy11():
        # TODO 外站，需要时间，有时候不给予返回
        url = 'https://iproyal.com/free-proxy-list/?page=1&entries=100'
        while True:
            r = WebRequest().get(url, timeout=15)
            proxies = re.findall(
                r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})</div><div class=\"flex items-center astro-lmapxigl\">(\d+)</div>',
                r.text)
            yield from [':'.join(proxy) for proxy in proxies]

            next = r.tree.xpath('//a[text()="Next"]/@href')
            if next:
                url = urllib.parse.urljoin(url, next[0])
                sleep(5)
            else:
                break

    @staticmethod
    def freeProxy12():
        # TODO 一天50次请求...
        urls = ['http://pubproxy.com/api/proxy?limit=5&https=true', 'http://pubproxy.com/api/proxy?limit=5&https=false']
        proxies = set()
        for url in urls:
            for _ in range(10):
                sleep(1)
                r = WebRequest().get(url, timeout=10)
                for proxy in [proxy['ipPort'] for proxy in r.json['data']]:
                    if proxy in proxies:
                        continue
                    yield proxy
                    proxies.add(proxy)

    @staticmethod
    def freeProxy13():
        # TODO 外站，访问有限制
        urls = ['https://freeproxylist.cc/servers/']
        while True:
            try:
                url = urls.pop()
            except IndexError:
                break

            r = WebRequest().get(url, timeout=10)
            proxies = re.findall(r'<td>(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})</td>[\s\S]*?<td>(\d+)</td>', r.text)
            yield from [':'.join(proxy) for proxy in proxies]

            r = re.findall(r'''<a\s+href='(https://freeproxylist\.cc/servers/\d+\.html)'>&raquo;</a></li>''', r.text)
            if r:
                urls.append(r[0])
                sleep(1)

    @staticmethod
    def freeProxy14():
        # TODO 外站问题
        url = 'https://hasdata.com/free-proxy-list'
        r = WebRequest().get(url, timeout=15)
        proxies = re.findall(r'<tr><td>(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})</td><td>(\d+)</td><td>HTTP', r.text)
        yield from [':'.join(proxy) for proxy in proxies]

    @staticmethod
    def freeProxy15():
        urls = ['https://www.freeproxy.world/?type=https&anonymity=&country=&speed=&port=&page=1',
                'https://www.freeproxy.world/?type=http&anonymity=&country=&speed=&port=&page=1']
        for url in urls:
            r = WebRequest().get(url, timeout=10)
            proxies = re.findall(
                r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\s*</td>\s*<td>\s*<a href=\"/\?port=\d+\">(\d+)</a>', r.text)
            yield from [':'.join(proxy) for proxy in proxies]

    @staticmethod
    def freeProxy16():
        # https://github.com/hookzof/socks5_list
        # https://raw.githubusercontent.com/hookzof/socks5_list/master/proxy.txt
        url = "https://raw.githubusercontent.com/hookzof/socks5_list/master/proxy.txt"
        urls = [url]
        for url in urls:
            r = WebRequest().get(url, timeout=10)
            proxies = [':'.join(proxy.split(':')[:2]).replace("\r", "") for proxy in r.text.split('\n') if proxy]
            if_ip = preValidator(proxies[0] if proxies and len(proxies) > 0 else "**##**")
            yield from proxies if if_ip else []

    @staticmethod
    def freeProxy17():
        # https://github.com/monosans/proxy-list
        # 1小时
        url = "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies.json"
        urls = [url]
        for url in urls:
            r = WebRequest().get(url, timeout=10)
            proxies = [f'{proxy["host"]}:{proxy["port"]}' for proxy in r.json if proxy]
            if_ip = preValidator(proxies[0] if proxies and len(proxies) > 0 else "**##**")
            yield from proxies if if_ip else []


    @staticmethod
    def freeProxy18():
        # https://github.com/mmpx12/proxy-list
        # 1小时
        url = "https://raw.githubusercontent.com/mmpx12/proxy-list/master/proxies.txt"
        urls = [url]
        for url in urls:
            r = WebRequest().get(url, timeout=10)
            proxies = []
            for proxy in r.text.split('\n'):
                if 'error code' in proxy:
                    continue
                try:
                    proxy = proxy.split('//')[1]
                    proxies.append(proxy.replace("\r", ""))
                except Exception:
                    continue
            yield from proxies


    @staticmethod
    def freeProxy19():
        # https://github.com/MuRongPIG/Proxy-Master
        # 1小时
        url = "https://raw.githubusercontent.com/MuRongPIG/Proxy-Master/main/{}.txt"
        urls = [url.format(ty) for ty in ['socks4_checked', 'socks5_checked', 'http_checked']]
        for url in urls:
            r = WebRequest().get(url, timeout=10)
            proxies = [":".join(proxy.split(':')[:2]) for proxy in r.text.split('\n') if proxy]
            if_ip = preValidator(proxies[0] if proxies and len(proxies) > 0 else "**##**")
            yield from proxies if if_ip else []

    @staticmethod
    def freeProxy20():
        # https://github.com/ALIILAPRO/Proxy
        # https://gh-proxy.com/
        # 1小时
        url = "https://raw.githubusercontent.com/ALIILAPRO/Proxy/main/{}.txt"
        urls = [url.format(ty) for ty in ['http', 'socks4', 'socks5']]
        for url in urls:
            r = WebRequest().get(url, timeout=10)
            proxies = [":".join(proxy.split(':')[:2]).replace('\r', '') for proxy in r.text.split('\n') if proxy]
            if_ip = preValidator(proxies[0] if proxies and len(proxies)>0 else "**##**")
            yield from proxies if if_ip else []


    @staticmethod
    def freeProxy21():
        # https://github.com/Zaeem20/FREE_PROXIES_LIST
        # https://gh-proxy.com/
        # 10min
        url = "https://raw.githubusercontent.com/Zaeem20/FREE_PROXIES_LIST/master/{}.txt"
        urls = [url.format(ty) for ty in ['socks5', 'socks4', 'http', 'https']]
        for url in urls:
            r = WebRequest().get(url, timeout=10)
            proxies = [":".join(proxy.split(':')[:2]).replace('\r', '') for proxy in r.text.split('\n') if proxy]
            if_ip = preValidator(proxies[0] if proxies and len(proxies) > 0 else "**##**")
            yield from proxies if if_ip else []

    @staticmethod
    def freeProxy22():
        # https://github.com/roosterkid/openproxylist
        # 1小时
        url = "https://raw.githubusercontent.com/roosterkid/openproxylist/main/{}.txt"
        #  'HTTPS'
        urls = [url.format(ty) for ty in ['SOCKS5', 'SOCKS4', 'HTTPS']]
        for url in urls:
            r = WebRequest().get(url, timeout=10)
            proxies = re.findall(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):[\s\S]*?(\d+)', r.text)
            proxies = [':'.join(proxy) for proxy in proxies]
            if_ip = preValidator(proxies[0] if proxies and len(proxies) > 0 else "**##**")
            yield from proxies if if_ip else []
    
#

if __name__ == '__main__':
    p = ProxyFetcher()
    for u in [p.freeProxy03()]:
        print(u)
        for ip in u:
            print("ip:{}, socket4:{}, socket5:{}".format( ip, "", ""))

