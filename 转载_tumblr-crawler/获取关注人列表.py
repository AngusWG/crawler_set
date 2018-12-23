#!/usr/bin/python3
# encoding: utf-8 
# @Time    : 2018/12/16 0:50 
# @author  : zza
# @Email   : 740713651@qq.com

import re
import time
from pprint import pprint

proxies = {
    "http": "http://127.0.0.1:9999",
    "https": "https://127.0.0.1:9999"
}
import requests


def get_doc(num):
    headers = {
        'accept-encoding': 'gzip, deflate',
        'accept-language': 'zh-CN,zh;q=0.9',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.26 Safari/537.36 Core/1.63.6788.400 QQBrowser/10.3.2767.400',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'cache-control': 'max-age=0',
        'authority': 'www.tumblr.com',
        'cookie': 'rxx=2p456456465LE8IgzoaKv1Nvaix0; documentWidth=1000',
    }

    response = requests.get('https://www.tumblr.com/following/{}'.format(num), proxies=proxies, headers=headers)
    time.sleep(3)
    print(num)
    return response.text


a = [get_doc(i) for i in list(range(0, 210, 25))]
res = []

with open("rec", "a", encoding="utf") as f:
    f.writelines(res)

for i in a:
    for j in re.findall('href="https?://([^ ]*)\.tumblr\.com', i):
        res.append(j)

res = set(res)
pprint(res)
res = ['{}\n'.format(i) for i in res]
with open("rec", "w", encoding="utf") as f:
    f.writelines(res)
