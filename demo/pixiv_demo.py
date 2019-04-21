#!/usr/bin/python3
# encoding: utf-8
# @author  : zza
# @Email   : 740713651@qq.com
# @Time    : 2018/8/23 0023
from pixivpy3 import *
from tqdm import tqdm

email = "740713651@qq.com"
passwd = '123456'
proxies = {"http": 'http://localhost:9999',
           "https": 'https://localhost:9999'}
api = PixivAPI(proxies=proxies)
api.login(email, passwd)

# 关注的新作品[New -> Follow] PAPI.me_following_works
json_result = api.me_following_works()
print(json_result)

path = r'E:\PycharmProjects\crawler_set\test'


def get_item(illust_id):
    print(illust_id)
    json_result = api.works(illust_id)
    metadata = json_result['response'][0]['metadata']
    if metadata is None:
        api.download(json_result['response'][0].image_urls['large'], path=path)
        print("-" * 10)
        return
    for page in tqdm(metadata['pages']):
        api.download(page.image_urls['large'], path=path)
    print("-" * 10)
    return


for illust in json_result.response:
    get_item(illust_id=illust['id'])

# illust = json_result.response[0]
# print(">>> %s, origin url: %s" % (illust.caption, illust.image_urls['large']))
