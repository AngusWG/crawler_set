#!/usr/bin/python3
# encoding: utf-8
# @Time    : 2019/7/1 21:58
# @author  : zza
# @Email   : 740713651@qq.com
# @File    : ip_crawler.py
import json
import logging
import os
import re

import pandas
import yaml
from flask import Flask, current_app
import requests
from flask.json import jsonify
from lxml import etree
import time

from retrying import retry
from selenium import webdriver
from selenium.webdriver import DesiredCapabilities

app = Flask(__name__)

# 读取配置
with open("../config.yaml", "rt", encoding="utf8") as f:
    print("use {} config.yaml".format(os.path.abspath("..")))
    conf = yaml.safe_load(f)

app.config.update(conf)
logging.basicConfig(format=app.config.get("log_format"), datefmt='%Y%m%d %I:%M:%S')
logger = logging.getLogger('werkzeug')
logger.setLevel(app.config.get("LOG_LEVEL", "INFO"))

dcap = dict(DesiredCapabilities.PHANTOMJS)
driver = webdriver.PhantomJS(executable_path=app.config["phantomjs_path"],
                             desired_capabilities=dcap)


@app.route("/domain/<string:domain>")
def domain(domain):
    ip_list = get_domain_ip_list(domain)
    data_list = []
    for ip in ip_list[:10]:
        data = get_dns_info(ip)
        data_list += data
    save_file(domain, data_list)
    return jsonify(data_list)


def get_domain_ip_list(domain=".pk1352.com"):
    driver.get("https://dns.bufferover.run/dns?q={}".format(domain))
    time.sleep(5)
    data = re.findall(r"\d+\.\d+\.\d+\.\d+", driver.page_source)
    return data


@app.route("/ip/<string:ip>")
def get_ip_info(ip="159.138.3.64"):
    try:
        res_list = get_dns_info(ip)
        save_file(ip, res_list)
        res = {"code": 0, "msg": "ok", "data": res_list}
    except requests.exceptions.ProxyError:
        res = {"code": -1, "msg": "代理失效", "data": []}
    return jsonify(res)


def save_file(file_name, res_list):
    file_path = os.path.join(app.config.get("csv_path", '.'), file_name + ".csv")
    pandas.DataFrame(res_list).to_csv(file_path, index=False)
    logger.info("[{}]文件已保存至:{}".format(file_name, file_path))


def get_proxy():
    t = current_app.config.get("time", 1)
    now = time.time()
    if now - t <= 1:
        return current_app.proxies
    url = "http://api3.xiguadaili.com/ip/?tid={}&num=1&protocol=https&sortby=time&filter=on"
    rep = requests.get(url.format(current_app.config.get("proxy_uid")))
    data = rep.text
    logger.debug("获取代理: {}".format(data))
    current_app.proxies = proxies = {"https": data}
    current_app.now = now
    return proxies


def wait_func(retry_times, *args, **kwargs):
    logger.info("代理失效，正在第{}次尝试".format(retry_times))
    return 1


@retry(wait_func=wait_func, stop_max_attempt_number=app.config.get("stop_max_attempt_number", 5))
def get_dns_info(ip="118.193.141.207"):
    logger.info("[{}] 查询securitytrails: ".format(ip))
    rep_sec = requests.get("https://securitytrails.com/list/ip/{}".format(ip), proxies=get_proxy())
    domain_list = etree.HTML(rep_sec.text).xpath('//td/a/text()')
    res_list = []
    for domain in domain_list:
        res = get_domain_info(domain)
        res["ip"] = ip
        res_list.append(res)
    logger.info("[{}] 数据:{} ".format(ip, res_list))
    return res_list


def get_domain_info(domain):
    try:
        rep_domain = requests.get("http://{}".format(domain), timeout=app.config.get("timeout", 2), proxies=get_proxy())
    except:
        res = {"code": 408, "msg": "timeout", "title": None, "domain": domain}
    else:
        title = " ".join(etree.HTML(rep_domain.text).xpath('//head/title/text()')).strip()
        res = {"code": rep_domain.status_code, "msg": "ok", "title": title, "domain": domain}
    res["filing_info"] = get_filing_info(domain)
    return res


def get_filing_info(domain='4yewu.cn'):
    params = (('key', current_app.config["filing_key"]),
              ('domainName', domain),)
    response = requests.get('http://apidata.chinaz.com/CallAPI/Domain', params=params,
                            headers={'Accept-Encoding': 'gzip,deflate'})
    res = response.json()
    if res.get("Result") is None:
        res = res['Result']
    else:
        res = res.get('Reason', "查询备案信息网站(apidata.chinaz.com)错误")
    return res


if __name__ == '__main__':
    app.run()
