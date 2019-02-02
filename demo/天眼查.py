#!/usr/bin/python3
# encoding: utf-8 
# @Time    : 2018/12/4 17:40
# @author  : zza
# @Email   : 740713651@qq.com
# from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
# from selenium import webdriver
#
# dcap = dict(DesiredCapabilities.PHANTOMJS)
# dcap["phantomjs.page.settings.userAgent"] = "Mozilla/5.0 (Windows NT 10.0; WOW64) " \
#                                             "AppleWebKit/537.36 (KHTML, like Gecko) " \
#                                             "Chrome/63.0.3239.26 Safari/537.36 Core/" \
#                                             "1.63.6716.400 QQBrowser/10.2.2214.40"
# dcap["phantomjs.page.settings.loadImages"] = True
# service_args = [
#     '--ignore-ssl-errors=true',
#     # '--proxy=119.41.168.186:53281', '--proxy-type=https',
#     '--ssl-protocol=TLSv1'
# ]
# browser = webdriver.PhantomJS(service_args=service_args, desired_capabilities=dcap)
# browser.get("https://www.tianyancha.com/company/3074213933")
# a = browser.find_element_by_xpath('//*[@id="_container_baseInfo"]/table[1]/tbody/tr[1]/td[2]/div[2]')
# print(a.get_attribute("title"))


import requests
import re
import urllib3
import urllib.parse
import json


class Baidu:
    """A generic spider for Baidu;
    For reuse of the socket in order to speed the query,
    it should be instantiated before use"""

    def __init__(self):
        self.conpool = urllib3.PoolManager()
        self.CLEAN_MARK_RULE = re.compile(r'\<\/?em\>')
        self.REGEX = re.compile(
            r'\}"\n        href = "(.+?)".{0,70}?\>(.+?)\<\/a\>.{0,1000}?\<div .{0,20}?abstract.*?\>(?:\<span .{0,50}?\>.{0,100}?\<\/span\>){0,3}(.+?)\<\/div\>',
            re.S)
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.79 Safari/537.36 Edge/14.14393',
            'Host': 'http://www.baidu.com'}

    def query(self, word, debug=False):
        url = r'http://www.baidu.com/s?wd='
        words = urllib.parse.quote(word)
        response = self.conpool.request('GET', url + words)
        result = self.REGEX.findall(response.data.decode())  # result-format: [(url, title, abstracts)]
        if debug:
            with open('html_baidu_query.html', 'w', encoding='utf-8') as f:
                f.write(response.data.decode('utf-8'))
        result_clean = []
        for item in result:
            item = list(item)
            for i in range(3):
                if i:  # urls (i==0) do not need to be cleaned
                    item[i] = self.CLEAN_MARK_RULE.sub('', item[i])
                    item[i] = item[i].replace(r'&quot;', '"')
                    item[i] = item[i].replace(r'&nbsp;', ' ')
                    item[i] = item[i].replace(r'&lt;', '<')
                    item[i] = item[i].replace(r'&gt;', '>')
                    item[i] = item[i].replace(r'&amp;', '&')
            result_clean.append(item)
        del result
        return result_clean


class TYC:
    """A class for Tianyancha.
    1. Get company id from query suggestions;
    2. Get detail info by company id"""

    def __init__(self):
        self.conpool = urllib3.PoolManager()

    def _get_baseinfo(self, com_name):
        name = urllib.parse.quote(com_name)
        url = r'http://www.tianyancha.com/v2/suggest/' + name + r'.json'
        response = self.conpool.request('GET', url)
        data = json.loads(response.data.decode('utf-8'))
        return data['data']

    def get_id(self, com_name):
        return str(self._get_baseinfo(com_name)[0]['id'])

    def get_name(self, com_name):
        return str(self._get_baseinfo(com_name)[0]['name'])

    def get_holders(self, com_name):
        com_id = self.get_id(com_name)
        url = r'http://www.tianyancha.com/expanse/holder.json?id=' + com_id + r'&ps=20&pn=1'
        response = self.conpool.request('GET', url)
        data = json.loads(response.data.decode('utf-8'))
        holderdata = data['data']['result']
        result = [(x['name'], x['amount']) for x in holderdata]
        return result

    def get_patent(self, com_name):
        com_id = self.get_id(com_name)
        url = r'http://www.tianyancha.com/expanse/patent.json?id=' + com_id + r'&pn=1&ps=5'
        response = self.conpool.request('GET', url)
        data = json.loads(response.data.decode('utf-8'))
        try:
            patentdata = data['data']['items']
        except TypeError:  # no patent info
            patentdata = None
        return patentdata

    def _get_invested(self, com_name):  # raw function need accurate company name
        url = r'http://www.tianyancha.com/expanse/findHistoryRongzi.json?name=' + urllib.parse.quote(
            com_name) + r'&ps=10&pn=1'
        response = self.conpool.request('GET', url)
        data = json.loads(response.data.decode('utf-8'))['data']['page']['rows']
        return data

    def _get_cominfo(self, com_name):  # still not valid function
        url = r'http://www.tianyancha.com/v2/company/' + self.get_id(com_name) + r'.json'
        res = self.conpool.request('GET', url)
        data = json.loads(res.data.decode('utf-8'))['data']
        return data

    def get_invested(self, com_name):
        return self._get_invested(self.get_name(com_name))


class QCC:
    """This is a class for Qichacha.
    It should log in for access to details, but getting accurate company names is free and useful. """

    QUERY_URL = r'http://www.qichacha.com/search'
    # Regex pattern for info extraction from html
    QUERY_RULE = re.compile(
        r'\<tr\> \<td\> \<img src="(?:.*?)"\> \<\/td\> \<td\> \<a.*?\>(.+?)\<\/a\>\<br\/\>\n企业法人：(.+?)(?:[\n,.]*?)联系方式：(.+?)(?:[\n,.]*?)\<')
    # Regex pattern for clean xml mark from results
    CLEAN_XML_MARK_RULE = re.compile(r'\<.+?\>')
    COOKIES = {
        'UM_distinctid': '15b94bd28c0532-06440fce5b87b3-3e64430f-15f900-15b94bd28c14d7',
        'gr_user_id': '2564fa5c-2962-4165-a15b-aacf48f7ffd7',
        '_uab_collina': '149284914580079253543107',
        'acw_tc': 'AQAAAOnY9RXMkAEAsLgiOgm41tWhL1Go',
        '_umdata': '70CF403AFFD707DF01F447BEB8F98B0A64DE1388E1FB72C22705EF3B0690146152B13D1F2132E739CD43AD3E795C914C0C36F949192B7ECFBD84BF01696FBF96',
        'PHPSESSID': '996me3inl5ipjqc8f5iq4glva2',
        'gr_session_id_9c1eb7420511f8b2': '01968266-5b16-4ae1-8344-c843b6f84132',
        'CNZZDATA1254842228': '2025307065-1492848434-%7C1493263211',
    }
    HEADER = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
        'host': "www.qichacha.com",
    }

    @classmethod
    def query(cls, querywords):
        """ For that I need most similar company name to my query word, we just get the first page (5 results)"""
        r = requests.get(cls.QUERY_URL, headers=cls.HEADER, cookies=cls.COOKIES, params={'key': querywords})
        result = cls.QUERY_RULE.findall(r.text)
        # print(r.text)
        return [[cls.CLEAN_XML_MARK_RULE.sub('', name) for name in _] for _ in result]


if __name__ == '__main__':
    test = TYC()
    print(test.get_invested('湖南天河国云科技有限公司'))
    # print(QCC.query('腾讯'))