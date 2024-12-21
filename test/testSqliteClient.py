# -*- coding: utf-8 -*-
# @Time    : 2024/12/21 23:09 
# @File    : testSqliteClient.py.py
from helper.proxy import Proxy


def testSqliteClient():
    from db.dbClient import DbClient
    db = DbClient("sqlite:///pool.db")
    # Insert a proxy
    proxy = Proxy(
        proxy="192.168.0.1:8080",
        https=True,
        socket4=False,
        socket5=False,
        fail_count=0,
        region="US",
        anonymous="yes",
        source="test_source",
        check_count=1,
        last_status="active",
        last_time="2024-12-21 12:00:00"
    )
    proxy2 = Proxy(
        proxy="192.168.0.2:8080",
        https=False,
        socket4=True,
        socket5=False,
        fail_count=0,
        region="US",
        anonymous="yes",
        source="test_source",
        check_count=1,
        last_status="active",
        last_time="2024-12-21 12:00:00"
    )
    proxy3 = Proxy(
        proxy="192.168.0.3:8080",
        https=False,
        socket4=False,
        socket5=True,
        fail_count=0,
        region="US",
        anonymous="yes",
        source="test_source",
        check_count=1,
        last_status="active",
        last_time="2024-12-21 12:00:00"
    )
    db.changeTable("use_proxy")
    print("put1: ", db.put(proxy).to_json)
    print("put2: ", db.put(proxy2).to_json)
    print("put3: ", db.put(proxy3).to_json)
    print("get: ", db.get(https=None, socket4=True).to_json)
    print("exists: ", db.exists("192.168.0.1:8080"))
    print("exists: ", db.exists("192.168.0.2:8080"))
    print("exists: ", db.exists("192.168.0.3:8080"))
    print("pop: ", db.pop(https=None))
    print("getAll: ", db.getAll(https=None))
    print("getAll: ", db.getAll(https=None, socket5=True))
    print("getCount", db.getCount())
    # Delete a proxy
    db.delete("192.168.0.1:8080")
    db.delete("192.168.0.2:8080")
    db.delete("192.168.0.3:8080")

if __name__ == '__main__':
    testSqliteClient()
