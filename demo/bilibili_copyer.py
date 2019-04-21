#!/usr/bin/python3
# encoding: utf-8 
# @Time    : 2018/8/19 15:01 
# @author  : zza
# @Email   : 740713651@qq.com
import os
import re
import time

import requests
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium import webdriver

file_dir = r"D:"
user_id = 19193
key_world = "北京时间"
# 初始化
service_args = ['--ignore-ssl-errors=true', '--ssl-protocol=TLSv1']
dcap = dict(DesiredCapabilities.PHANTOMJS)
dcap["phantomjs.page.settings.userAgent"] = "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, " \
                                            "like Gecko) Chrome/63.0.3239.26 Safari/537.36 Core/1.63.6716.400 " \
                                            "QQBrowser/10.2.2214.40"
dcap["phantomjs.page.settings.loadImages"] = True
browser = webdriver.PhantomJS(r"{}\temp\phantomjs.exe".format(file_dir), service_args=service_args,
                              desired_capabilities=dcap)


def get_pictrue(element_html):
    """获取图片"""
    urls = re.findall(r'style="background-image: url\(([^@]*)', element_html)
    for url in urls:
        body = requests.get(url)
        name = url[url.rfind("/") + 1:]
        file = r'{}\temp\pic\{}'.format(file_dir, str(name))
        if not os.path.exists(file):
            with open(file, 'wb') as f:
                f.write(body.content)
            print("pic save", end=" ")
    print()


print("开始工作")
browser.get('http://space.bilibili.com/{}/dynamic'.format(user_id))
time.sleep(3)
browser.implicitly_wait(15)
js = "var q=document.body.scrollTop=10000"
browser.execute_script(js)
browser.implicitly_wait(15)
elements = browser.find_elements_by_xpath('//*[@id="page-dynamic"]/div[1]/div/div/div/div[1]/div[1]/div[1]/div')

source_code = ""

e_len = len(elements)
print("总共找到{}条记录".format(e_len))
for index, element in enumerate(elements):
    print("[{}/{}]: start".format(index, e_len))
    if key_world not in element.text:
        continue
    code = element.get_attribute('innerHTML')
    if 'class="video-wrap"' in code:  # 视屏
        continue
    if "image: url" in code:
        get_pictrue(code)
    source_code += "\n\n" + code
    print("[{}/{}]: save ".format(index, e_len))

with open(r"{}\temp\src.html".format(file_dir), "w") as f:
    f.write(source_code)

print("程序完成")
input("按任意键退出")
