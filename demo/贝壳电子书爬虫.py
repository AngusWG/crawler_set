#!/usr/bin/python3
# encoding: utf-8 
# @Time    : 2018/9/10 20:19 
# @author  : zza
# @Email   : 740713651@qq.com
import os
from urllib.parse import urlencode, quote
from lxml import etree
import requests

path = "F:/txt/{}"
header = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.26 Mobile Safari/537.36",
    "Accept-Encoding": "gzip, deflate",
    "Host": "www.bktxt.com",
    "Proxy-Connection": "Keep-Alive",
    "Pragma": "no-cache",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Referer": "http://www.bktxt.com/1573.html",
    "Cookie": "__51cke__=; __BAIDU_STATE_END__=yes; bookclick=20%7C57844%7C; __tins__19210252=%7B%22sid%22%3A%201540387719482%2C%20%22vd%22%3A%2026%2C%20%22expires%22%3A%201540390122057%7D; __51laig__=26"}


def download(url, title):
    url, param_str = url.split("?")
    param_str = param_str.split("&")
    param_list = dict([i.split("=", 1) for i in param_str])
    param_list = urlencode(param_list, encoding="utf8").replace("+", "%20")
    url = "{}?{}".format(url, param_list)
    rep = requests.get(url, stream=True, headers=header)
    with open(os.path.join(path, title + ".txt"), "wb") as file:
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
    title = selector.xpath('//*[@class="downrar"]//@title')[0].replace("TXT免费下", "").replace(" ", "")
    header['Referer'] = url
    download(url_, title)


def get_url_from_index(page_name):
    error_pag = []
    url = "http://www.bktxt.com/{}/{}.html"
    i = 0
    global path
    path = path.format(page_name)
    if not os.path.isdir(path):
        os.mkdir(path)
    while True:
        i = i + 1
        print("start page {} / {}".format(page_name, i))
        rep = requests.get(url.format(page_name, i), headers=header)
        selector = etree.HTML(rep.text)
        url_list = selector.xpath('//ul[@class="list"]/li/a/@href')
        print("get {} url ".format(len(url_list)))
        if len(url_list) == 0:
            break
        for j in url_list:
            print("start {}".format(j))
            try:
                get_url_by_page(j)
                error_pag.append(j)
            except Exception:
                error_pag.append(j)
                print("get error ", j)
    with open("error.txt", "a", encoding='utf8') as f:
        f.write("\n".join(error_pag))


def main():
    # for page in [1,2,3,4,5]:
    for page in range(1, 13):
        get_url_from_index(page)


if __name__ == '__main__':
    main()
    # get_url_from_index(2)
    # get_url_by_page("http://www.bktxt.com/34777.html")
