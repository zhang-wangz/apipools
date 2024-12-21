from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine, Row
from sqlalchemy.pool import QueuePool
from typing import Dict, Optional, List
from helper.proxy import Proxy
from handler.logHandler import LogHandler

class SqliteClient:
    def __init__(self, db_url: str, **kwargs):
        self.engine: Engine = create_engine(
            db_url,
            poolclass=QueuePool,  # 指定使用 QueuePool 连接池
            pool_size=45,  # 最大连接数
            max_overflow=5,  # 额外允许创建的连接数
            pool_timeout=30,  # 等待连接超时时间（秒）
            pool_recycle=3600,  # 回收时间，防止连接断开
            echo=False
        )
        self._initialize_table()

    def _initialize_table(self):
        with self.engine.connect() as conn:
            conn.execute(text('''
                CREATE TABLE IF NOT EXISTS proxies (
                    proxy TEXT PRIMARY KEY,
                    https BOOLEAN,
                    socket4 BOOLEAN,
                    socket5 BOOLEAN,
                    fail_count INTEGER,
                    region TEXT,
                    anonymous TEXT,
                    source TEXT,
                    check_count INTEGER,
                    last_status TEXT,
                    last_time TEXT
                )
            '''))
            conn.commit()

    def get_https(self):
        with self.engine.connect() as conn:
            query = "SELECT * FROM proxies WHERE https = true ORDER BY RANDOM() LIMIT 1"
            result = conn.execute(text(query)).fetchone()
            return Proxy.createFromJson(dict(result._mapping)) if result else None

    def get_sockets4(self):
        with self.engine.connect() as conn:
            query = "SELECT * FROM proxies WHERE socket4 = true ORDER BY RANDOM() LIMIT 1"
            result = conn.execute(text(query)).fetchone()
            return Proxy.createFromJson(dict(result._mapping)) if result else None

    def get_sockets5(self):
        with self.engine.connect() as conn:
            query = "SELECT * FROM proxies WHERE socket5 = true ORDER BY RANDOM() LIMIT 1"
            result = conn.execute(text(query)).fetchone()
            return Proxy.createFromJson(dict(result._mapping)) if result else None

    def get(self, https=False, socket4=False, socket5=False) -> Optional[Proxy]:
        """
        返回一个代理, 如果有指定，则返回对应的，否则随机返回一个
        :return:
        """
        if https:
            return self.get_https()
        if socket4:
            return self.get_sockets4()
        if socket5:
            return self.get_sockets5()
        with self.engine.connect() as conn:
            query = "SELECT * FROM proxies ORDER BY RANDOM() LIMIT 1"
            result = conn.execute(text(query), {"https": https}).fetchone()
            return dict(result._mapping) if result else None

    def put(self, proxy_obj):
        """
        将代理放入
        :param proxy_obj: Proxy obj
        :return:
        """
        with self.engine.connect() as conn:
            conn.execute(text('''
                       INSERT OR REPLACE INTO proxies (proxy, https, socket4, socket5, fail_count, region, anonymous, source, check_count, last_status, last_time)
                       VALUES (:proxy, :https, :socket4, :socket5, :fail_count, :region, :anonymous, :source, :check_count, :last_status, :last_time)
                   '''), proxy_obj.to_dict)
            conn.commit()
        return proxy_obj.to_dict

    def update(self, proxy_obj):
        """
        更新 proxy 属性
        :param proxy_obj:
        :return:
        """
        put(self, proxy_obj)

    def delete(self, proxy_str):
        """
        移除指定代理
        :param proxy_str: proxy str
        :return:
        """
        with self.engine.connect() as conn:
            conn.execute(text("DELETE FROM proxies WHERE proxy = :proxy"), {"proxy": proxy_str})
            conn.commit()

    def exists(self, proxy_str):
        """
        判断指定代理是否存在
        :param proxy_str: proxy str
        :return:
        """
        with self.engine.connect() as conn:
            result = conn.execute(text("SELECT 1 FROM proxies WHERE proxy = :proxy LIMIT 1"),
                                  {"proxy": proxy_str}).fetchone()
            return result is not None


    def pop(self, https, socket4=False, socket5=False):
        """
        弹出一个代理
        :return: dict {proxy: value}
        """
        proxy = self.get(https, socket4, socket5)
        self.delete(proxy.proxy)
        return proxy.to_dict


    def getAll(self, https=False, socket4=False, socket5=False) -> List[Dict]:
        """
        字典形式返回所有代理
        :return:
        """
        if https:
            query = "SELECT * FROM proxies WHERE https = true"
        elif socket4:
            query = "SELECT * FROM proxies WHERE socket4 = true"
        elif socket5:
            query = "SELECT * FROM proxies WHERE socket5 = true"
        else:
            query =  "SELECT * FROM proxies"
        with self.engine.connect() as conn:
            results = conn.execute(text(query)).fetchall()
            return [dict(row._mapping) for row in results]

    def clear(self):
        """
        清空所有代理
        :return:
        """
        with self.engine.connect() as conn:
            conn.execute(text("DELETE FROM proxies"))
            conn.commit()

    def changeTable(self, name):
        # sqlite不需要该实现，不需要转换table
        pass


    def getCount(self):
        """
        返回代理数量
        :return:
        """
        with self.engine.connect() as conn:
            query = "SELECT COUNT(*) FROM proxies"
            result = conn.execute(text(query)).fetchone()
            return result[0] if result else 0

    def test(self):
        log = LogHandler('sqlite_client')
        try:
            self.getCount()
        except TimeoutError as e:
            log.error('sqlite connection time out: %s' % str(e), exc_info=True)
            return e
        except ConnectionError as e:
            log.error('sqlite connection error: %s' % str(e), exc_info=True)
            return e
        except Exception as e:
            log.error('sqlite connection error: %s' % str(e), exc_info=True)
            return e


