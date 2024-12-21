# -*- coding: utf-8 -*-
# @Time    : 2024/12/21 15:58 
# @File    : fetch.py
import json
import datetime
from datetime import timedelta


def can_fetch(json_data):
    from datetime import datetime
    nw = datetime.now()
    day = json_data.get('day', 0)
    hour = json_data.get('hour', 0)
    minute = json_data.get('minute', 0)
    second = json_data.get('second', 0)
    last = json_data.get('lastTime', 0) # 时间戳
    if day == 0 and hour == 0 and minute == 0 and second == 0:
        return True, json_data
    if last == 0:
        json_data['lastTime'] = nw.timestamp()
        return True, json_data
    last_time = datetime.fromtimestamp(last)
    _time = last_time + timedelta(days=day, hours=hour, minutes=minute, seconds=second)
    if _time > nw:
        return False, json_data
    else:
        json_data['lastTime'] = nw.timestamp()
        return True, json_data

def save_json_data(json_data, file_path):
    with open(file_path, 'w', encoding='utf-8') as fetch_file:
        fetch_file.write(json.dumps(json_data, indent=4))

if __name__ == '__main__':
    # with open('./proxy_fetcher.json', encoding='utf-8') as f:
    #     data = json.load(f)
    #     d = []
    #     for _, i in enumerate(data):
    #         a, b = can_fetch(i)
    #         print(a, b)
    #         d.append(b)
    #     save_json_data(d, "./proxy_fetcher.json")
    pass





