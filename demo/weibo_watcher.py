#!/usr/bin/python3
# encoding: utf-8 
# @Time    : 2018/8/19 15:01 
# @author  : zza
# @Email   : 740713651@qq.com
import json
import os
import smtplib
import logging
import socket
import time
from logging.handlers import RotatingFileHandler
from email.header import Header
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import redis
import requests
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium import webdriver

logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logger = logging.getLogger('')
###
service_args = [
    '--ignore-ssl-errors=true',
    # '--proxy=119.41.168.186:53281', '--proxy-type=https',
    '--ssl-protocol=TLSv1'
]
dcap = dict(DesiredCapabilities.PHANTOMJS)
dcap["phantomjs.page.settings.userAgent"] = "Mozilla/5.0 (Windows NT 10.0; WOW64) " \
                                            "AppleWebKit/537.36 (KHTML, like Gecko) " \
                                            "Chrome/63.0.3239.26 Safari/537.36 Core/" \
                                            "1.63.6716.400 QQBrowser/10.2.2214.40"
dcap["phantomjs.page.settings.loadImages"] = True
browser = webdriver.PhantomJS("./phantomjs", service_args=service_args, desired_capabilities=dcap)

host_ip = socket.gethostbyname(socket.gethostname())
r = redis.Redis(host='ali.4yewu.cn', port=6379)


def send_email():
    from_addr = "1169254037@qq.com"
    password = "vkyvmovizdsiigja"
    receivers = ['740713651@qq.com']  # 接收邮件，可设置为你的QQ邮箱或者其他邮箱

    # 创建一个带附件的实例
    message = MIMEMultipart()
    message['From'] = Header("百度云", 'utf-8')
    message['To'] = Header("你", 'utf-8')
    subject = '微博更新通知'
    message['Subject'] = Header(subject, 'utf-8')

    msgAlternative = MIMEMultipart('alternative')
    message.attach(msgAlternative)

    files2 = []
    files = os.listdir(".")
    for i in files:
        if i.endswith(".png"):
            files2.append(i)

    if len(files2) == 0:
        print("没有更新")
        return
    for i in files2:
        # 指定图片为当前目录
        fp = open(i, 'rb')
        msgImage = MIMEImage(fp.read())
        fp.close()

        # 定义图片 ID，在 HTML 文本中引用
        mail_msg = """<p><img src="cid:{}"></p>""".format(i[:-4])
        msgAlternative.attach(MIMEText(mail_msg, 'html', 'utf-8'))
        msgImage.add_header('Content-ID', '<{}>'.format(i[:-4]))
        message.attach(msgImage)
        os.remove(i)
    ##############
    smtp_server = "smtp.qq.com"

    try:
        smtpObj = smtplib.SMTP_SSL(smtp_server, 465)  # SMTP协议默认端口是25
        smtpObj.login(from_addr, password)
        smtpObj.sendmail(from_addr, receivers, message.as_string())
        print("邮件发送成功")
    except smtplib.SMTPException:
        print("Error: 无法发送邮件")
    return


def get_proxy():
    return requests.get("http://ali.4yewu.cn:8080/get/").content


def delete_proxy(proxy):
    requests.get("http://ali.4yewu.cn:8080/delete/?proxy={}".format(proxy))


def made_png(user_id):
    print("start {}".format(user_id))
    while True:
        proxy = get_proxy()
        proxy1 = proxy.decode().split(":")
        try:
            browser.command_executor._commands['executePhantomScript'] = (
                'POST', '/session/$sessionId/phantom/execute')
            browser.execute('executePhantomScript',
                            {'script': '''phantom.setProxy({},{},{});'''.format(proxy1[0], proxy1[1],
                                                                                "http"),
                             'args': []})
            browser.get('https://m.weibo.com/u/{}'.format(user_id))
            browser.implicitly_wait(10)
            elements = browser.find_elements_by_xpath('//div[@class="weibo-text"]')
            break
        except Exception as err:
            delete_proxy(proxy)
            continue
    # browser.save_screenshot(str(int(time.time())) + ".png")
    texts = list()
    for i in elements:
        texts.append(i.text)
    print("获得最近{}条记录".format(len(texts)))
    for text in texts:
        c = r.hget(user_id, text)
        if c is None:
            print("{} 有更新".format(user_id))
            file_name = "{}_{}.png".format(str(user_id), str(int(time.time())))
            time.sleep(3)
            browser.save_screenshot(file_name)
            print("截图完毕")
            r.delete(user_id)
            for a in texts:
                r.hset(user_id, a, "True")
            break
    print("{}扫描完成".format(user_id))


def server():
    # ubuntu 中文乱码问题
    # https://blog.csdn.net/sinat_21302587/article/details/53585527
    # sudo apt-get install xfonts-wqy
    while True:
        try:
            made_png("2036565412")
            made_png("1421647581")
            made_png("1810507404")
            send_email()
            print("一次扫描完成")
            time.sleep(30)
        except Exception as err:
            print("Exception {}".format(err))
            pass


if __name__ == '__main__':
    server()
