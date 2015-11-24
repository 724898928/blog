#!/usr/bin/env python
# -*- coding: utf-8 -*-
##必须加上面一行，否则中文注释报错

import socket
import threading
import time 
import os
import sys
import json
import urllib
import urlparse


def getDefault():
    return json.dumps({'name':'test'})
def getUser():

    return json.dumps({'name':'bill'})
url_mapping = {
    '/' : getDefault,
    '/user/get' : getUser
}
cur_path = sys.path[0]
if os.path.isfile(cur_path):
    cur_path = os.path.dirname(cur_path)
root = cur_path + '/root'
resHeaders = {
    'Proxy-Connection': 'Keep-Alive', 
    'Connection': 'Keep-Alive',
    'Keep-Alive': 'max=5, timeout=120',
    'Via': '1.1 JA-ISA02',
    'Date': 'Fri, 18 May 2022 09:05:56 GMT', 
    'Server': 'nginx version 2.6',
    'Cache-Control': 'max-age=3600',
    'Last-Modified': 'Fri, 18 May 2015 09:05:56 GMT', 
    'ETag': 'v2.6',
    'Set-Cookie': 'name=bill'
}
resHeaders_arr = []
server = {}
server['protocol'] = 'HTTP/1.1'
evn = {}

def parse_request_uri(uri):
    '解析URI'
    if uri == '*':
        return None, None, uri
    i = uri.find('://')
    if i> 0 and '?' not in uri[:i]:
        scheme, remainder = uri[:i].lower(), uri[i+3]
        authority, path = remainder.split('/',1)
        return scheme, authority, path
    if uri.startswith('/'):
        return None, None, uri
    else:
        return None, uri, None

def handle(s):
    '处理一个请求在一个线程里.'
    reqData = s.recv(4096)
    reqHeaders = reqData.split('\r\n')

    evn['method'], evn['uri'], evn['req_protocol'] = reqHeaders[0].strip().split(' ',2)
    rp = int(evn['req_protocol'][5]), int(evn['req_protocol'][7])
    sp = int(server['protocol'][5]), int(server['protocol'][7])
    evn['response_protocol'] = 'HTTP/%s.%s' % min(rp, sp)
    for hd in reqHeaders[1:]:
        if hd in ' \t':
            v = hd.strip()
        else:
            try:
                k, v = hd.split(':',1)
            except Exception as e:
                print e
            k = k.strip().title()
            v = v.strip()
            evn[k] = v

    evn['scheme'], evn['authority'], evn['path'] = parse_request_uri(evn['uri'])
    if '?' in evn['path']:
        evn['path'], evn['querystring'] = evn['path'].split('?', 1)

    #从请求头或body里拿参数数据
    if evn['method'] == 'POST':
        params = urlparse.parse_qs(reqHeaders[-1])
    elif evn.has_key('querystring'):
        params = urlparse.parse_qs(evn['querystring'])
    else:
        params = {}
    evn['request'] = process_params(params,evn['method'])

    

    ##解析路径及调用路由
    req_file = root + evn['path'] 
    if evn['path'].startswith('/static',0) and os.path.isfile(req_file):
        fd = open(req_file,'r')
        res = fd.read()
        fd.close()
        resHeaders['Content-Type'] = 'text/plain'
        resHeaders['Content-Length'] = str(len(res))
        resHeaders_arr = []
        resHeaders_arr.insert(0,'HTTP/1.1 200 OK');
        
    elif evn['path'] in url_mapping:
        res = {'name':'bill','age':30}
        res = json.dumps(res)
        print evn['path']
        res =url_mapping[evn['path']]()
        resHeaders['Content-Type'] = 'text/json'
        resHeaders['Content-Length'] = str(len(res))
        resHeaders_arr = []
        resHeaders_arr.insert(0,'HTTP/1.1 200 OK');
    else:
        res = ''
        resHeaders['Content-Type'] = 'text/html'
        resHeaders['Content-Length'] = str(len(res))
        resHeaders_arr = []
        resHeaders_arr.insert(0,'HTTP/1.1 404 NOT FOUND');

    process_resHeader()
    rh = '\r\n'.join(resHeaders_arr)
    s.send(rh.strip() + '\r\n\r\n')
    s.send(res)
    s.close()

def process_resHeader():
    '处理响应头信息'
    for k,v in resHeaders.iteritems():
        resHeaders_arr.append(k + ':' +v)

def process_params(params, type):
    '处理请求数据'
    data = {}
    data[type] = {}
    for k in params.keys():
        if len(params[k]) > 1:
            data[type][k] = params[k]
        else:
            data[type][k] = params[k][0]

    return data

try:
    HOST='0.0.0.0'
    PORT=8503
    if len(sys.argv) == 3:
        HOST = sys.argv[1]
        PORT = int(sys.argv[2])
    else:
        len(sys.argv) == 2
        HOST = sys.argv[1]
    BUFFSIZE = 1024*4
    ADDR = (HOST,PORT)

    ##初始化soket
    ss=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ss.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
    ss.bind(ADDR)
    ss.listen(5)


    ##处理请求
    while True:
        print 'waiting for connection...'
        cs, addr = ss.accept()
        print '...connected from:',addr
        evn['remote_addr'] = addr[0]
        evn['remote_port'] = addr[1]
        evn['server_name'] = socket.gethostname()
        evn['server_addr'] = socket.gethostbyname(socket.gethostname())
        evn['server_port'] = ADDR[1]
        evn['software'] = 'webserver 1.0'

        thread = threading.Thread(target = handle, args = (cs,))
        thread.start()

    ss.close()

except Exception ,e:
    print 'catch exception : ',e
