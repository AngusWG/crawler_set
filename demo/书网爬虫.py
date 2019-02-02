#!/usr/bin/python3
# encoding: utf-8 
# @Time    : 2019/2/2 10:20
# @Author  : zza
# @Email   : 740713651@qq.com
from lxml import etree
import requests
import re

headers = {
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.26 Safari/537.36 Core/1.63.6788.400 QQBrowser/10.3.2767.400',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Referer': None,
    'Connection': 'keep-alive',
}


def one_page(book_url, page_num=1):
    if page_num is not 1:
        book_url = book_url.replace(".html", "_{}.html".format(page_num))
    headers['Referer'] = book_url
    rep = requests.get(book_url, headers=headers)

    rep.encoding = "GBK"
    selector = etree.HTML(rep.text)
    text = selector.xpath('//*[@class="artz"]//text()')

    res = ""
    for i in text:
        if i.startswith('\r\n'):
            res += i.strip() + "\n" if len(i.strip()) is not 0 else ""
    return res


def one_book(name, url):
    # page num
    rep = requests.get(url, headers=headers)
    rep.encoding = "GBK"
    page = int(re.findall(r"共(\d*)页", rep.text)[-1])

    res = ""
    for i in range(1, page + 1):
        res += one_page(url, i)
        print("{} page {} ok".format(name, i))
    with open("{}.txt".format(name), "w", encoding="utf8") as f:
        f.write(res)
    print("{} download success".format(name))


if __name__ == '__main__':
    # http://www.blfushu.com/
    name = ''
    url = ''
    one_book(name, url)
