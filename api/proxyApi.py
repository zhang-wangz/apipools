# -*- coding: utf-8 -*-
# !/usr/bin/env python

from werkzeug.wrappers import Response
from flask import Flask, jsonify, request
from helper.proxy import Proxy
from handler.proxyHandler import ProxyHandler
from handler.configHandler import ConfigHandler

app = Flask(__name__)
conf = ConfigHandler()
proxy_handler = ProxyHandler()


class JsonResponse(Response):
    @classmethod
    def force_type(cls, response, environ=None):
        if isinstance(response, (dict, list)):
            response = jsonify(response)

        return super(JsonResponse, cls).force_type(response, environ)


app.response_class = JsonResponse

api_list = [
    {"url": "/get", "params": "type: ''https'|''", "desc": "get a proxy"},
    {"url": "/pop", "params": "", "desc": "get and delete a proxy"},
    {"url": "/delete", "params": "proxy: 'e.g. 127.0.0.1:8080'", "desc": "delete an unable proxy"},
    {"url": "/all", "params": "type: ''https'|''", "desc": "get all proxy from proxy pool"},
    {"url": "/count", "params": "", "desc": "return proxy count"}
]


@app.route('/')
def index():
    return {'url': api_list}


@app.route('/get/')
def get():
    https = request.args.get("type", "").lower() == 'https'
    socket4 = request.args.get("type", "").lower() == 'socket4'
    socket5 = request.args.get("type", "").lower() == 'socket5'
    proxy = proxy_handler.get(https=https, socket4=socket4, socket5=socket5)
    return proxy.to_dict if proxy else {"code": 0, "src": "no proxy"}


@app.route('/getLatest/')
def getLatest():
    limit = request.args.get("limit", 1)
    offset = request.args.get("offset", 0)
    https = request.args.get("type", "").lower() == 'https'
    socket4 = request.args.get("type", "").lower() == 'socket4'
    socket5 = request.args.get("type", "").lower() == 'socket5'
    proxies = proxy_handler.getLatest(limit=limit, offset=offset, https=https, socket4=socket4, socket5=socket5)
    return jsonify([_.to_dict for _ in proxies]) if len(proxies)> 0 \
        else {"code": 0, "src": "no proxy"}


@app.route('/pop/')
def pop():
    https = request.args.get("type", "").lower() == 'https'
    socket4 = request.args.get("type", "").lower() == 'socket4'
    socket5 = request.args.get("type", "").lower() == 'socket5'
    proxy = proxy_handler.pop(https=https, socket4=socket4, socket5=socket5)
    return proxy.to_dict if proxy else {"code": 0, "src": "no proxy"}


@app.route('/all/')
def getAll():
    https = request.args.get("type", "").lower() == 'https'
    socket4 = request.args.get("type", "").lower() == 'socket4'
    socket5 = request.args.get("type", "").lower() == 'socket5'
    proxies = proxy_handler.getAll(https=https, socket4=socket4, socket5=socket5)
    return jsonify([_.to_dict for _ in proxies])


@app.route('/delete/', methods=['GET'])
def delete():
    proxy = request.args.get('proxy')
    status = proxy_handler.delete(Proxy(proxy))
    return {"code": 0, "src": status}


@app.route('/count/')
def getCount():
    proxies = proxy_handler.getAll(socket4=False, socket5=False)
    type_dict = {}
    source_dict = {}
    for proxy in proxies:
        if proxy.https:
            http_type = 'https'
        elif proxy.socket4:
            http_type = 'socket4'
        elif proxy.socket5:
            http_type = 'socket5'
        else:
            http_type = 'http'
        type_dict[http_type] = type_dict.get(http_type, 0) + 1
        for source in proxy.source.split('/'):
            source_dict[source] = source_dict.get(source, 0) + 1
    return {"type_dict": type_dict, "source": source_dict, "count": len(proxies)}


def runFlask():
    app.run(host=conf.serverHost, port=conf.serverPort)


if __name__ == '__main__':
    runFlask()
