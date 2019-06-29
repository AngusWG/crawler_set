#!/usr/bin/python3
# encoding: utf-8
# @Time    : 2019/6/29 22:11
# @author  : zza
# @Email   : 740713651@qq.com
# @Form https://github.com/MrJStyle/Python-Crawler

import os
import re
import requests
from lxml import etree

home_url = "http://wallpaperswide.com"
header = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Safari/537.36'
}
# 需要填写的参数！！！
definition = "1920x1080"  # 填写分辨率 例如 2560x2560
save_dir = r"C:\Users\74071\Pictures\wallpaper"  # 请避免中文
start_page = 0  # 起始页码
end_page = 50  # 结束页码


def downloads(res="/blue_ocean_aesthetic_background-wallpapers.html"):
    print("start :{}".format(res))
    try:
        req1 = requests.get("{}{}".format(home_url, res), headers=header)
        photo_url = etree.HTML(req1.text).xpath('//div/a[contains(text(),"{}")]/@href'.format(definition))[0]
        rep = requests.get(home_url + photo_url, stream=True, headers=header)
        file_name = re.findall("filename=(.+)", rep.headers['content-disposition'])[0]
        file_path = os.path.join(save_dir, file_name)
    except IndexError as err:
        print("err   :{}\n{}\n".format(res, err))
        return
    if os.path.exists(file_path):
        return True
    with open(file_path, "wb") as file:
        for chunk in rep.iter_content(chunk_size=1024 * 10):
            if chunk:
                file.write(chunk)
    print("end   :{}".format(res))


def service():
    for page in range(start_page, end_page):
        print("\n{}\npage = {}".format("*" * 20, page))
        req1 = requests.get("{}/page/{}".format(home_url, page), headers=header)
        res_list = etree.HTML(req1.text).xpath('//div[@class="thumb"]/div[1]/a/@href')
        [downloads(res) for res in res_list]


if __name__ == '__main__':
    service()
