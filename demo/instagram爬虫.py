#!/usr/bin/python3
# encoding: utf-8 
# @Time    : 2018/9/25 15:43 
# @author  : zza
# @Email   : 740713651@qq.com
import json
import re
from pprint import pprint

import requests

# 登录后获得session   可以考虑Selenium获取
sessionid = "7668380119%3AzmIi4K8nHVF392%3A2"
# 代理设置
proxies = {"http": 'http://localhost:9999',
           "https": 'https://localhost:9999'}

header = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.84 Safari/537.36",
    "referer": "https://www.instagram.com/instagram/",
    "x-requested-with": "XMLHttpRequest",
    "cookie": "sessionid={};".format(sessionid),
    "accept": "g*/*",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "gzh-CN,zh;q=0.9",
}


def get_items_info(items):
    """从列表中获取需求数据"""
    for item in items:
        item = item['node']
        # 用得pprint  好看点
        pprint({"img_url": item['display_url'],
                "comment_count": item['edge_media_to_comment']['count'],
                "like_count": item['edge_media_preview_like']['count'],
                "text": item['edge_media_to_caption']['edges'][0]['node']['text']
                })
        print("*" * 50)
    pass


def main():
    # 第一页
    url = "https://www.instagram.com/instagram/"
    req1 = requests.get(url, headers=header, proxies=proxies)
    res = re.findall('<script type="text/javascript">window._sharedData = (.*);</script>', req1.text)
    res = json.loads(res[0])['entry_data']['ProfilePage'][0]['graphql']['user']["edge_owner_to_timeline_media"]
    get_items_info(res["edges"])

    # 其他页
    variables = {"id": "25025320", "first": 12,
                 "after": res["page_info"]['end_cursor']}
    url = "https://www.instagram.com/graphql/query/"
    while True:
        params = {
            'query_hash': 'a5164aed103f24b03e7b7747a2d94e3c',
            'variables': json.dumps(variables),
        }
        req1 = requests.get(url, params=params, headers=header, proxies=proxies)
        if req1.status_code != 200:
            print(req1.status_code)
            raise Exception("返回码不为200了")
        text = json.loads(req1.text)["data"]["user"]["edge_owner_to_timeline_media"]
        get_items_info(text["edges"])
        variables['after'] = text["page_info"]['end_cursor']
        print("下一页id：", text["page_info"]['end_cursor'])
    pass


if __name__ == '__main__':
    main()
