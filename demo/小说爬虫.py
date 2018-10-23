#!/usr/bin/python3
# encoding: utf-8 
# @Time    : 2018/9/10 20:19 
# @author  : zza
# @Email   : 740713651@qq.com
import os
from urllib.parse import urlencode, quote
from lxml import etree
import requests

path = "F:/txt/11"
header = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.26 Mobile Safari/537.36"
    , "Accept-Encoding": "gzip, deflate",
    "Host": "www.bktxt.com",
    "Proxy-Connection": "Keep-Alive",
    "Pragma": "no-cache",
    "Accept": "*/*",
    "Referer": "http://www.bktxt.com/1573.html",
    "Cookie": "__51cke__=; __lfcc=1; bookclick=9710%7C33343%7C6%7C1573%7C58498%7C; __tins__19210252=%7B%22sid%22%3A%201536586464190%2C%20%22vd%22%3A%2010%2C%20%22expires%22%3A%201536589214042%7D; __51laig__=22"}


def download(url):
    url, param_str = url.split("?")
    param_str = param_str.split("&")
    param_list = dict([i.split("=") for i in param_str])
    file_name = param_list['name'] + ".txt"
    # param_list['name'] = param_list['name'].encode("gb2312")
    param_list = urlencode(param_list, encoding="gb2312").replace("+", "%20")
    url = "{}?{}".format(url, param_list)
    rep = requests.get(url, stream=True, headers=header)
    with open(os.path.join(path, file_name), "wb") as file:
        for chunk in rep.iter_content(chunk_size=512):
            if chunk:
                file.write(chunk)
    return True


def get_url_by_page(url):
    # url = "http://www.bktxt.com/57845.html"
    global header
    header['Referer'] = "http://www.bktxt.com/11/1.html"
    rep = requests.get(url, headers=header)
    selector = etree.HTML(rep.text)
    url_ = selector.xpath('//*[@class="downrar"]//@href')[0]
    header['Referer'] = url
    download(url_)


def get_url_from_index():
    error_pag = []
    url = "http://www.bktxt.com/11/{}.html"
    for i in range(87, 0, -1):
        print("start page {}".format(i))
        rep = requests.get(url.format(i), headers=header)
        selector = etree.HTML(rep.text)
        url_list = selector.xpath('//ul[@class="list"]/li/a/@href')
        print("get {} url ".format(len(url_list)))
        for j in url_list:
            print("start {}".format(j))
            try:
                get_url_by_page(j)
                error_pag.append(j)
            except Exception:
                error_pag.append(j)
                print("get error ", j)
    with open("error.txt", "w", encoding='utf8') as f:
        f.write("\n".join(error_pag))


if __name__ == '__main__':
    get_url_from_index()
